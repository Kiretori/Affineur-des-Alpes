from datetime import timedelta, datetime, timezone
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette import status
from ..database.connect_db import get_db_connection
from ..database.models import User, UserType
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
import jwt
import os
from dotenv import load_dotenv

load_dotenv()

auth_router = APIRouter(prefix="/auth", tags=["auth"])

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("HASH_ALGORITHM")


bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")


class CreateUserRequest(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


db_dependency = Annotated[Session, Depends(get_db_connection)]


@auth_router.post("/signup", response_class=HTMLResponse)
async def signup(
    request: Request,
    db: db_dependency,
    username: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
):
    if password != confirm_password:
        return """
        <div class="error-message" role="alert">
            Passwords do not match
        </div>
        """

    # Check if user exists
    existing_user = db.query(User).filter(User.username == username).first()
    if existing_user:
        return """
        <div class="error-message" role="alert">
            Username already exists
        </div>
        """

    # Create new user
    create_user_model = User(
        username=username,
        hashed_password=bcrypt_context.hash(password),
        role=UserType.regular,
    )
    db.add(create_user_model)
    db.commit()

    # Return success message
    return """
    <div class="success-message" role="alert">
        Account created successfully! You can now login.
    </div>
    """


@auth_router.post("/token", response_class=HTMLResponse)
async def login(
    request: Request,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: db_dependency,
):
    user = authenticate_user(db, form_data.username, form_data.password)

    if not user:
        # If it's an HTMX request, return error HTML
        if "hx-request" in request.headers:
            return """
            <div class="error-message" role="alert">
                Invalid username or password
            </div>
            """
        # If it's a normal form submit, return an error status code
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    # If the login is successful, create the access token
    token = create_access_token(
        user.username, user.id_user, user.role, timedelta(minutes=20)
    )

    # Check if the request is an HTMX request
    if "hx-request" in request.headers:
        # Return a script for redirection after successful login (HTMX)
        response = """
        <script>
            window.location.href = '/';
        </script>
        """
        return response

    # If it's not an HTMX request, return the token in a JSON response (standard API request)
    return Token(access_token=token, token_type="bearer")


def authenticate_user(db, username: str, password: str) -> bool | User:
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user


def create_access_token(
    username: str, id_user: int, role: UserType, expires_delta: timedelta
):
    encode = {"id": id_user, "sub": username, "role": role.value}
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({"exp": expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)  # type: ignore


async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])  # type: ignore
        username: str | None = payload.get("sub")
        id_user: str | None = payload.get("id")
        role: str | None = payload.get("role")
        if username is None or id_user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate user.",
            )
        return {"id_user": id_user, "username": username, "role": role}
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user."
        )


async def get_current_admin_user(
    current_user: Annotated[dict, Depends(get_current_user)],
) -> dict:
    if current_user["role"] != UserType.admin.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User does not have admin privileges",
        )
    return current_user


@auth_router.post("/logout", response_class=RedirectResponse)
async def logout():
    # Create a RedirectResponse that directly points to the login page
    response = RedirectResponse(url="/login")

    # Remove the access token cookie by setting its expiry date in the past
    response.delete_cookie("access_token")

    return response
