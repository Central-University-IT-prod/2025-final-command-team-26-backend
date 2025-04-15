from .. import app_auth
from films_backend.schemas.queries import FilmsFilters, FilmsSearch
from films_backend.schemas.films import FilmEdit, FilmIn, Film, ViewStatusIn
from films_backend.schemas.genres import Genre
from films_backend.schemas.tmdb import SearchMovie
from films_backend.db.models import Films, Users, UsersFilms, Genres
from films_backend.utils.serializers import serialize_film
from films_backend.api import tmdb
from tortoise.expressions import Q
from typing import Annotated
from uuid import UUID
from random import sample

from fastapi import APIRouter, Query, HTTPException, Depends

router = APIRouter(prefix='/user/films', tags=['Films'])


@router.post(
    '',
    description='Создание фильма пользователем',
    responses={
        201: {'description': 'Успешное создание фильма'},
        400: {'description': 'Неверный формат полей'},
        401: {'description': 'Неавторизованный пользователь'},
        404: {'description': 'Жанр не найден'},
    },
    status_code=201,
)
async def create_film(
    user: Annotated[Users, Depends(app_auth.user_from_jwt)], data: FilmIn
) -> Film:
    if data.tmdb_id:
        film, _ = await Films.get_or_create(
            tmdb_id=data.tmdb_id,
            defaults=data.model_dump(include={'title', 'year', 'tmdb_id'}),
        )
    else:
        film = await Films.create(**data.model_dump(include={'title', 'year'}))

    user_film = await UsersFilms.create(
        **data.model_dump(exclude={'title', 'year', 'genres', 'tmdb_id'}),
        user=user,
        film=film,
    )
    try:
        genres = [await Genres.get(id=genre_id) for genre_id in data.genres]
    except Exception as e:
        raise HTTPException(status_code=404, detail=f'Genre not found. {e}')

    await film.genres.add(*genres)

    return await serialize_film(user_film)


@router.get(
    '',
    description='Получение фильма пользователем',
    responses={
        200: {'description': 'Успешное получение фильмов'},
        400: {'description': 'Неверный формат полей'},
        401: {'description': 'Неавторизованный пользователь'},
    },
)
async def list_films(
    user: Annotated[Users, Depends(app_auth.user_from_jwt)],
    query: Annotated[FilmsFilters, Query()],
) -> list[Film]:
    base_condition = Q()

    if query.genres:
        base_condition &= Q(film__genres__id__in=query.genres)

    if query.years_from is not None:
        base_condition &= Q(film__year__gte=query.years_from)

    if query.years_to is not None:
        base_condition &= Q(film__year__lte=query.years_to)

    if query.is_viewed is not None:
        base_condition &= Q(is_viewed=query.is_viewed)

    if query.playlist:
        base_condition &= Q(playlists__id=query.playlist)

    if query.name is not None:
        base_condition &= Q(film__title__search=query.name.replace(' ', '_')) | Q(
            film__title__icontains=query.name
        )

    films = (
        await user.users_films.filter(base_condition)
        .order_by('-created_date')
        .offset(query.offset)
        .limit(query.limit)
        .prefetch_related('film')
    )

    films = [await serialize_film(film) for film in films]

    ids = []
    items = []

    for film in films:
        if film.id not in ids:
            ids.append(film.id)
            items.append(film)

    films = items

    if query.recommendate and len(films) > 0:
        return sample(films, min(len(films), 3))

    return films


@router.get(
    '/{film_id}',
    description='Получение по ID',
    responses={
        200: {'description': 'Успешное получение фильма'},
        400: {'description': 'Неверный формат полей'},
        401: {'description': 'Неавторизованный пользователь'},
        404: {'description': 'Фильм не найден'},
    },
)
async def get_film(
    user: Annotated[Users, Depends(app_auth.user_from_jwt)], film_id: UUID
) -> Film:
    film = await UsersFilms.get_or_none(id=film_id, user=user).prefetch_related('film')

    if not film:
        raise HTTPException(status_code=404, detail='Film not found')

    return await serialize_film(film)


@router.patch(
    '/{film_id}',
    description='Корректировка полей фильма',
    responses={
        200: {'description': 'Фильм успешно обновлен'},
        400: {'description': 'Неверный формат полей | Невозвожно изменить фильм'},
        401: {'description': 'Неавторизованный пользователь'},
        404: {'description': 'Фильм не найден'},
    },
)
async def update_film(
    user: Annotated[Users, Depends(app_auth.user_from_jwt)],
    film_id: UUID,
    data: FilmEdit,
) -> Film:
    film = await UsersFilms.get_or_none(id=film_id, user=user).prefetch_related('film')
    if not film:
        raise HTTPException(status_code=404, detail='Film not found')

    try:
        await film.update_from_dict(
            data.model_dump(exclude={'genres', 'title', 'year'}, exclude_unset=True)
        )
        await film.save()

        await film.film.update_from_dict(
            data.model_dump(include={'title', 'year'}, exclude_unset=True)
        )
        await film.film.save()

        if data.genres is not None:
            await film.film.genres.clear()
            genres = [await Genres.get_or_none(id=genre_id) for genre_id in data.genres]
            await film.film.genres.add(*genres)

    except Exception as e:
        raise HTTPException(status_code=400, detail=f'Unable to update film. {e}')

    return await serialize_film(film)


@router.delete(
    '/{film_id}',
    description='Удаление фильма',
    responses={
        204: {'description': 'Фильм успешно удален'},
        401: {'description': 'Неавторизованный пользователь'},
        404: {'description': 'Фильм не найден'},
    },
    status_code=204,
)
async def delete_film(
    user: Annotated[Users, Depends(app_auth.user_from_jwt)], film_id: UUID
) -> None:
    film = await UsersFilms.get_or_none(id=film_id, user=user)
    if not film:
        raise HTTPException(status_code=404, detail='Film not found')

    await film.delete()


@router.post(
    '/{film_id}/view',
    description='Установка статуса просмотра фильма',
    responses={
        200: {'description': 'Статус успешно изменен'},
        400: {'description': 'Неверный формат полей'},
        401: {'description': 'Неавторизованный пользователь'},
        404: {'description': 'Фильм не найден'},
    },
    status_code=200,
)
async def change_view_status(
    user: Annotated[Users, Depends(app_auth.user_from_jwt)],
    film_id: UUID,
    data: ViewStatusIn,
) -> Film:
    film = await UsersFilms.get_or_none(id=film_id, user=user).prefetch_related('film')
    if not film:
        raise HTTPException(status_code=404, detail='Film not found')

    await film.update_from_dict(data.model_dump())
    await film.save()

    return await serialize_film(film)


@router.get(
    '/search/film',
    description='Установка статуса просмотра фильма',
    responses={
        200: {'description': 'Успешное выполнение операции'},
        404: {'description': 'Фильмы не найдены'},
    },
)
async def search(query: Annotated[FilmsSearch, Query()]) -> list[SearchMovie]:
    films = await tmdb.search_movies(query.search)
    if films is None:
        raise HTTPException(status_code=404, detail='No films found.')
    return films


@router.get(
    '/search/get_genres',
    description='Установка статуса просмотра фильма',
    responses={
        200: {'description': 'Успешное выполнение операции'},
        404: {'description': 'Фильм не найден'},
    },
)
async def get_genres(genres: str) -> list[Genre]:
    if genres == '':
        raise HTTPException(status_code=404, detail='Genres not found.')

    genres = list(map(int, genres.split(',')))

    return [
        Genre.model_validate(genre.__dict__)
        for genre_id in genres
        if (genre := await Genres.get_or_none(tmdb_id=genre_id))
    ]
