from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum

app = FastAPI(
    title="Notification Service",
    description="Sends and manages email/SMS notifications to guests and staff",
    version="1.0.0"
)

notifications_db = {}
counter = {"id": 1}

class NotificationType(str, Enum):
    BOOKING_CONFIRMATION = "booking_confirmation"
    BOOKING_CANCELLATION = "booking_cancellation"
    CHECK_IN_REMINDER = "check_in_reminder"
    CHECK_OUT_REMINDER = "check_out_reminder"
    PAYMENT_RECEIPT = "payment_receipt"
    GENERAL = "general"

class NotificationChannel(str, Enum):
    EMAIL = "email"
    SMS = "sms"
    BOTH = "both"

class NotificationStatus(str, Enum):
    QUEUED = "queued"
    SENT = "sent"
    FAILED = "failed"

class NotificationCreate(BaseModel):
    recipient_id: int
    recipient_email: str
    recipient_phone: Optional[str] = None
    notification_type: NotificationType
    channel: NotificationChannel = NotificationChannel.EMAIL
    subject: str
    message: str
    booking_id: Optional[int] = None

class NotificationUpdate(BaseModel):
    status: Optional[NotificationStatus] = None

class Notification(NotificationCreate):
    id: int
    status: NotificationStatus = NotificationStatus.QUEUED
    sent_at: Optional[str] = None
    created_at: str

@app.get("/", tags=["Health"])
def health_check():
    return {"service": "Notification Service", "status": "running", "port": 8006}

@app.get("/notifications", response_model=List[Notification], tags=["Notifications"])
def get_all_notifications():
    """Retrieve all notifications"""
    return list(notifications_db.values())

@app.get("/notifications/{notification_id}", response_model=Notification, tags=["Notifications"])
def get_notification(notification_id: int):
    """Retrieve a specific notification by ID"""
    if notification_id not in notifications_db:
        raise HTTPException(status_code=404, detail="Notification not found")
    return notifications_db[notification_id]

@app.get("/notifications/recipient/{recipient_id}", response_model=List[Notification], tags=["Notifications"])
def get_notifications_by_recipient(recipient_id: int):
    """Get all notifications sent to a specific guest"""
    return [n for n in notifications_db.values() if n.recipient_id == recipient_id]

@app.get("/notifications/booking/{booking_id}", response_model=List[Notification], tags=["Notifications"])
def get_notifications_by_booking(booking_id: int):
    """Get all notifications related to a booking"""
    return [n for n in notifications_db.values() if n.booking_id == booking_id]

@app.post("/notifications", response_model=Notification, status_code=201, tags=["Notifications"])
def send_notification(notification: NotificationCreate):
    """Send a new notification"""
    notif_id = counter["id"]
    new_notif = Notification(
        id=notif_id,
        status=NotificationStatus.SENT,
        sent_at=datetime.now().isoformat(),
        created_at=datetime.now().isoformat(),
        **notification.dict()
    )
    notifications_db[notif_id] = new_notif
    counter["id"] += 1
    return new_notif

@app.put("/notifications/{notification_id}", response_model=Notification, tags=["Notifications"])
def update_notification(notification_id: int, update: NotificationUpdate):
    """Update notification status"""
    if notification_id not in notifications_db:
        raise HTTPException(status_code=404, detail="Notification not found")
    notif = notifications_db[notification_id].dict()
    for key, value in update.dict(exclude_none=True).items():
        notif[key] = value
    notifications_db[notification_id] = Notification(**notif)
    return notifications_db[notification_id]

@app.delete("/notifications/{notification_id}", tags=["Notifications"])
def delete_notification(notification_id: int):
    """Delete a notification record"""
    if notification_id not in notifications_db:
        raise HTTPException(status_code=404, detail="Notification not found")
    del notifications_db[notification_id]
    return {"message": f"Notification {notification_id} deleted successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8006)
