from app.models.base import BaseModel
from app.database import db

class Route(BaseModel):
    TABLE_NAME = "Routes"
    PK = "route_number"

    @classmethod
    def create(cls, route_number, mileage_km, cost_per_km):
        with db.get_cursor() as cur:
            query = """
                INSERT INTO Routes (route_number, mileage_km, cost_per_km)
                VALUES (%s, %s, %s)
            """
            cur.execute(query, (route_number, mileage_km, cost_per_km))