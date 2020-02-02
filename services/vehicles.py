import asyncpg

from entities import Vehicle


class VehicleService:
    def __init__(self, conn: asyncpg.Connection):
        self.conn = conn

    async def upsert(self, vehicles: [Vehicle]):
        values = [(
            vehicle.id,
            vehicle.label,
            vehicle.status,
            vehicle.latitude,
            vehicle.longitude,
            vehicle.updated_at,
            vehicle.in_service,
        ) for vehicle in vehicles]
        await self.conn.executemany('''
            INSERT INTO vehicles (id, label, status, latitude, longitude, updated_at, in_service)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            ON CONFLICT (id)
            DO UPDATE SET label=$2, status=$3, latitude=$4, longitude=$5, updated_at=$6, in_service=$7;
        ''', values)
