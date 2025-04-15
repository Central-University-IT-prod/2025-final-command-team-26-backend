from dotenv import load_dotenv
from fastapi import HTTPException

import jwt
import datetime
import os

load_dotenv()


class Token:
    def __init__(self):
        self.SECRET_KEY = os.getenv('RANDOM_SECRET')
        self.ALGORITHM = 'HS256'
        self.ACCESS_TOKEN_EXPIRE = 60 * 24

    def create_access_token(self, user_id: str) -> str:
        """
        Генерация токена

        :return: token_id, token
        """

        try:
            payload = {
                'sub': user_id,
                'exp': datetime.datetime.utcnow()
                + datetime.timedelta(minutes=self.ACCESS_TOKEN_EXPIRE),
            }

            token = jwt.encode(payload, self.SECRET_KEY, algorithm=self.ALGORITHM)

            return token

        except Exception as e:
            print(e)

    def verify_token(self, token: str) -> tuple[str, str]:
        """
        Проверка токена

        :return: token_id, yandex_id
        """

        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            yandex_id = payload.get('sub')

            return yandex_id

        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail='Токен истек.')
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail='Недействительный токен.')
        except HTTPException as e:
            raise e
        except Exception as e:
            print(f'Token verification error: {e}')
            raise HTTPException(status_code=500, detail='Внутренняя ошибка сервера')
