from films_backend.db.models import UsersFilms, Playlists
from films_backend.schemas.films import Film
from films_backend.schemas.genres import Genre
from films_backend.schemas.playlists import Playlist


async def serialize_film(film: UsersFilms) -> Film:
    genres = list(
        map(
            lambda genre: Genre(id=genre.id, title=genre.title),
            await film.film.genres.all(),
        )
    )

    return Film(
        title=film.film.title,
        year=film.film.year,
        genres=genres,
        note=film.note,
        link=film.link,
        id=film.id,
        is_viewed=film.is_viewed,
        viewed_date=film.view_date,
        tmdb_id=film.film.tmdb_id,
    )


async def serialize_playlist(playlist: Playlists):
    films = [
        await serialize_film(film)
        for film in await playlist.films.all().prefetch_related('film')
    ]
    is_viewed = all([film.is_viewed for film in films])

    return Playlist(
        id=playlist.id,
        title=playlist.title,
        is_viewed=is_viewed,
        films=films,
    )
