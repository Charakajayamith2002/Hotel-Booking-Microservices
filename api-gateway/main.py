from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, RedirectResponse
from fastapi.staticfiles import StaticFiles
import httpx
import uvicorn

app = FastAPI(
    title="Hotel Booking - API Gateway",
    description="""
## 🏨 Hotel Booking System — API Gateway

This gateway provides a **single entry point** for all microservices.
Instead of remembering 6 different ports, all requests go through **port 8000**.

### Routing Table

| Gateway Prefix         | Microservice           | Port |
|------------------------|------------------------|------|
| `/api/guests/*`        | Guest Service          | 8001 |
| `/api/rooms/*`         | Room Service           | 8002 |
| `/api/bookings/*`      | Booking Service        | 8003 |
| `/api/payments/*`      | Payment Service        | 8004 |
| `/api/staff/*`         | Staff Service          | 8005 |
| `/api/feedbacks/*`     | Feedback Service       | 8006 |
""",
    version="1.0.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:3002", "http://localhost:3003", "http://localhost:3004", "http://localhost:3005", "http://localhost:3006", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/static", StaticFiles(directory="static"), name="static")

SERVICE_REGISTRY = {
    "guests":    "http://localhost:8001",
    "rooms":     "http://localhost:8002",
    "bookings":  "http://localhost:8003",
    "payments":  "http://localhost:8004",
    "staff":     "http://localhost:8005",
    "feedbacks": "http://localhost:8006",
}

@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/static/index.html")

@app.get("/health", tags=["Gateway"])
def gateway_health():
    return {
        "service": "API Gateway",
        "status": "running",
        "port": 8000,
        "registered_services": list(SERVICE_REGISTRY.keys())
    }

@app.get("/services", tags=["Gateway"])
def list_services():
    return {
        name: {"upstream": url, "gateway_prefix": f"/api/{name}"}
        for name, url in SERVICE_REGISTRY.items()
    }

async def proxy_request(service_name: str, path: str, request: Request) -> Response:
    if service_name not in SERVICE_REGISTRY:
        raise HTTPException(
            status_code=404,
            detail=f"Service '{service_name}' not found. Available: {list(SERVICE_REGISTRY.keys())}"
        )
    base_url = SERVICE_REGISTRY[service_name]
    upstream_path = f"/{service_name}/{path}" if path else f"/{service_name}"
    query_string = str(request.url.query)
    upstream_url = f"{base_url}{upstream_path}"
    if query_string:
        upstream_url += f"?{query_string}"
    headers = {
        k: v for k, v in request.headers.items()
        if k.lower() not in ("host", "content-length")
    }
    body = await request.body()
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            upstream_response = await client.request(
                method=request.method,
                url=upstream_url,
                headers=headers,
                content=body,
            )
        return Response(
            content=upstream_response.content,
            status_code=upstream_response.status_code,
            media_type=upstream_response.headers.get("content-type", "application/json"),
        )
    except httpx.ConnectError:
        raise HTTPException(
            status_code=503,
            detail=f"Service '{service_name}' is unavailable. Make sure it is running."
        )
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail=f"Service '{service_name}' timed out.")

@app.api_route(
    "/api/{service_name}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    tags=["Gateway Proxy"]
)
async def gateway_proxy_root(service_name: str, request: Request):
    return await proxy_request(service_name, "", request)

@app.api_route(
    "/api/{service_name}/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    tags=["Gateway Proxy"]
)
async def gateway_proxy(service_name: str, path: str, request: Request):
    return await proxy_request(service_name, path, request)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)