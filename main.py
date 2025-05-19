import asyncio
import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, HTTPException, Request, APIRouter
from fastapi.openapi.utils import get_openapi
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from models.role import RoleBase
from routes.v1 import auth, trainings, training_dates, bookings
from utils.config import settings
from utils.database import roles_collection
from utils.exception_handler import global_exception_handler, http_exception_handler
from utils.logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)
limiter = Limiter(key_func=get_remote_address, default_limits=[settings.ACCESS_LIMIT])

initial_roles = [
    RoleBase(name="admin", permissions=["read", "create", "update", "delete", "read_training", "manage_booking"]),
    RoleBase(name="user", permissions=["read_training", "manage_booking"]),
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    if await roles_collection.count_documents({}) == 0:
        await roles_collection.insert_many([role.dict() for role in initial_roles])
        logger.info("[FastAPI] Initial roles seeded.")
    else:
        logger.info("[FastAPI] Roles already exist, skipping seed.")
    yield


app = FastAPI(
    title=settings.TITLE,
    description=settings.DESCRIPTION,
    version=settings,
    lifespan=lifespan,
    contact={
        "name": "API Support",
        "email": "stefan.h@cker.tel",
    },
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
    redoc_url="/api/redoc"

)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=settings.TITLE,
        version=settings.VERSION,
        description=settings.DESCRIPTION,
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

app.add_exception_handler(Exception, global_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

allowed_origins = [
    "http://localhost",
    "http://127.0.0.1",
    "https://localhost",
    "https://127.0.0.1",
    "http://localhost:3000",
    "http://127.0.0.1:3000",

]
# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Custom exception handler (optional)
@app.exception_handler(RateLimitExceeded)
async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    content = f"Rate limit exceeded. {exc.detail}. Try again later."
    logger.error(content, exc_info=True)
    return JSONResponse(
        status_code=429,
        content={"detail": content},
    )


root_router = APIRouter(prefix="/api")

root_router.include_router(auth.router, prefix="/v1")
root_router.include_router(trainings.router, prefix="/v1")
root_router.include_router(training_dates.router, prefix="/v1")
root_router.include_router(bookings.router, prefix="/v1")


@root_router.get("/")
@limiter.limit("5/minute")  # Limit to 5 requests per minute per IP
async def root(request: Request):
    return {"message": "Hello, to Training Provider API!"}


app.include_router(root_router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
