import logging
from datetime import datetime

import aiohttp
import asyncpg

from entities import Route, Vehicle, Trip
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
        params = {'filter[route_type]': '1', 'include': 'trip,route'}
        response_json = await self.get(url=f'{self.endpoint}/vehicles', params=params)

        vehicles = {}
        for data in response_json.get('data', []):
            attributes = data.get('attributes', {})
            try:
                vehicle = Vehicle(
                    label=attributes.get('label'),
                    status=attributes.get('current_status'),
                    latitude=attributes.get('latitude'),
                    longitude=attributes.get('longitude'),
                    updated_at=datetime.fromisoformat(attributes.get('updated_at')),
                    in_service=True,
                )
                vehicles[vehicle.label] = vehicle
            except TypeError as e:
                logger.error('Error processing vehicle info', extra={'error': e})
        logger.info(f'Retrieved {len(vehicles)} vehicle(s).')

        trips = self._processing_trips(response_json)

        async with self.pool.acquire() as conn:
            service = VehicleService(conn)
            out_of_service = set(await service.get_in_service_vehicle_labels()) - set(vehicles.keys())
            if out_of_service:
                await service.set_vehicle_out_of_service(list(out_of_service))
                logger.info(f'Mark vehicles {out_of_service} as out of service.')

            await service.upsert(vehicles.values())
            await service.upsert_trips(trips)
        return vehicles.values()

    def _processing_trips(self, response_json) -> [Trip]:
        """Extract trips the vehicles in services are making.

        :param response_json: dict
        :return: [Trip]
        """

        vehicle_labels = {}  # [trip_id, vehicle_label]
        for data in response_json.get('data', []):
            try:
                trip_id = data['relationships']['trip']['data']['id']
                vehicle_label = data['attributes']['label']
                vehicle_labels[trip_id] = vehicle_label
            except KeyError:
                continue

        direction = {}  # [route_id, [direction]]
        trips_data = {}  # [trip_id, dict]
        for data in response_json.get('included', []):
            try:
                data_id, data_type = data['id'], data['type']
                if data_type == 'route':
                    direction[data_id] = data['attributes']['direction_names']
                elif data_type == 'trip':
                    trips_data[data_id] = data
            except KeyError:
                continue

        trips: [Trip] = []
        for trip_id, data in trips_data.items():
            try:
                route_id = data['relationships']['route']['data']['id']
                trip = Trip(
                    id=trip_id,
                    route_id=route_id,
                    vehicle_label=vehicle_labels.get(trip_id),
                    head_sign=data['attributes']['headsign'],
                    direction=direction[route_id][data['attributes']['direction_id']]
                )
                trips.append(trip)
            except KeyError:
                continue

        logger.info(f'Retrieved {len(trips)} trip(s).')

        return trips
