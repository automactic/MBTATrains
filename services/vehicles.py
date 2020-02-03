import asyncpg

from entities import Vehicle, Trip


class VehicleService:
    def __init__(self, conn: asyncpg.Connection):
        self.conn = conn

    async def get_in_service_vehicle_labels(self) -> [str]:
        records = await self.conn.fetch('''
            SELECT label FROM vehicles WHERE in_service=true;
        ''')
        return [record['label'] for record in records]

    async def set_vehicle_out_of_service(self, labels: [str]):
        await self.conn.execute('''
            UPDATE vehicles
            SET in_service=false
            WHERE label = any($1::varchar[]);
        ''', labels)

    async def upsert(self, vehicles: [Vehicle]):
        values = [(
            vehicle.label,
            vehicle.status,
            vehicle.latitude,
            vehicle.longitude,
            vehicle.updated_at,
            vehicle.in_service,
        ) for vehicle in vehicles]
        await self.conn.executemany('''
            INSERT INTO vehicles (label, status, latitude, longitude, updated_at, in_service)
            VALUES ($1, $2, $3, $4, $5, $6)
            ON CONFLICT (label)
            DO UPDATE SET status=$2, latitude=$3, longitude=$4, updated_at=$5, in_service=$6;
        ''', values)

    async def upsert_trips(self, trips: [Trip]):
        values = [(
            trip.id,
            trip.route_id,
            trip.vehicle_label,
            trip.head_sign,
            trip.direction,
        ) for trip in trips]
        await self.conn.executemany('''
            INSERT INTO trips (id, route_id, vehicle_label, head_sign, direction)
            VALUES ($1, $2, $3, $4, $5)
            ON CONFLICT (id)
            DO UPDATE SET route_id=$2, vehicle_label=$3, head_sign=$4, direction=$5;
        ''', values)
