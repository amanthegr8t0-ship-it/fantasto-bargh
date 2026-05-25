import redis
from core.config import REDIS_URL

redis_client = redis.from_url(REDIS_URL)