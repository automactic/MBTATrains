import asyncio
import logging
import os

import aiohttp

import sql
from services.data_collection import DataCollectionService


async def repeat(f, interval):
    while True:
        await asyncio.gather(f(), asyncio.sleep(interval))


async def main():
    await sql.create_tables()
    pool = await sql.create_pool()

    headers = {'x-api-key': os.getenv('API_KEY')}
    async with aiohttp.ClientSession(headers=headers) as session:
        service = DataCollectionService(session, pool)
        await asyncio.gather(
            repeat(service.retrieve_routes, 100),
            repeat(service.retrieve_vehicles, 5),
        )

if __name__ == '__main__':
    logging.basicConfig(level='INFO')
    asyncio.run(main())
