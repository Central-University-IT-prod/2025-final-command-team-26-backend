from uuid import UUID
from typing_extensions import Self
from enum import Enum


from pydantic import BaseModel, Field, model_validator


class PaginationQuery(BaseModel):
    offset: int = Field(0, ge=0)
    limit: int = Field(10, ge=0)


class FilmsFilters(PaginationQuery):
    genres: list[UUID] | None = Field(default=None)
    years_from: int | None = Field(default=None, gt=0)
    years_to: int | None = Field(default=None, lt=9999)
    is_viewed: bool | None = Field(default=None)
    playlist: UUID | None = Field(default=None)
    recommendate: bool | None = Field(default=None)
    name: str | None = Field(default=None)

    @model_validator(mode='after')
    def check_years(self) -> Self:
        if self.years_from is not None and self.years_to is not None:
            if self.years_to < self.years_from:
                raise ValueError('years_to cannot be less than years_from')

        return self


class MediaType(str, Enum):
    movie = 'movie'
    tv = 'tv'


class FilmsSearch(PaginationQuery):
    search: str | None = Field()
    page: int | None = Field(default=1, ge=1)
