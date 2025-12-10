from app.models.base import BaseModel
from app.database import db


class RouteSheet(BaseModel):
    TABLE_NAME = "RouteSheets"
    PK = "sheet_id"

    @classmethod
    def create(cls, sheet_date, vehicle_id, route_number, fuel_used_liters):
        with db.get_cursor() as cur:
            query = """
                INSERT INTO RouteSheets (sheet_date, vehicle_id, route_number, fuel_used_liters)
                VALUES (%s, %s, %s, %s)
            """
            cur.execute(query, (sheet_date, vehicle_id, route_number, fuel_used_liters))

    @classmethod
    def update(cls, sheet_id, sheet_date, vehicle_id, route_number, fuel_used_liters):
        with db.get_cursor() as cur:
            query = """
                UPDATE RouteSheets 
                SET sheet_date = %s, vehicle_id = %s, route_number = %s, fuel_used_liters = %s
                WHERE sheet_id = %s
            """
            cur.execute(query, (sheet_date, vehicle_id, route_number, fuel_used_liters, sheet_id))

    @classmethod
    def is_vehicle_busy(cls, vehicle_id, check_date, exclude_sheet_id=None):
        with db.get_cursor() as cur:
            query = """
                SELECT COUNT(*) as count 
                FROM RouteSheets 
                WHERE vehicle_id = %s AND sheet_date = %s
            """
            params = [vehicle_id, check_date]
            if exclude_sheet_id:
                query += " AND sheet_id != %s"
                params.append(exclude_sheet_id)
            cur.execute(query, tuple(params))
            return cur.fetchone()['count'] > 0

    @classmethod
    def get_total_fuel(cls):
        with db.get_cursor() as cur:
            cur.execute("SELECT SUM(fuel_used_liters) as total FROM RouteSheets")
            res = cur.fetchone()
            return res['total'] if res and res['total'] else 0

    @classmethod
    def get_full_report(cls, sort_by='sheet_date', sort_order='desc', vehicle_id=None, route_filter=None, limit=None,
                        offset=0):
        allowed_sorts = {
            'sheet_date': 'rs.sheet_date',
            'fuel': 'rs.fuel_used_liters',
            'mileage': 'r.mileage_km'
        }
        sort_column = allowed_sorts.get(sort_by, 'rs.sheet_date')
        order_direction = 'ASC' if sort_order.lower() == 'asc' else 'DESC'

        with db.get_cursor() as cur:
            base_query = """
                SELECT 
                    rs.sheet_id, rs.sheet_date, rs.fuel_used_liters,
                    rs.vehicle_id, rs.route_number,
                    v.license_plate, v.model,
                    d.full_name as driver_name,
                    r.mileage_km
                FROM RouteSheets rs
                JOIN Vehicles v ON rs.vehicle_id = v.vehicle_id
                JOIN Drivers d ON v.driver_id = d.driver_id
                JOIN Routes r ON rs.route_number = r.route_number
            """

            where_clauses = []
            params = []

            if vehicle_id:
                where_clauses.append("rs.vehicle_id = %s")
                params.append(vehicle_id)

            if route_filter:
                where_clauses.append("rs.route_number = %s")
                params.append(route_filter)

            where_sql = ""
            if where_clauses:
                where_sql = " WHERE " + " AND ".join(where_clauses)

            count_query = f"SELECT COUNT(*) as total FROM RouteSheets rs {where_sql}"
            cur.execute(count_query, tuple(params))
            total_rows = cur.fetchone()['total']

            query = base_query + where_sql + f" ORDER BY {sort_column} {order_direction}"

            if limit:
                query += f" LIMIT {limit} OFFSET {offset}"

            cur.execute(query, tuple(params))
            return cur.fetchall(), total_rows