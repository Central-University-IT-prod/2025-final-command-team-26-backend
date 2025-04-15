from .. import app_auth
from films_backend.db.models import Users
from typing import Annotated

from fastapi import APIRouter
from fastapi.params import Depends

router = APIRouter(prefix='/users', tags=['Users'])


@router.get('/me')
async def my_login(user: Annotated[Users, Depends(app_auth.user_from_jwt)]) -> str:
    return user.login
