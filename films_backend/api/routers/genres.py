from films_backend.schemas.genres import Genre
from films_backend.db.models import Genres

from fastapi import APIRouter

router = APIRouter(prefix='/genres', tags=['Genres'])


@router.get(
    '',
    description='Получение списка жанров',
    responses={
        200: {'description': 'Успешное выполнение операции'},
    },
)
async def get_genres() -> list[Genre]:
    genres = await Genres.all()
    return list(
        map(lambda genre: Genre.model_validate(genre, from_attributes=True), genres)
    )
