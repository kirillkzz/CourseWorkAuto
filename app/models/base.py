from app.database import db

class BaseModel:
    TABLE_NAME = ""
    PK = "id"

    @classmethod
    def get_all(cls):
        with db.get_cursor() as cur:
            query = f"SELECT * FROM {cls.TABLE_NAME} ORDER BY {cls.PK} ASC"
            cur.execute(query)
            return cur.fetchall()

    @classmethod
    def get_by_id(cls, id):
        with db.get_cursor() as cur:
            query = f"SELECT * FROM {cls.TABLE_NAME} WHERE {cls.PK} = %s"
            cur.execute(query, (id,))
            return cur.fetchone()

    @classmethod
    def delete(cls, id):
        with db.get_cursor() as cur:
            query = f"DELETE FROM {cls.TABLE_NAME} WHERE {cls.PK} = %s"
            cur.execute(query, (id,))

    @classmethod
    def count(cls):
        with db.get_cursor() as cur:
            query = f"SELECT COUNT(*) as count FROM {cls.TABLE_NAME}"
            cur.execute(query)
            return cur.fetchone()['count']