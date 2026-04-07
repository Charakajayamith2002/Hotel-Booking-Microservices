@echo off
echo Starting Hotel Booking System Microservices...
echo.

start "Guest Service" cmd /k "cd guest-service && python main.py"
timeout /t 1 >nul

start "Room Service" cmd /k "cd room-service && python main.py"
timeout /t 1 >nul

start "Booking Service" cmd /k "cd booking-service && python main.py"
timeout /t 1 >nul

start "Payment Service" cmd /k "cd payment-service && python main.py"
timeout /t 1 >nul

start "Staff Service" cmd /k "cd staff-service && python main.py"
timeout /t 1 >nul

start "Feedback Service" cmd /k "cd feedback-service && python main.py"
timeout /t 1 >nul

timeout /t 2 >nul
start "API Gateway" cmd /k "cd api-gateway && python main.py"
timeout /t 1 >nul
echo.
echo All services started!
echo.
echo ==========================================
echo   UI:      http://localhost:8000
echo   Swagger: http://localhost:8000/docs
echo ==========================================
echo.
pause
