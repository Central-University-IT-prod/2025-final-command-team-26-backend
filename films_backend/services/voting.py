from ..config import app_config
from ..schemas.rooms import (
    Room,
    RoomUser,
    RoomFilm,
    RoomStates,
    RoundStates,
    VoteRound,
    UserVote,
)
from uuid import UUID
from datetime import datetime, timedelta, timezone

import redis.asyncio as redis


class VotingManager:
    def __init__(self, redis_client: redis.Redis):
        self._redis_client = redis_client

    async def create_room(self, title: str, owner: RoomUser) -> Room:
        room = Room(title=title, users=[owner])
        await self._redis_client.set(
            str(room.id),
            room.model_dump_json(),
            exat=datetime.now(timezone.utc) + timedelta(hours=app_config.room_ttl),
        )

        return room

    async def get_room(self, room_id: UUID) -> Room:
        room_data = await self._redis_client.get(str(room_id))
        if not room_data:
            raise KeyError('Room not found')

        return Room.model_validate_json(room_data)

    async def change_room_state(self, room_id: UUID, state: RoomStates) -> Room:
        room = await self.get_room(room_id)

        room.state = state
        await self._redis_client.set(
            str(room.id),
            room.model_dump_json(),
            exat=datetime.now(timezone.utc) + timedelta(hours=app_config.room_ttl),
        )

        return room

    async def delete_room(self, room_id: UUID) -> None:
        await self._redis_client.delete(str(room_id))

    async def add_user(self, room_id: UUID, user: RoomUser) -> Room:
        room = await self.get_room(room_id)
        if user in room.users:
            raise KeyError('User already exists')

        room.users.append(user)
        await self._redis_client.set(
            str(room.id),
            room.model_dump_json(),
            exat=datetime.now(timezone.utc) + timedelta(hours=app_config.room_ttl),
        )

        return room

    async def get_user(self, room_id: UUID, user_id: UUID) -> RoomUser:
        room = await self.get_room(room_id)

        filtered_users = list(filter(lambda user: user.id == user_id, room.users))
        if not filtered_users:
            raise KeyError('User not found')

        return filtered_users[0]

    async def remove_user(self, room_id: UUID, user_id: UUID) -> Room:
        room = await self.get_room(room_id)
        user = await self.get_user(room_id, user_id)

        room.users.remove(user)
        await self._redis_client.set(
            str(room.id),
            room.model_dump_json(),
            exat=datetime.now(timezone.utc) + timedelta(hours=app_config.room_ttl),
        )

        return room

    async def add_film(self, room_id: UUID, film: RoomFilm) -> Room:
        room = await self.get_room(room_id)
        user_films = list(
            filter(lambda room_film: room_film.user_id == film.user_id, room.films)
        )
        if len(user_films) > 0:
            raise KeyError('User can add only one film')

        room.films.append(film)
        await self._redis_client.set(
            str(room.id),
            room.model_dump_json(),
            exat=datetime.now(timezone.utc) + timedelta(hours=app_config.room_ttl),
        )

        return room

    async def get_film(self, room_id: UUID, film_id: UUID) -> RoomFilm:
        room = await self.get_room(room_id)
        films = list(filter(lambda film: film.id == film_id, room.films))
        if not films:
            raise KeyError('Film not found')

        return films[0]

    async def edit_film(self, room_id: UUID, film: RoomFilm) -> Room:
        room = await self.get_room(room_id)
        room_film = await self.get_film(room_id, film.id)
        if film.user_id != room_film.user_id:
            raise PermissionError('You can only edit your films')

        room.films[room.films.index(room_film)] = film
        await self._redis_client.set(
            str(room.id),
            room.model_dump_json(),
            exat=datetime.now(timezone.utc) + timedelta(hours=app_config.room_ttl),
        )

        return room

    async def remove_film(
        self, room_id: UUID, film_id: UUID, user_id: UUID | None = None
    ) -> Room:
        room = await self.get_room(room_id)
        film = await self.get_film(room_id, film_id)

        if user_id is not None and film.user_id != user_id:
            raise PermissionError('You can only remove your films')

        room.films.remove(film)
        await self._redis_client.set(
            str(room.id),
            room.model_dump_json(),
            exat=datetime.now(timezone.utc) + timedelta(hours=app_config.room_ttl),
        )

        return room

    async def create_round(self, room_id: UUID) -> Room:
        room = await self.get_room(room_id)

        room.rounds.append(VoteRound())
        await self._redis_client.set(
            str(room.id),
            room.model_dump_json(),
            exat=datetime.now(timezone.utc) + timedelta(hours=app_config.room_ttl),
        )

        return room

    async def accept_vote(self, room_id: UUID, vote: UserVote) -> Room:
        room = await self.get_room(room_id)
        await self.get_user(room_id, vote.user_id)

        if room.state != RoomStates.VOTING:
            raise PermissionError('You can vote only on voting')

        user_votes = list(
            filter(
                lambda user_vote: user_vote.user_id == vote.user_id,
                room.rounds[-1].votes,
            )
        )
        if user_votes:
            room.rounds[-1].votes.remove(user_votes[0])

        room.rounds[-1].votes.append(vote)
        await self._redis_client.set(
            str(room.id),
            room.model_dump_json(),
            exat=datetime.now(timezone.utc) + timedelta(hours=app_config.room_ttl),
        )

        return room

    async def change_round_state(
        self, room_id: UUID, state: RoundStates, round_id: int = -1
    ) -> Room:
        room = await self.get_room(room_id)
        if round_id >= 0 and round_id > len(room.rounds) - 1:
            raise KeyError('Round not found')

        room.rounds[round_id].state = state
        await self._redis_client.set(
            str(room.id),
            room.model_dump_json(),
            exat=datetime.now(timezone.utc) + timedelta(hours=app_config.room_ttl),
        )

        return room
