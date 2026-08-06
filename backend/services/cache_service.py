import json
from extensions import get_redis
from config import Config


def get_cached(key):
    """
    Try to retrieve a value from Redis cache.
    Returns the parsed object if found, or None if not cached.
    """
    redis_client = get_redis()
    if not redis_client:
        return None
    try:
        value = redis_client.get(key)
        if value:
            return json.loads(value)
    except Exception:
        pass
    return None


def set_cached(key, data, ttl=None):
    """
    Store a value in Redis cache with an expiry time.
    ttl (time-to-live) is in seconds. Defaults to Config.CACHE_TTL (5 minutes).
    """
    redis_client = get_redis()
    if not redis_client:
        return
    try:
        redis_client.setex(
            key,
            ttl or Config.CACHE_TTL,
            json.dumps(data)
        )
    except Exception:
        pass


def invalidate_cache(key):
    """
    Delete a specific key from the cache.
    Call this whenever trek data changes so stale data isn't served.
    """
    redis_client = get_redis()
    if not redis_client:
        return
    try:
        redis_client.delete(key)
    except Exception:
        pass


def invalidate_trek_caches():
    """
    Invalidate all trek-related cache keys.
    Called when any trek is created, updated, or deleted.
    """
    invalidate_cache('open_treks')
    invalidate_cache('all_treks')