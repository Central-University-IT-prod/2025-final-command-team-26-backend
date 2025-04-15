from httpx import AsyncClient
from fastapi import HTTPException

from films_backend.config import app_config


class OAuth(AsyncClient):
    """
    Запросы к Yandex
    """

    def __init__(self) -> None:
        super().__init__()

        self.CLIENT_ID = app_config.client_id
        self.CLIENT_SECRET = app_config.client_secret

    async def get_data(self, token: str) -> str | None:
        response = await self.get(
            url='https://login.yandex.ru/info',
            headers={'Authorization': f'OAuth {token}'},
        )
        response = response.json()
        if not response.get('psuid'):
            return HTTPException(
                status_code=404,
                detail='User not found',
            )

        return response

    async def get_user_token(self, code: str) -> str | None:
        response = await self.post(
            url='https://oauth.yandex.ru/token',
            data={
                'grant_type': 'authorization_code',
                'code': code,
                'client_id': self.CLIENT_ID,
                'client_secret': self.CLIENT_SECRET,
            },
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
        )
        print(response.status_code)
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail=response.text)

        token_data = response.json()
        access_token = token_data.get('access_token')

        return access_token
