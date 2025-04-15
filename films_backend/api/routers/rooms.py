import asyncio
import random
from collections import Counter

from .. import app_auth, connection_manager, vote_manager
from films_backend.db.models import Users
from films_backend.schemas.rooms import (
    Room,
    RoomIn,
    RoomWSIn,
    RoomWSOut,
    WSActions,
    RoomUser,
    RoomFilm,
    RoomStates,
    UserVote,
    RoundStates,
    RoundResults,
    FilmVoteResults,
)
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect

from ...config import app_config

router = APIRouter(prefix='/rooms', tags=['Rooms'])


@router.post('')
async def create_room(
    user: Annotated[Users | None, Depends(app_auth.user_from_jwt_nullable)],
    data: RoomIn,
) -> Room:
    user_login = user.login if user else data.owner_login
    if not user_login:
        raise HTTPException(
            status_code=403, detail='You must be logged in or provide owner login'
        )
    return await vote_manager.create_room(
        title=data.title, owner=RoomUser(login=user_login)
    )


@router.websocket('/ws/{room_id}')
async def room_websocket(websocket: WebSocket, room_id: UUID):
    try:
        await connection_manager.connect(websocket, room_id)
        await receive_ws(websocket, room_id)
    except WebSocketDisconnect:
        user_id = connection_manager.disconnect(websocket, room_id)
        await vote_manager.remove_user(room_id, user_id)


async def receive_ws(websocket: WebSocket, room_id: UUID):
    async for data in websocket.iter_json():
        try:
            data_in = RoomWSIn.model_validate(data)
            match data_in.action:
                case WSActions.GET_ROOM:
                    room = await vote_manager.get_room(room_id)

                    await connection_manager.send_personal_data(
                        websocket, room_id, RoomWSOut(payload=room).model_dump(mode='json')
                    )
                case WSActions.LOGIN:
                    payload = RoomUser.model_validate(data_in.payload)

                    await connection_manager.connect(websocket, room_id, payload.id)

                    room = await vote_manager.add_user(room_id, payload)

                    await connection_manager.send_personal_data(
                        websocket,
                        room_id,
                        RoomWSOut(payload=payload, type='user').model_dump(mode='json'),
                    )

                    print(RoomWSOut(payload=room))
                    await connection_manager.broadcast(
                        room_id, RoomWSOut(payload=room).model_dump(mode='json')
                    )
                case WSActions.ADD_FILM:
                    payload = RoomFilm.model_validate(data_in.payload)

                    room = await vote_manager.add_film(room_id, payload)

                    await connection_manager.broadcast(
                        room_id, RoomWSOut(payload=room).model_dump(mode='json')
                    )

                case WSActions.UPDATE_FILM:
                    payload = RoomFilm.model_validate(data_in.payload)

                    room = await vote_manager.edit_film(room_id, payload)

                    await connection_manager.broadcast(
                        room_id, RoomWSOut(payload=room).model_dump(mode='json')
                    )

                case WSActions.REMOVE_FILM:
                    payload = RoomFilm.model_validate(data_in.payload)

                    room = await vote_manager.remove_film(room_id, payload.id)

                    await connection_manager.broadcast(
                        room_id, RoomWSOut(payload=room).model_dump(mode='json')
                    )

                case WSActions.START_VOTE:
                    asyncio.create_task(handle_voting(room_id))
                case WSActions.VOTE:
                    payload = UserVote.model_validate(data_in.payload)

                    room = await vote_manager.accept_vote(room_id, payload)

                    await connection_manager.broadcast(
                        room_id, RoomWSOut(payload=room).model_dump(mode='json')
                    )
        except Exception as e:
            await connection_manager.send_personal_data(websocket, room_id, RoomWSOut(status='error', error_message=str(e)).model_dump(mode='json'))


async def handle_voting(room_id: UUID):
    for i in range(app_config.max_vote_rounds):
        await vote_manager.create_round(room_id)
        room = await vote_manager.change_room_state(room_id, RoomStates.VOTING)
        await connection_manager.broadcast(
            room_id, RoomWSOut(payload=room).model_dump(mode='json')
        )
        await asyncio.sleep(app_config.round_time)

        room = await vote_manager.get_room(room_id)

        votes = dict(Counter([vote.film_id for vote in room.rounds[-1].votes]))
        await connection_manager.broadcast(
            room_id,
            RoomWSOut(
                payload=RoundResults(
                    votes_count={
                        film_id: FilmVoteResults(
                            title=(await vote_manager.get_film(room_id, film_id)).title,
                            votes_count=votes[film_id],
                        )
                        for film_id in votes.keys()
                    }
                ),
                type='round_results',
            ).model_dump(mode='json'),
        )

        res = None
        if len(set(votes.values())) <= 1:  # Voted equally
            film_id = random.choice(list(votes.keys()))
            res = await vote_manager.get_film(room_id, film_id)
        else:
            min_score = min(votes.values())
            worst_film = list(
                filter(lambda f_id: votes[f_id] == min_score, votes.keys())
            )
            for film_id in worst_film:
                await vote_manager.remove_film(room_id, film_id)

        if i == app_config.max_vote_rounds - 1 and res is None:
            film_id = random.choice(list(votes.keys()))
            res = await vote_manager.get_film(room_id, film_id)

        if res:
            await connection_manager.broadcast(
                room_id,
                RoomWSOut(
                    payload=RoundResults(
                        votes_count={
                            film_id: FilmVoteResults(
                                title=(
                                    await vote_manager.get_film(room_id, film_id)
                                ).title,
                                votes_count=votes[film_id],
                            )
                            for film_id in votes.keys()
                        },
                        choice=res,
                    ),
                    type='round_results',
                ).model_dump(mode='json'),
            )
            connections = connection_manager.active_connections[room_id].copy()
            for websocket in connections:
                await connection_manager.disconnect(websocket, room_id)
            await vote_manager.delete_room(room_id)
            break

        await vote_manager.change_round_state(room_id, RoundStates.END)
        room = await vote_manager.change_room_state(room_id, RoomStates.WAITING)

        await connection_manager.broadcast(
            room_id, RoomWSOut(payload=room).model_dump(mode='json')
        )
        await asyncio.sleep(app_config.round_timeout)
