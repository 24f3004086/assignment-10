from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uuid
import time
from collections import defaultdict

app = FastAPI()

# -----------------------------
# CHANGE THIS TO YOUR EMAIL
# -----------------------------
EMAIL = "24f3004086@ds.study.iitm.ac.in"

# -----------------------------
# Allowed Origins
# -----------------------------
from fastapi.middleware.cors import CORSMiddleware

origins = [
    "https://app-vzn1lg.example.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# Rate Limit Settings
# -----------------------------
RATE_LIMIT = 15
WINDOW = 10

clients = defaultdict(list)

# -----------------------------
# Middleware 1
# Request Context
# -----------------------------
@app.middleware("http")
async def request_context(request: Request, call_next):

    request_id = request.headers.get("X-Request-ID")

    if not request_id:
        request_id = str(uuid.uuid4())

    request.state.request_id = request_id

    response = await call_next(request)

    response.headers["X-Request-ID"] = request_id

    return response


# -----------------------------
# Middleware 2
# Rate Limiter
# -----------------------------
@app.middleware("http")
async def rate_limiter(request: Request, call_next):

    client = request.headers.get("X-Client-Id", "anonymous")

    now = time.time()

    clients[client] = [
        t for t in clients[client]
        if now - t < WINDOW
    ]

    if len(clients[client]) >= RATE_LIMIT:
        return JSONResponse(
            status_code=429,
            content={"detail": "Rate limit exceeded"}
        )

    clients[client].append(now)

    response = await call_next(request)

    return response


# -----------------------------
# Endpoint
# -----------------------------
@app.get("/ping")
async def ping(request: Request):

    return {
        "email": EMAIL,
        "request_id": request.state.request_id
    }