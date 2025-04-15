from .routers import auth, films, genres, playlists, rooms, users
from ..utils.api import lifespan

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware


tags_metadata = [
    {
        'name': 'Auth',
        'description': 'Регистрация и авторизация пользователя.',
    },
    {'name': 'Users', 'description': 'Информация о пользователе'},
    {
        'name': 'Films',
        'description': 'Операции с фильмами',
    },
    {
        'name': 'Genres',
        'description': 'Получение списка жанров',
    },
    {
        'name': 'Playlists',
        'description': 'Операции с плейлистами',
    },
    {
        'name': 'Rooms',
        'description': 'Голосование пользователей',
    },
]

app = FastAPI(
    title='Т-фильмы API',
    description='Документация "T-фильмы"',
    root_path='/api',
    lifespan=lifespan,
    openapi_tags=tags_metadata,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(films.router)
app.include_router(genres.router)
app.include_router(playlists.router)
app.include_router(rooms.router)


@app.get('/')
async def root() -> str:
    return 'T-Films API'


@app.get('/ping')
async def ping() -> str:
    return 'АААААААААААААААААААААААААААААААААААААА'


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=400,
        content={
            'status': 'error',
            'message': 'Ошибка валидации данных.',
            'details': str(exc.errors()),
        },
    )
