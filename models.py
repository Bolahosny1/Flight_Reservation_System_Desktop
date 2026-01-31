from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from typing import Optional

class BookingStatus(Enum):
    CONFIRMED = "Confirmed"
    CANCELLED = "Cancelled"
    PENDING = "Pending"

@dataclass(frozen=True)
class Flight:
    id: int
    origin: str
    destination: str
    departure_time: str  # Kept as string for DB simplicity, but could be datetime
    price: float
    capacity: int
    booked_count: int = 0  # New field to track availability

    @property
    def available_seats(self) -> int:
        return self.capacity - self.booked_count

    @property
    def is_available(self) -> bool:
        return self.available_seats > 0

    @property
    def formatted_price(self) -> str:
        return f"${self.price:,.2f}"

    def __repr__(self):
        return f"<Flight {self.origin} -> {self.destination} | Seats: {self.available_seats}>"

@dataclass
class Booking:
    id: Optional[int]
    flight_id: int
    passenger_name: str
    status: BookingStatus = BookingStatus.CONFIRMED
    created_at: datetime = field(default_factory=datetime.now)

    @property
    def is_active(self) -> bool:
        return self.status == BookingStatus.CONFIRMED

    def cancel(self):
        self.status = BookingStatus.CANCELLED
