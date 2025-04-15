from fastapi import APIRouter, HTTPException, Body
from typing import Annotated

from .. import app_auth
from films_backend.services.oauth import OAuth
from films_backend.schemas.basic_auth import BasicAuth
from films_backend.utils import Token
from films_backend.db.models import Users


auth = OAuth()
jwt = Token()

router = APIRouter(prefix='/auth', tags=['Auth'])


@router.post(
    '/get_token',
    description='Аутентификация через OAuth2',
    responses={
        201: {'description': 'Пользователь успешно зарегистрирован'},
        400: {'description': 'Токен пользователя не найден'},
        404: {'description': 'Пользователь не найден'},
    },
    status_code=201,
)
async def login(body: Annotated[dict, Body()]):
    token = await auth.get_user_token(body['code'])
    data = await auth.get_data(token)

    user, _ = await Users.get_or_create(token=token, defaults={'login': data['login']})
    token = app_auth.user_to_jwt(user=user)

    return {'token': token}


@router.post(
    '/basic/register',
    description='Регистрация пользователя через логин и пароль',
    responses={
        201: {'description': 'Пользователь успешно зарегистрирован'},
        400: {'description': 'Неверная валидация полей'},
        409: {'description': 'Пользователь с таким логином уже существует'},
    },
    status_code=201,
)
async def basic_register(data: BasicAuth):
    if await Users.exists(login=data.login):
        raise HTTPException(status_code=409, detail='User already exists')

    user = await Users.create(
        **data.model_dump(exclude={'password'}),
        password_hash=app_auth.hash(data=data.password),
    )

    token = app_auth.user_to_jwt(user=user)

    return {'token': token}


@router.post(
    '/basic/login',
    description='Аутентификация пользователя через логин и пароль',
    responses={
        201: {'description': 'Успешный вход'},
        400: {'description': 'Неверный формат полей'},
        404: {'description': 'Пользователь не найден'},
    },
    status_code=201,
)
async def basic_login(data: BasicAuth):
    user = await Users.get_or_none(login=data.login)

    if user is None or not app_auth.verify_hash(
        data=data.password, hashed=user.password_hash
    ):
        raise HTTPException(status_code=404, detail='User not found')

    token = app_auth.user_to_jwt(user=user)

    return {'token': token}
