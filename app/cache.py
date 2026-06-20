import logging

from redis import Redis, RedisError

from .config import REDIS_URL

logger = logging.getLogger(__name__)


def get_cache_client() -> Redis | None:
    try:
        client = Redis.from_url(REDIS_URL, decode_responses=True)
        client.ping()
        return client
    except RedisError as error:
        logger.warning("Redis offline ou não configurado: %s", error)
        return None


cache_client = get_cache_client()


def increment_counter(key: str, amount: int = 1) -> None:
    if not cache_client:
        return
    try:
        cache_client.incrby(key, amount)
    except RedisError as error:
        logger.warning("Falha ao incrementar contador Redis %s: %s", key, error)


def set_value(key: str, value: str) -> None:
    if not cache_client:
        return
    try:
        cache_client.set(key, value)
    except RedisError as error:
        logger.warning("Falha ao definir valor Redis %s: %s", key, error)


def get_value(key: str) -> str | None:
    if not cache_client:
        return None
    try:
        return cache_client.get(key)
    except RedisError as error:
        logger.warning("Falha ao ler valor Redis %s: %s", key, error)
        return None
