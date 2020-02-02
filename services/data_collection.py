import logging
from datetime import datetime

import aiohttp

from entities import Route, Vehicle
from services import RouteService

logger = logging.getLogger(__name__)


class DataCollectionService:
    def __init__(self, session: aiohttp.ClientSession):
        self.session = session
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
        return routes

    async def retrieve_vehicles(self) -> [Vehicle]:
        url = f'{self.endpoint}/vehicles'
        params = {'filter[route]': 'Orange'}
        vehicles = []

        async with self.session.get(url, params=params) as response:
            response_json = await response.json()
            for data in response_json.get('data', []):
                attributes = data.get('attributes', {})
                try:
                    vehicle = Vehicle(
                        id=data.get('id'),
                        label=attributes.get('label'),
                        latitude=attributes.get('latitude'),
                        longitude=attributes.get('longitude'),
                        current_status=attributes.get('current_status'),
                        updated_at=datetime.fromisoformat(attributes.get('updated_at'))
                    )
                    vehicles.append(vehicle)
                except TypeError as e:
                    logger.error('Error processing vehicle info', extra={'error': e})

        logger.info('Retrieved Vehicles')
        return vehicles
