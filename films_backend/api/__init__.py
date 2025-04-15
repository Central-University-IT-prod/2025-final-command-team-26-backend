import redis.asyncio as redis

from films_backend.config import app_config
from films_backend.utils.auth import AppAuth
from films_backend.services.tmdb import GetTMDBData
from films_backend.services.voting import VotingManager
from films_backend.services.websockets import ConnectionManager

app_auth = AppAuth(secret_key=app_config.secret_key, jwt_ttl=app_config.jwt_ttl)
tmdb = GetTMDBData(proxy=app_config.proxy)

redis_client = redis.Redis(
    host=app_config.redis_host, port=app_config.redis_port, decode_responses=True
)
vote_manager = VotingManager(redis_client=redis_client)
connection_manager = ConnectionManager()
