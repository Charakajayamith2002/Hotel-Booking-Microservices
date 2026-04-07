#!/bin/bash
echo "Starting Hotel Booking System Microservices..."
echo ""

cd "$(dirname "$0")"

# Start all microservices in background
python guest-service/main.py &
echo "Guest Service started on port 8001"

python room-service/main.py &
echo "Room Service started on port 8002"

python booking-service/main.py &
echo "Booking Service started on port 8003"

python payment-service/main.py &
echo "Payment Service started on port 8004"

python staff-service/main.py &
echo "Staff Service started on port 8005"

python feedback-service/main.py &
echo "Feedback Service started on port 8006"

sleep 2

python api-gateway/main.py &
echo "API Gateway started on port 8000"

python api-gateway/frontend.py &
echo "Frontend started on port 8007"

echo ""
echo "All services running!"
echo ""
echo "Direct Swagger URLs:"
echo "  Guest Service:         http://localhost:8001/docs"
echo "  Room Service:          http://localhost:8002/docs"
echo "  Booking Service:       http://localhost:8003/docs"
echo "  Payment Service:       http://localhost:8004/docs"
echo "  Staff Service:         http://localhost:8005/docs"
echo "  Feedback Service:      http://localhost:8006/docs"
echo ""
echo "Gateway Swagger URL:"
echo "  API Gateway:           http://localhost:8000/docs"
echo ""
echo "Frontend URL:"
echo "  UI:                    http://localhost:8007"
echo ""
echo "Press Ctrl+C to stop all services"
wait
