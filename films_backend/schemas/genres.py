from uuid import UUID

from pydantic import BaseModel, Field


class Genre(BaseModel):
    id: UUID | None = Field(default=None)
    tmdb_id: int | None = Field(default=None)
    title: str | None = Field(default=None)
