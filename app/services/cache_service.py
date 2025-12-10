import redis
import os
import json
import datetime


class CacheService:
    _client = None

    @classmethod
    def get_client(cls):
        if cls._client is None:
            try:
                redis_host = os.environ.get('REDIS_HOST', 'localhost')
                cls._client = redis.Redis(
                    host=redis_host,
                    port=6379,
                    decode_responses=True,
                    socket_connect_timeout=2
                )
                cls._client.ping()
            except Exception as e:
                print(f"Redis недоступний: {e}")
                cls._client = None
        return cls._client

    @staticmethod
    def _json_serial(obj):
        if isinstance(obj, (datetime.date, datetime.datetime)):
            return obj.isoformat()
        raise TypeError(f"Type {type(obj)} not serializable")

    @classmethod
    def get_report(cls):
        client = cls.get_client()
        if not client:
            return None

        try:
            data = client.get('full_report_v1')
            if data:
                return json.loads(data)
        except Exception as e:
            print(f"Помилка читання кешу: {e}")
        return None

    @classmethod
    def save_report(cls, data, ttl=60):
        client = cls.get_client()
        if not client:
            return

        try:
            json_data = json.dumps(data, default=cls._json_serial)
            client.setex('full_report_v1', ttl, json_data)
        except Exception as e:
            print(f"Помилка запису в кеш: {e}")

    @classmethod
    def clear_report_cache(cls):
        client = cls.get_client()
        if client:
            client.delete('full_report_v1')
            print("Кеш успішно очищено.")

    @classmethod
    def log_action(cls, message):
        client = cls.get_client()
        if client:
            try:
                timestamp = datetime.datetime.now().strftime("%H:%M:%S")
                full_message = f"[{timestamp}] {message}"
                client.lpush('recent_actions', full_message)
                client.ltrim('recent_actions', 0, 9)
            except Exception as e:
                print(f"Redis Log Error: {e}")

    @classmethod
    def get_recent_actions(cls):
        client = cls.get_client()
        if not client:
            return []

        try:
            return client.lrange('recent_actions', 0, -1)
        except Exception as e:
            print(f"Redis Read Error: {e}")
            return []