from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum

app = FastAPI(
    title="Payment Service",
    description="Processes and manages hotel payments and invoices",
    version="1.0.0"
)

payments_db = {}
counter = {"id": 1}

class PaymentMethod(str, Enum):
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    CASH = "cash"
    BANK_TRANSFER = "bank_transfer"

class PaymentStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"

class PaymentCreate(BaseModel):
    booking_id: int
    guest_id: int
    amount: float
    currency: str = "USD"
    payment_method: PaymentMethod

class PaymentUpdate(BaseModel):
    status: Optional[PaymentStatus] = None

class Payment(PaymentCreate):
    id: int
    status: PaymentStatus = PaymentStatus.PENDING
    transaction_ref: str
    paid_at: Optional[str] = None
    created_at: str

def generate_ref(payment_id: int) -> str:
    return f"TXN-HBS-{datetime.now().strftime('%Y%m%d')}-{payment_id:04d}"

@app.get("/", tags=["Health"])
def health_check():
    return {"service": "Payment Service", "status": "running", "port": 8004}

@app.get("/payments", response_model=List[Payment], tags=["Payments"])
def get_all_payments():
    """Retrieve all payment records"""
    return list(payments_db.values())

@app.get("/payments/{payment_id}", response_model=Payment, tags=["Payments"])
def get_payment(payment_id: int):
    """Retrieve a payment by ID"""
    if payment_id not in payments_db:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payments_db[payment_id]

@app.get("/payments/booking/{booking_id}", response_model=List[Payment], tags=["Payments"])
def get_payments_by_booking(booking_id: int):
    """Get all payments linked to a booking"""
    return [p for p in payments_db.values() if p.booking_id == booking_id]

@app.post("/payments", response_model=Payment, status_code=201, tags=["Payments"])
def create_payment(payment: PaymentCreate):
    """Process a new payment"""
    payment_id = counter["id"]
    new_payment = Payment(
        id=payment_id,
        transaction_ref=generate_ref(payment_id),
        status=PaymentStatus.COMPLETED,
        paid_at=datetime.now().isoformat(),
        created_at=datetime.now().isoformat(),
        **payment.dict()
    )
    payments_db[payment_id] = new_payment
    counter["id"] += 1
    return new_payment

@app.put("/payments/{payment_id}", response_model=Payment, tags=["Payments"])
def update_payment_status(payment_id: int, update: PaymentUpdate):
    """Update payment status (e.g. refund)"""
    if payment_id not in payments_db:
        raise HTTPException(status_code=404, detail="Payment not found")
    payment = payments_db[payment_id].dict()
    for key, value in update.dict(exclude_none=True).items():
        payment[key] = value
    payments_db[payment_id] = Payment(**payment)
    return payments_db[payment_id]

@app.delete("/payments/{payment_id}", tags=["Payments"])
def refund_payment(payment_id: int):
    """Initiate a refund for a payment"""
    if payment_id not in payments_db:
        raise HTTPException(status_code=404, detail="Payment not found")
    payments_db[payment_id] = Payment(**{**payments_db[payment_id].dict(), "status": PaymentStatus.REFUNDED})
    return {"message": f"Payment {payment_id} refunded successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)
