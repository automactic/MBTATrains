import asyncio
import logging
import asyncpg
import aiohttp

from services.data_collection import DataCollectionService
from sql import create_tables, create_pool


async def repeat(f, interval):
    while True:
        await asyncio.gather(f(), asyncio.sleep(interval))


async def main():
    await create_tables()

    pool = await create_pool()
    async with aiohttp.ClientSession() as session:
        service = DataCollectionService(session, pool)
        await asyncio.gather(
            repeat(service.retrieve_routes, 100),
            repeat(service.retrieve_vehicles, 5),
        )

if __name__ == '__main__':
    logging.basicConfig(level='INFO')
    asyncio.run(main())
