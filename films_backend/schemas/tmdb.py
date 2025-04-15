from pydantic import BaseModel, Field


class SearchMovie(BaseModel):
    adult: bool | None = Field(default=None)
    backdrop_path: str | None = Field(default=None)
    genre_ids: list[int] | None = Field(default=None)
    id: int | None = Field(default=None)
    original_language: str | None = Field(default=None)
    original_title: str | None = Field(default=None)
    overview: str | None = Field(default=None)
    popularity: float | None = Field(default=None)
    poster_path: str | None = Field(default=None)
    release_date: str | None = Field(default=None)
    title: str | None = Field(default=None)
    video: bool | None = Field(default=None)
    vote_average: float | None = Field(default=None)
    vote_count: int | None = Field(default=None)


class Genre(BaseModel):
    id: int
    name: str
