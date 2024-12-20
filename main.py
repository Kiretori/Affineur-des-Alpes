from dotenv import load_dotenv
import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from .api import auth, routes
from pathlib import Path

load_dotenv()

secret_key = os.getenv("SECRET_KEY")
if not secret_key:
    raise ValueError("Secret key not provided in environment")
app = FastAPI()

BASE_DIR = Path(__file__).resolve().parent

# Mount the static directory
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")


app.include_router(auth.auth_router)
app.include_router(routes.router)
