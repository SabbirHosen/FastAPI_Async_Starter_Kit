import aioredis
import os
from fastapi import Depends

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

class RedisCache:
    def __init__(self):
        self.redis = None

    async def get_redis(self):
        if not self.redis:
            self.redis = await aioredis.from_url(REDIS_URL, decode_responses=True)
        return self.redis

    async def get(self, key: str):
        redis = await self.get_redis()
        return await redis.get(key)

    async def set(self, key: str, value: str, expire: int = 3600):
        redis = await self.get_redis()
        await redis.set(key, value, ex=expire)

redis_cache = RedisCache()
