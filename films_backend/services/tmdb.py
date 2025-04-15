from httpx import AsyncClient, ReadTimeout
from typing import List
from fastapi import HTTPException

from films_backend.config import app_config

from films_backend.schemas.tmdb import Genre, SearchMovie


class GetTMDBData(AsyncClient):
    """
    Запросы к TMDB
    """

    def __init__(self, proxy: str) -> None:
        super().__init__(
            base_url='https://api.themoviedb.org/3',
            proxy=proxy,
        )

        self.tokens = [
            app_config.api_key_1,
            app_config.api_key_2,
        ]

    async def search_movies(
        self, query: str, page: int = 1
    ) -> list[SearchMovie] | None:
        """
        Поиск фильмов

        :param query: название фильма
        :param page: страница
        """
        for try_ in range(0, len(self.tokens)):
            try:
                response = await self.get(
                    url='/search/movie',
                    params={'query': query, 'language': 'ru-RU', 'page': 1},
                    headers={'Authorization': f'Bearer {self.tokens[try_]}'},
                )
                if response.status_code != 200:
                    if try_ == 2:
                        raise HTTPException(status_code=500, detail='TMDB error')
                    else:
                        print(f'Try: {try_}')
                        continue

                data = response.json()['results']
                if len(data) == 0:
                    return None
                data: List[SearchMovie] = [SearchMovie(**item) for item in data]
                return data

            except ReadTimeout:
                if try_ == 2:
                    raise HTTPException(status_code=500, detail='TMDB error')
                else:
                    print(f'Try: {try_}')
                    continue

    async def search_tv_shows(
        self, query: str, page: int = 1
    ) -> list[SearchMovie] | None:
        """
        Поиск TV шоу

        :param query: название фильма
        :param page: страница
        """
        for try_ in range(0, len(self.tokens)):
            try:
                response = await self.get(
                    url='/search/movie',
                    params={'query': query, 'language': 'ru-RU', 'page': 1},
                    headers={'Authorization': f'Bearer {self.tokens[try_]}'},
                )

                if response.status_code != 200:
                    if try_ == 2:
                        raise HTTPException(status_code=500, detail='TMDB error')
                    else:
                        continue

                data = response.json()['results']
                if len(data) == 0:
                    return None
                data: List[SearchMovie] = [SearchMovie(**item) for item in data]
                return data

            except ReadTimeout:
                if try_ == 2:
                    raise HTTPException(status_code=500, detail='TMDB error')
                else:
                    print(f'Try: {try_}')
                    continue

    async def get_ids(self, media_type: str) -> list[Genre] | None:
        """
        Получение списка значений ID жанров

        :param media_type:  tv/movie
        """
        for try_ in range(0, len(self.tokens)):
            try:
                response = await self.get(
                    url=f'/genre/{media_type.lower()}/list',
                    params={'language': 'ru'},
                    headers={'Authorization': f'Bearer {self.tokens[try_]}'},
                )

                if response.status_code != 200:
                    if try_ == 2:
                        raise HTTPException(status_code=500, detail='TMDB error')
                    else:
                        print(f'Try: {try_}')
                        continue

                data = response.json()['genres']
                if len(data) == 0:
                    return None
                data: List[Genre] = [Genre(**item) for item in data]
                return data

            except ReadTimeout:
                if try_ == 4:
                    raise HTTPException(status_code=500, detail='TMDB error')
                else:
                    print(f'Try: {try_}')
                    continue

    async def get_film_keywords(self, movie_id: int) -> list[str] | None:
        """
        Получение ключевых слов фильма

        :param movie_id: ID фильма
        """
        for try_ in range(0, len(self.tokens)):
            try:
                response = await self.get(url=f'/movie/{movie_id}/keywords')
                data: dict = response.json()['keywords']
                if len(data) == 0:
                    return None
                data = [list(item.values())[1] for item in data]
                return data

            except ReadTimeout:
                if try_ == 4:
                    raise HTTPException(status_code=500, detail='TMDB error')
                else:
                    print(f'Try: {try_}')
                    continue
