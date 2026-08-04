from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_cors_config
from app.core.database import initialize_database
from app.routers import complaints

# Creates tables on startup if they don't exist yet. Fine for this assignment;
# a real deployment would use Alembic migrations instead.
initialize_database()

app = FastAPI(title="AIVOA Complaint Management System", version="0.1.0")

allowed_origins, allowed_origin_regex = get_cors_config()

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=allowed_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(complaints.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}