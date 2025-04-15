from .films import Film
from uuid import UUID

from pydantic import BaseModel, Field


class PlaylistEdit(BaseModel):
    title: str = Field(min_length=1, max_length=255)


class PlaylistIn(PlaylistEdit):
    films: list[UUID]


class Playlist(PlaylistIn):
    id: UUID
    films: list[Film]
    is_viewed: bool
