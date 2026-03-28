# 🏨 Hotel Booking System — Microservices Architecture

## Tech Stack
- **Language**: Python 3.10+
- **Framework**: FastAPI
- **API Gateway**: FastAPI + httpx proxy

## Project Structure
```
hotel-booking-system/
├── api-gateway/         → Port 8000 (single entry point)
├── guest-service/       → Port 8001
├── room-service/        → Port 8002
├── booking-service/     → Port 8003
├── payment-service/     → Port 8004
├── staff-service/       → Port 8005
└── feedback-service/    → Port 8006
```

## Installation

Install dependencies for all services:
```bash
pip install fastapi uvicorn httpx pydantic
```

## Running the Services

Open **7 terminal windows** and run one command in each:

```bash
# Terminal 1 - API Gateway
cd api-gateway && python main.py

# Terminal 2 - Guest Service
cd guest-service && python main.py

# Terminal 3 - Room Service
cd room-service && python main.py

# Terminal 4 - Booking Service
cd booking-service && python main.py

# Terminal 5 - Payment Service
cd payment-service && python main.py

# Terminal 6 - Staff Service
cd staff-service && python main.py

# Terminal 7 - Feedback Service
cd feedback-service && python main.py
```

## Swagger UI

| Service          | Direct Swagger URL                        | Via Gateway                          |
|------------------|-------------------------------------------|--------------------------------------|
| API Gateway      | http://localhost:8000/docs                | —                                    |
| Guest Service    | http://localhost:8001/docs                | http://localhost:8000/api/guests     |

## Built-in web UI (new)

You can now open the gateway-embedded UI here after starting all services:
- `http://localhost:8000/` (redirects to the GUI)

This UI calls all services through API Gateway paths:
- `GET /api/guests`
- `GET /api/rooms`
- `GET /api/bookings`
- `GET /api/payments`
- `GET /api/staff`
- `GET /api/feedbacks`

Guest creation button is supported in the UI to add sample guest data.
| Room Service     | http://localhost:8002/docs                | http://localhost:8000/api/rooms      |
| Booking Service  | http://localhost:8003/docs                | http://localhost:8000/api/bookings   |
| Payment Service  | http://localhost:8004/docs                | http://localhost:8000/api/payments   |
| Staff Service    | http://localhost:8005/docs                | http://localhost:8000/api/staff      |
| Feedback Service | http://localhost:8006/docs                | http://localhost:8000/api/feedbacks  |

## Example Requests via Gateway

```bash
# Get all guests
GET http://localhost:8000/api/guests

## Micro-frontend setup (per-service UIs)

Each backend service supports CORS for frontend ports 3000–3006 and gateway 8000.

1. Create a frontend app for each service (e.g., React):
   - `npx create-react-app frontend/guest-ui`
   - `npx create-react-app frontend/room-ui`
2. In each app, call the gateway API path:
   - `GET /api/guests`, `GET /api/rooms`, etc.
3. Run service + gateway + UI apps in separate terminals:
   - `cd guest-service && python main.py`
   - `cd api-gateway && python main.py`
   - `cd frontend/guest-ui && npm start`
4. Use browser URLs:
   - `http://localhost:3000` (guest UI)
   - `http://localhost:8000/api/guests` (gateway route)

```
# Get available rooms
GET http://localhost:8000/api/rooms?available_only=true

# Create a booking
POST http://localhost:8000/api/bookings
{
  "guest_id": 1,
  "room_id": 2,
  "check_in_date": "2026-04-20",
  "check_out_date": "2026-04-25",
  "total_price": 650.0
}

# Process payment
POST http://localhost:8000/api/payments
{
  "booking_id": 1,
  "amount": 650.0,
  "payment_method": "card"
}

# Submit feedback
POST http://localhost:8000/api/feedbacks
{
  "guest_id": 1,
  "booking_id": 1,
  "rating": 5,
  "comment": "Amazing stay!"
}
```
