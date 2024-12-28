from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from ..database.connect_db import get_db_connection
from ..database.models import Produit, Promotion, Magasin
from ..api.auth import get_current_user, get_current_admin_user

router = APIRouter()
templates = Jinja2Templates(directory="templates")


db_dependency = Annotated[Session, Depends(get_db_connection)]
user_dependency = Annotated[dict, Depends(get_current_user)]


@router.get("/admin-only")
async def admin_route(current_user: Annotated[dict, Depends(get_current_admin_user)]):
    return {"message": "Admin access granted", "user": current_user}


@router.get("/login")
async def login(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@router.get("/")
async def home(
    request: Request,
    current_user=user_dependency,
    db: Session = Depends(get_db_connection),
):
    promotions = db.query(Promotion).all()
    products = db.query(Produit).all()
    nearest_store = db.query(Magasin).first()

    return templates.TemplateResponse(
        "main.html",
        {
            "request": request,
            "user": current_user,
            "promotions": promotions,
            "products": products,
            "nearest_store": nearest_store,
        },
    )
