from app.models.base import BaseModel
from app.database import db

class Driver(BaseModel):
    TABLE_NAME = "Drivers"
    PK = "driver_id"

    @classmethod
    def create(cls, full_name, phone, address):
        with db.get_cursor() as cur:
            query = """
                INSERT INTO Drivers (full_name, phone, address)
                VALUES (%s, %s, %s)
                RETURNING driver_id
            """
            cur.execute(query, (full_name, phone, address))
            return cur.fetchone()['driver_id']

    @classmethod
    def search(cls, query_str):
        with db.get_cursor() as cur:
            sql = "SELECT * FROM Drivers WHERE full_name ILIKE %s ORDER BY full_name"
            cur.execute(sql, (f"%{query_str}%",))
            return cur.fetchall()