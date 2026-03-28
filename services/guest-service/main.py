from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

app = FastAPI(
    title="Guest Service",
    description="Manages hotel guest profiles and registrations",
    version="1.0.0"
)

# In-memory storage
guests_db = {}
counter = {"id": 1}

class GuestCreate(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone: str
    national_id: str
    nationality: str

class GuestUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None

class Guest(GuestCreate):
    id: int
    created_at: str

@app.get("/", tags=["Health"])
def health_check():
    return {"service": "Guest Service", "status": "running", "port": 8001}

@app.get("/guests", response_model=List[Guest], tags=["Guests"])
def get_all_guests():
    """Retrieve all registered guests"""
    return list(guests_db.values())

@app.get("/guests/{guest_id}", response_model=Guest, tags=["Guests"])
def get_guest(guest_id: int):
    """Retrieve a guest by ID"""
    if guest_id not in guests_db:
        raise HTTPException(status_code=404, detail="Guest not found")
    return guests_db[guest_id]

@app.post("/guests", response_model=Guest, status_code=201, tags=["Guests"])
def create_guest(guest: GuestCreate):
    """Register a new guest"""
    guest_id = counter["id"]
    new_guest = Guest(
        id=guest_id,
        created_at=datetime.now().isoformat(),
        **guest.dict()
    )
    guests_db[guest_id] = new_guest
    counter["id"] += 1
    return new_guest

@app.put("/guests/{guest_id}", response_model=Guest, tags=["Guests"])
def update_guest(guest_id: int, update: GuestUpdate):
    """Update guest information"""
    if guest_id not in guests_db:
        raise HTTPException(status_code=404, detail="Guest not found")
    guest = guests_db[guest_id].dict()
    for key, value in update.dict(exclude_none=True).items():
        guest[key] = value
    guests_db[guest_id] = Guest(**guest)
    return guests_db[guest_id]

@app.delete("/guests/{guest_id}", tags=["Guests"])
def delete_guest(guest_id: int):
    """Delete a guest record"""
    if guest_id not in guests_db:
        raise HTTPException(status_code=404, detail="Guest not found")
    del guests_db[guest_id]
    return {"message": f"Guest {guest_id} deleted successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
