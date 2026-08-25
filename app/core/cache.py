import json

import redis

from app.core.config import settings

redis_client = redis.from_url(settings.redis_url, decode_responses=True)

DEFAULT_TTL_SECONDS = 60  # short TTL — price data changes; we don't want a stale cache


def cache_get(key: str):
    # Cache is a performance optimization, not a source of truth — if Redis is
    # unreachable (e.g. in tests, or a transient outage), fail open rather than
    # taking the whole endpoint down.
    try:
        raw = redis_client.get(key)
        return json.loads(raw) if raw else None
    except redis.exceptions.RedisError:
        return None


def cache_set(key: str, value, ttl: int = DEFAULT_TTL_SECONDS):
    try:
        redis_client.set(key, json.dumps(value), ex=ttl)
    except redis.exceptions.RedisError:
        pass


def cache_delete(key: str):
    try:
        redis_client.delete(key)
    except redis.exceptions.RedisError:
        pass
