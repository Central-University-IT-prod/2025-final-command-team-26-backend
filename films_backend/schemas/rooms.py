from enum import IntEnum, Enum
from typing import Any, Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class WSActions(str, Enum):
    LOGIN = 'login'
    GET_ROOM = 'get_room'
    REMOVE_USER = 'remove_user'
    ADD_FILM = 'add_film'
    REMOVE_FILM = 'remove_film'
    UPDATE_FILM = 'update_film'
    START_VOTE = 'start_vote'
    VOTE = 'vote'


class RoomStates(IntEnum):
    PREPARATION = 0
    VOTING = 1
    WAITING = 2
    END = 3


class RoundStates(IntEnum):
    ACTIVE = 0
    END = 1


class RoomWSIn(BaseModel):
    user_id: UUID | None = None
    action: WSActions
    payload: dict[str, Any] = {}


class RoomWSOut(BaseModel):
    status: Literal['ok', 'error'] = 'ok'
    type: Literal['room', 'user', 'round_results'] = 'room'
    error_message: str | None = None
    payload: Any = None


class UserVote(BaseModel):
    user_id: UUID
    film_id: UUID


class VoteRound(BaseModel):
    state: RoundStates = RoundStates.ACTIVE
    votes: list[UserVote] = []


class RoomUser(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    login: str


class RoomFilm(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    user_id: UUID
    title: str


class RoomIn(BaseModel):
    owner_login: str | None = None
    title: str


class FilmVoteResults(BaseModel):
    title: str
    votes_count: int


class RoundResults(BaseModel):
    votes_count: dict[UUID, FilmVoteResults]
    choice: RoomFilm | None = None


class Room(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    title: str
    state: RoomStates = RoomStates.PREPARATION
    users: list[RoomUser] = []
    films: list[RoomFilm] = []

    rounds: list[VoteRound] = []
