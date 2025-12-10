from app.models.base import BaseModel
from app.database import db

class Vehicle(BaseModel):
    TABLE_NAME = "Vehicles"
    PK = "vehicle_id"

    @classmethod
    def create(cls, license_plate, model, driver_id):
        with db.get_cursor() as cur:
            query = """
                INSERT INTO Vehicles (license_plate, model, driver_id)
                VALUES (%s, %s, %s)
            """
            cur.execute(query, (license_plate, model, driver_id))

    @classmethod
    def get_all_with_drivers(cls):
        with db.get_cursor() as cur:
            query = """
                SELECT v.*, d.full_name as driver_name 
                FROM Vehicles v
                LEFT JOIN Drivers d ON v.driver_id = d.driver_id
                ORDER BY v.vehicle_id
            """
            cur.execute(query)
            return cur.fetchall()