from .. import app_auth
from films_backend.db.models import Users, Playlists, UsersFilms
from films_backend.schemas.playlists import Playlist, PlaylistIn, PlaylistEdit
from films_backend.utils.serializers import serialize_playlist
from films_backend.schemas.queries import PaginationQuery
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Body, Depends, HTTPException, Query

router = APIRouter(prefix='/playlists', tags=['Playlists'])


@router.post(
    '',
    description='Создание плейлиста',
    responses={
        201: {'description': 'Успешное создание плейлиста'},
        400: {'description': 'Неверный формат полей'},
        401: {'description': 'Неавторизованный пользователь'},
        404: {'description': 'Фильм не найден'},
    },
    status_code=201,
)
async def create_playlist(
    user: Annotated[Users, Depends(app_auth.user_from_jwt)], data: PlaylistIn
) -> Playlist:
    playlist = await Playlists.create(title=data.title, user=user)
    try:
        films = [await UsersFilms.get(id=film_id) for film_id in data.films]
    except Exception as e:
        raise HTTPException(status_code=404, detail=f'Film not found. {e}')

    await playlist.films.add(*films)
    return await serialize_playlist(playlist)


@router.get(
    '',
    description='Получение плейлиста',
    responses={
        200: {'description': 'Успешное получение плейлиста'},
        400: {'description': 'Неверный формат полей'},
        401: {'description': 'Неавторизованный пользователь'},
    },
    status_code=200,
)
async def list_playlists(
    user: Annotated[Users, Depends(app_auth.user_from_jwt)],
    query: Annotated[PaginationQuery, Query()],
) -> list[Playlist]:
    playlists = await user.playlists.offset(query.offset).limit(query.limit)

    return [await serialize_playlist(playlist) for playlist in playlists]


@router.get(
    '/{playlist_id}',
    description='Получение плейлиста по ID',
    responses={
        200: {'description': 'Успешное получение плейлиста'},
        400: {'description': 'Неверный формат полей'},
        401: {'description': 'Неавторизованный пользователь'},
        404: {'description': 'Плейлист не найден'},
    },
    status_code=200,
)
async def get_playlist(
    user: Annotated[Users, Depends(app_auth.user_from_jwt)], playlist_id: UUID
) -> Playlist:
    playlist = await Playlists.get_or_none(id=playlist_id)
    if not playlist:
        raise HTTPException(status_code=404, detail='Playlist not found')

    return await serialize_playlist(playlist)


@router.patch(
    '/{playlist_id}',
    description='Корректировка плейлиста по ID',
    responses={
        200: {'description': 'Успешная корректировка плейлиста'},
        400: {'description': 'Неверный формат полей'},
        401: {'description': 'Неавторизованный пользователь'},
        404: {'description': 'Плейлист не найден'},
    },
)
async def update_playlist(
    user: Annotated[Users, Depends(app_auth.user_from_jwt)],
    playlist_id: UUID,
    data: PlaylistEdit,
) -> Playlist:
    playlist = await Playlists.get_or_none(id=playlist_id)
    if not playlist:
        raise HTTPException(status_code=404, detail='Playlist not found')

    playlist.title = data.title
    await playlist.save()

    return await serialize_playlist(playlist)


@router.post(
    '/{playlist_id}/films',
    description='Получение фильмов из плейлиста',
    responses={
        200: {'description': 'Успешное получение фильмов'},
        400: {'description': 'Неверный формат полей'},
        401: {'description': 'Неавторизованный пользователь'},
        404: {'description': 'Плейлист или фильм не найдены'},
    },
)
async def add_film_to_playlist(
    user: Annotated[Users, Depends(app_auth.user_from_jwt)],
    playlist_id: UUID,
    film_id: Annotated[UUID, Body(embed=True)],
) -> Playlist:
    playlist = await Playlists.get_or_none(id=playlist_id)

    if not playlist:
        raise HTTPException(status_code=404, detail='Playlist not found')

    film = await UsersFilms.get_or_none(id=film_id, user=user).prefetch_related('film')
    if not film:
        raise HTTPException(status_code=404, detail='Film not found')

    await playlist.films.add(film)
    return await serialize_playlist(playlist)


@router.delete(
    '/{playlist_id}/films/{film_id}',
    description='Удаление фильма из плейлиста по ID',
    responses={
        204: {'description': 'Успешное удаление'},
        400: {'description': 'Неверный формат полей'},
        401: {'description': 'Неавторизованный пользователь'},
        404: {'description': 'Плейлист или фильм не найдены'},
    },
    status_code=204,
)
async def remove_film_from_playlist(
    user: Annotated[Users, Depends(app_auth.user_from_jwt)],
    playlist_id: UUID,
    film_id: UUID,
) -> None:
    playlist = await Playlists.get_or_none(id=playlist_id)

    if not playlist:
        raise HTTPException(status_code=404, detail='Playlist not found')

    film = await UsersFilms.get_or_none(id=film_id, user=user).prefetch_related('film')
    if not film:
        raise HTTPException(status_code=404, detail='Film not found')

    await playlist.films.remove(film)


@router.delete(
    '/{playlist_id}',
    description='Удаление лейлиста по ID',
    responses={
        204: {'description': 'Успешное удаление'},
        400: {'description': 'Неверный формат полей'},
        401: {'description': 'Неавторизованный пользователь'},
        404: {'description': 'Плейлист не найден'},
    },
    status_code=204,
)
async def delete_playlist(
    user: Annotated[Users, Depends(app_auth.user_from_jwt)], playlist_id: UUID
) -> None:
    playlist = await Playlists.get_or_none(id=playlist_id)
    if not playlist:
        raise HTTPException(status_code=404, detail='Playlist not found')

    await playlist.delete()
