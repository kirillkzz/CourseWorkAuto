import os
from contextlib import contextmanager
from psycopg2 import pool
from psycopg2.extras import RealDictCursor

DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_NAME = os.environ.get('DB_NAME', 'autotransport')
DB_USER = os.environ.get('DB_USER', 'postgres')
DB_PASS = os.environ.get('DB_PASSWORD', 'postgres')

class Database:
    _connection_pool = None

    @classmethod
    def initialize(cls):
        if cls._connection_pool is None:
            try:
                cls._connection_pool = pool.ThreadedConnectionPool(
                    minconn=1,
                    maxconn=20,
                    host=DB_HOST,
                    database=DB_NAME,
                    user=DB_USER,
                    password=DB_PASS
                )
                print("Connection Pool створено успішно.")
            except Exception as e:
                print(f"Помилка створення пулу з'єднань: {e}")

    @classmethod
    @contextmanager
    def get_cursor(cls):
        if cls._connection_pool is None:
            cls.initialize()

        conn = cls._connection_pool.getconn()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                yield cursor
                conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"Помилка SQL: {e}")
            raise e
        finally:
            cls._connection_pool.putconn(conn)

db = Database