import asyncpg

from entities import Route


class RouteService:
    def __init__(self, conn: asyncpg.Connection):
        self.conn = conn

    async def list(self) -> [Route]:
        records = await self.conn.fetch('''
            SELECT id, name, description, type, sort_order, color, text_color FROM routes
        ''')
        routes = [Route(**record) for record in records]
        return routes

    async def upsert(self, routes: [Route]):
        values = [(
            route.id,
            route.name,
            route.description,
            route.type,
            route.sort_order,
            route.color,
            route.text_color,
        ) for route in routes]
        await self.conn.executemany('''
            INSERT INTO routes (id, name, description, type, sort_order, color, text_color)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            ON CONFLICT (id)
            DO UPDATE SET name=$2, description=$3, type=$4, sort_order=$5, color=$6, text_color=$7;
        ''', values)
