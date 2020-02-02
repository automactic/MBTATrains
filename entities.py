from dataclasses import dataclass
from datetime import datetime

@dataclass
class Route:
    id: str
    name: str
    description: str
    type: str
    sort_order: int
    color: str
    text_color: str


@dataclass
class Vehicle:
    id: str
    label: str
    status: str
    latitude: float
    longitude: float
    updated_at: datetime
    in_service: bool = False
