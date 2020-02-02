import asyncpg

from entities import Vehicle


class VehicleService:
    def __init__(self, conn: asyncpg.Connection):
        self.conn = conn

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
