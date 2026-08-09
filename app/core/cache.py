"""Thin Redis cache wrapper.

Degrades gracefully: if Redis is unreachable, reads miss and writes no-op so the
API keeps working (cache is an optimization, not a dependency).
"""

import json
import logging
from typing import Any, Optional

import redis

from app.core.config import settings

logger = logging.getLogger(__name__)

try:
    _client: Optional[redis.Redis] = redis.Redis.from_url(
        settings.REDIS_URL, decode_responses=True, socket_connect_timeout=1
    )
except Exception as exc:  # pragma: no cover - construction rarely fails
    logger.warning("Redis client init failed: %s", exc)
    _client = None


def cache_get(key: str) -> Optional[Any]:
    if _client is None:
        return None
    try:
        raw = _client.get(key)
        return json.loads(raw) if raw is not None else None
    except Exception as exc:
        logger.warning("Redis GET failed (%s): %s", key, exc)
        return None


def cache_set(key: str, value: Any, ttl_seconds: int = 60) -> None:
    if _client is None:
        return
    try:
        _client.set(key, json.dumps(value, default=str), ex=ttl_seconds)
    except Exception as exc:
        logger.warning("Redis SET failed (%s): %s", key, exc)


def cache_delete(*keys: str) -> None:
    if _client is None or not keys:
        return
    try:
        _client.delete(*keys)
    except Exception as exc:
        logger.warning("Redis DEL failed (%s): %s", keys, exc)
