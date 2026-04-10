import redis
import json

cache = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
def set_cache(key, data, ttl=300):
    cache.setex(key, ttl, json.dumps(data))


def get_cache(key):
    data = cache.get(key)
    if data:
        print(f" CACHE HIT: {key}")
        return json.loads(data)

    print(f" CACHE MISS: {key}")
    return None



def delete_cache(key):
    cache.delete(key)
