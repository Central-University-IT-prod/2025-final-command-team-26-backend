from ..db.models import Users
from datetime import datetime, timedelta, timezone
from typing import Any, Annotated

import jwt
from passlib.context import CryptContext

from fastapi import HTTPException, Depends
from fastapi.security.http import HTTPBearer, HTTPAuthorizationCredentials

CREDENTIALS_EXCEPTION = HTTPException(
    status_code=401,
    detail='Пользователь не авторизован.',
    headers={'WWW-Authenticate': 'Bearer'},
)

USER_AUTH_SCHEME = HTTPBearer(scheme_name='Users', auto_error=False)


class AppAuth:
    def __init__(
        self,
        secret_key: str,
        scheme: str = 'argon2',
        jwt_algorithm: str = 'HS256',
        jwt_ttl: int = 12,
    ):
        self.__secret_key = secret_key
        self.jwt_algorithm = jwt_algorithm
        self.jwt_ttl = jwt_ttl

        self._context = CryptContext(schemes=[scheme], deprecated='auto')

    @property
    def jwt_expiry(self) -> datetime:
        return datetime.now(tz=timezone.utc) + timedelta(hours=self.jwt_ttl)

    def hash(self, data: str) -> str:
        return self._context.hash(secret=data)

    def verify_hash(self, data: str | bytes, hashed: str | bytes) -> bool:
        return self._context.verify(secret=data, hash=hashed)

    def _encode_jwt(self, payload: dict[str, Any], exp: datetime) -> str:
        payload = payload.copy()
        payload['exp'] = exp

        return jwt.encode(
            payload=payload, key=self.__secret_key, algorithm=self.jwt_algorithm
        )

    def _decode_jwt(self, jwt_token: str) -> dict[str, Any]:
        try:
            return jwt.decode(
                jwt=jwt_token.encode('utf-8'),
                key=self.__secret_key,
                algorithms=[self.jwt_algorithm],
            )
        except jwt.InvalidTokenError:
            raise CREDENTIALS_EXCEPTION

    def user_to_jwt(self, user: Users) -> str:
        exp = self.jwt_expiry
        return self._encode_jwt(payload={'sub': str(user.id)}, exp=exp)

    async def user_from_jwt_nullable(
        self, creds: Annotated[HTTPAuthorizationCredentials, Depends(USER_AUTH_SCHEME)]
    ) -> Users | None:
        if not creds or not creds.credentials:
            return None
        token_data = self._decode_jwt(jwt_token=creds.credentials)
        return await Users.get_or_none(id=token_data.get('sub'))

    async def user_from_jwt(
        self, creds: Annotated[HTTPAuthorizationCredentials, Depends(USER_AUTH_SCHEME)]
    ) -> Users:
        user = await self.user_from_jwt_nullable(creds)
        if not user:
            raise CREDENTIALS_EXCEPTION
        return user
