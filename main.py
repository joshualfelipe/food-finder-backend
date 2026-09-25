import logging
import uuid

from controller.router_loader import register_routers
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from postgrest.exceptions import APIError

logger = logging.getLogger(__name__)

app = FastAPI()

# Postgres error codes that are the client's fault; everything else (e.g. 42501
# permission denied) is a server/config problem and surfaces as a 500.
DB_CLIENT_ERRORS = {
    "22P02": (status.HTTP_400_BAD_REQUEST, "Invalid identifier format."),
    "23503": (status.HTTP_400_BAD_REQUEST, "Referenced resource does not exist."),
    "23505": (status.HTTP_409_CONFLICT, "Resource already exists."),
}


@app.exception_handler(APIError)
async def database_error_handler(request: Request, error: APIError) -> JSONResponse:
    status_code, detail = DB_CLIENT_ERRORS.get(
        error.code,
        (status.HTTP_500_INTERNAL_SERVER_ERROR, "A database error occurred."),
    )
    # Full DB details (table names, hints) go to the logs only, never the client;
    # error_id is returned so a client-reported error can be found in the logs
    error_id = str(uuid.uuid4())
    logger.error(
        "Database error [%s] on %s %s: code=%s message=%s hint=%s",
        error_id,
        request.method,
        request.url.path,
        error.code,
        error.message,
        error.hint,
    )
    return JSONResponse(
        status_code=status_code, content={"detail": detail, "error_id": error_id}
    )


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_routers(app)


@app.get("/")
async def root():
    return {"message": "API is running"}
