import logging
from datetime import datetime

import aiohttp
import asyncpg

from entities import Route, Vehicle
from services.routes import RouteService
from services.vehicles import VehicleService

logger = logging.getLogger(__name__)


class DataCollectionService:
    def __init__(self, session: aiohttp.ClientSession, pool: asyncpg.pool.Pool):
        self.session = session
        self.pool = pool
        self.endpoint = 'https://api-v3.mbta.com'

    async def get(self, url, params):
        async with self.session.get(url, params=params) as response:
            return await response.json()

    async def retrieve_routes(self) -> [Route]:
        def type_converter(type: int) -> str:
            if type == 0:
                return 'Light Rail'
            elif type == 1:
                return 'Heavy Rail'
            elif type == 2:
                return 'Commuter Rail'
            elif type == 3:
                return 'Bus'
            elif type == 4:
                return 'Ferry'
            else:
                return 'Unknown'

        response_json = await self.get(url=f'{self.endpoint}/routes', params={'filter[type]': '1'})
        routes = []
        for data in response_json.get('data', []):
            attributes = data.get('attributes', {})
            try:
                route = Route(
                    id=data.get('id'),
                    name=attributes.get('long_name'),
                    description=attributes.get('description'),
                    type=type_converter(attributes.get('type')),
                    sort_order=attributes.get('sort_order'),
                    color=attributes.get('color'),
                    text_color=attributes.get('text_color'),
                )
                routes.append(route)
            except TypeError as e:
                logger.error('Error processing route info', extra={'error': e})

        logger.info(f'Retrieved {len(routes)} route(s).')

        async with self.pool.acquire() as conn:
            await RouteService(conn).upsert(routes)
        return routes

    async def retrieve_vehicles(self) -> [Vehicle]:
        response_json = await self.get(url=f'{self.endpoint}/vehicles', params={'filter[route_type]': '1'})
        vehicles = []
        for data in response_json.get('data', []):
            attributes = data.get('attributes', {})
            try:
                vehicle = Vehicle(
                    id=data.get('id'),
                    label=attributes.get('label'),
                    status=attributes.get('current_status'),
                    latitude=attributes.get('latitude'),
                    longitude=attributes.get('longitude'),
                    updated_at=datetime.fromisoformat(attributes.get('updated_at')),
                    in_service=True,
                )
                vehicles.append(vehicle)
            except TypeError as e:
                logger.error('Error processing vehicle info', extra={'error': e})

        logger.info(f'Retrieved {len(vehicles)} vehicle(s).')

        async with self.pool.acquire() as conn:
            await VehicleService(conn).upsert(vehicles)
        return vehicles
