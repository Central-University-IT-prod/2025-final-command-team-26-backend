from films_backend.schemas.genres import Genre
from datetime import date
from uuid import UUID

from pydantic import BaseModel, Field


class FilmEdit(BaseModel):
    title: str | None = Field(default=None, min_length=1)
    year: int | None = Field(default=None, gt=0)
    genres: list[UUID] | None = Field(default=None)
    note: str | None = Field(default=None, min_length=0)
    link: str | None = Field(default=None, min_length=8, pattern=r'^http(s?):\/{2}')


class FilmIn(FilmEdit):
    title: str = Field(min_length=1)
    tmdb_id: int | None = None


class Film(FilmIn):
    id: UUID
    genres: list[Genre] | None = None
    is_viewed: bool = False
    viewed_date: date | None = None


class ViewStatusIn(BaseModel):
    is_viewed: bool


class MediaFromSeqrch(BaseModel):
    media_type: str
    title: str
    tmdb_id: int
