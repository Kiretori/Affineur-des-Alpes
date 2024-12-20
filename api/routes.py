from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from ..database.connect_db import get_db_connection
from ..api.auth import get_current_user, get_current_admin_user

router = APIRouter()
templates = Jinja2Templates(directory="templates")


db_dependency = Annotated[Session, Depends(get_db_connection)]
user_dependency = Annotated[dict, Depends(get_current_user)]


@router.get("/admin-only")
async def admin_route(current_user: Annotated[dict, Depends(get_current_admin_user)]):
    return {"message": "Admin access granted", "user": current_user}


@router.get("/")
async def read_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
