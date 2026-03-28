from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, date
from enum import Enum

app = FastAPI(
    title="Booking Service",
    description="Handles hotel reservations and booking management",
    version="1.0.0"
)

bookings_db = {}
counter = {"id": 1}

class BookingStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CHECKED_IN = "checked_in"
    CHECKED_OUT = "checked_out"
    CANCELLED = "cancelled"

class BookingCreate(BaseModel):
    guest_id: int
    room_id: int
    check_in_date: str   # ISO date string e.g. "2026-04-01"
    check_out_date: str
    num_guests: int
    special_requests: Optional[str] = None

class BookingUpdate(BaseModel):
    status: Optional[BookingStatus] = None
    special_requests: Optional[str] = None
    check_in_date: Optional[str] = None
    check_out_date: Optional[str] = None

class Booking(BookingCreate):
    id: int
    status: BookingStatus = BookingStatus.PENDING
    total_nights: int
    created_at: str

def calc_nights(check_in: str, check_out: str) -> int:
    d1 = datetime.fromisoformat(check_in).date()
    d2 = datetime.fromisoformat(check_out).date()
    return max((d2 - d1).days, 1)

@app.get("/", tags=["Health"])
def health_check():
    return {"service": "Booking Service", "status": "running", "port": 8003}

@app.get("/bookings", response_model=List[Booking], tags=["Bookings"])
def get_all_bookings():
    """Retrieve all bookings"""
    return list(bookings_db.values())

@app.get("/bookings/{booking_id}", response_model=Booking, tags=["Bookings"])
def get_booking(booking_id: int):
    """Retrieve a booking by ID"""
    if booking_id not in bookings_db:
        raise HTTPException(status_code=404, detail="Booking not found")
    return bookings_db[booking_id]

@app.get("/bookings/guest/{guest_id}", response_model=List[Booking], tags=["Bookings"])
def get_bookings_by_guest(guest_id: int):
    """Get all bookings for a specific guest"""
    return [b for b in bookings_db.values() if b.guest_id == guest_id]

@app.post("/bookings", response_model=Booking, status_code=201, tags=["Bookings"])
def create_booking(booking: BookingCreate):
    """Create a new reservation"""
    booking_id = counter["id"]
    nights = calc_nights(booking.check_in_date, booking.check_out_date)
    new_booking = Booking(
        id=booking_id,
        total_nights=nights,
        created_at=datetime.now().isoformat(),
        **booking.dict()
    )
    bookings_db[booking_id] = new_booking
    counter["id"] += 1
    return new_booking

@app.put("/bookings/{booking_id}", response_model=Booking, tags=["Bookings"])
def update_booking(booking_id: int, update: BookingUpdate):
    """Update booking status or details"""
    if booking_id not in bookings_db:
        raise HTTPException(status_code=404, detail="Booking not found")
    booking = bookings_db[booking_id].dict()
    for key, value in update.dict(exclude_none=True).items():
        booking[key] = value
    if "check_in_date" in update.dict(exclude_none=True) or "check_out_date" in update.dict(exclude_none=True):
        booking["total_nights"] = calc_nights(booking["check_in_date"], booking["check_out_date"])
    bookings_db[booking_id] = Booking(**booking)
    return bookings_db[booking_id]

@app.delete("/bookings/{booking_id}", tags=["Bookings"])
def cancel_booking(booking_id: int):
    """Cancel a booking"""
    if booking_id not in bookings_db:
        raise HTTPException(status_code=404, detail="Booking not found")
    bookings_db[booking_id] = Booking(**{**bookings_db[booking_id].dict(), "status": BookingStatus.CANCELLED})
    return {"message": f"Booking {booking_id} cancelled successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
