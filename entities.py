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
    latitude: float
    longitude: float
    current_status: str
    updated_at: datetime
