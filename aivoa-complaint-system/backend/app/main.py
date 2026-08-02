from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import initialize_database
from app.routers import complaints

# Creates tables on startup if they don't exist yet. Fine for this assignment;
# a real deployment would use Alembic migrations instead.
initialize_database()

app = FastAPI(title="AIVOA Complaint Management System", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://0.0.0.0:5173",
        "http://10.0.10.47:5173",
        "http://10.0.2.15:5173",
    ],
    allow_origin_regex=r"https://.*\.app\.github\.dev",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(complaints.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
