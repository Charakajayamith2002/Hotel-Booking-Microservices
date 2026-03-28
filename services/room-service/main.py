from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum

app = FastAPI(
    title="Room Service",
    description="Manages hotel rooms, types, and availability",
    version="1.0.0"
)

rooms_db = {}
counter = {"id": 1}

class RoomType(str, Enum):
    SINGLE = "single"
    DOUBLE = "double"
    SUITE = "suite"
    DELUXE = "deluxe"

class RoomStatus(str, Enum):
    AVAILABLE = "available"
    OCCUPIED = "occupied"
    MAINTENANCE = "maintenance"

class RoomCreate(BaseModel):
    room_number: str
    room_type: RoomType
    floor: int
    price_per_night: float
    max_occupancy: int
    amenities: List[str] = []

class RoomUpdate(BaseModel):
    status: Optional[RoomStatus] = None
    price_per_night: Optional[float] = None
    amenities: Optional[List[str]] = None

class Room(RoomCreate):
    id: int
    status: RoomStatus = RoomStatus.AVAILABLE
    created_at: str

# Seed some default rooms
def seed_rooms():
    sample_rooms = [
        {"room_number": "101", "room_type": "single", "floor": 1, "price_per_night": 80.0, "max_occupancy": 1, "amenities": ["WiFi", "TV"]},
        {"room_number": "201", "room_type": "double", "floor": 2, "price_per_night": 120.0, "max_occupancy": 2, "amenities": ["WiFi", "TV", "Mini-bar"]},
        {"room_number": "301", "room_type": "suite", "floor": 3, "price_per_night": 250.0, "max_occupancy": 4, "amenities": ["WiFi", "TV", "Jacuzzi", "Mini-bar"]},
    ]
    for r in sample_rooms:
        room_id = counter["id"]
        rooms_db[room_id] = Room(id=room_id, created_at=datetime.now().isoformat(), **r)
        counter["id"] += 1

seed_rooms()

@app.get("/", tags=["Health"])
def health_check():
    return {"service": "Room Service", "status": "running", "port": 8002}

@app.get("/rooms", response_model=List[Room], tags=["Rooms"])
def get_all_rooms():
    """Retrieve all rooms"""
    return list(rooms_db.values())

@app.get("/rooms/available", response_model=List[Room], tags=["Rooms"])
def get_available_rooms():
    """Get all currently available rooms"""
    return [r for r in rooms_db.values() if r.status == RoomStatus.AVAILABLE]

@app.get("/rooms/{room_id}", response_model=Room, tags=["Rooms"])
def get_room(room_id: int):
    """Retrieve a room by ID"""
    if room_id not in rooms_db:
        raise HTTPException(status_code=404, detail="Room not found")
    return rooms_db[room_id]

@app.post("/rooms", response_model=Room, status_code=201, tags=["Rooms"])
def create_room(room: RoomCreate):
    """Add a new room"""
    room_id = counter["id"]
    new_room = Room(id=room_id, created_at=datetime.now().isoformat(), **room.dict())
    rooms_db[room_id] = new_room
    counter["id"] += 1
    return new_room

@app.put("/rooms/{room_id}", response_model=Room, tags=["Rooms"])
def update_room(room_id: int, update: RoomUpdate):
    """Update room details or status"""
    if room_id not in rooms_db:
        raise HTTPException(status_code=404, detail="Room not found")
    room = rooms_db[room_id].dict()
    for key, value in update.dict(exclude_none=True).items():
        room[key] = value
    rooms_db[room_id] = Room(**room)
    return rooms_db[room_id]

@app.delete("/rooms/{room_id}", tags=["Rooms"])
def delete_room(room_id: int):
    """Remove a room"""
    if room_id not in rooms_db:
        raise HTTPException(status_code=404, detail="Room not found")
    del rooms_db[room_id]
    return {"message": f"Room {room_id} deleted successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
