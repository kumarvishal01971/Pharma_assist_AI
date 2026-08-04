from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import parse_cors_origin_regex, parse_cors_origins, settings
from app.core.database import initialize_database
from app.routers import complaints

# Creates tables on startup if they don't exist yet. Fine for this assignment;
# a real deployment would use Alembic migrations instead.
initialize_database()

app = FastAPI(title="AIVOA Complaint Management System", version="0.1.0")

allowed_origins = parse_cors_origins(settings.cors_allowed_origins)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=parse_cors_origin_regex(settings.cors_allowed_origin_regex),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(complaints.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}