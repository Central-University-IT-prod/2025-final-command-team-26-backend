from contextlib import asynccontextmanager
from films_backend.db import init_db
from films_backend.config import app_config
from films_backend.api import tmdb
from films_backend.db.models import Genres

from fastapi import FastAPI


async def add_genres():
    genres_films = await tmdb.get_ids(media_type='movie')
    genres_tv = await tmdb.get_ids(media_type='tv')
    genres_films = {(genre.id, genre.name) for genre in genres_films}
    genres_tv = {(genre.id, genre.name) for genre in genres_tv}

    all_ = genres_films | genres_tv

    for id, genre in all_:
        await Genres.get_or_create(tmdb_id=id, defaults={'title': genre.capitalize()})


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db(
        username=app_config.postgres_user,
        password=app_config.postgres_password,
        db_name=app_config.postgres_db,
        host=app_config.postgres_host,
    )

    await add_genres()

    yield
