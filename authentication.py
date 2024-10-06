from datetime import datetime, timedelta, timezone
from typing import Annotated, Union

import jwt
from jwt.exceptions import InvalidTokenError, PyJWKError
from fastapi import APIRouter, Depends, FastAPI, HTTPException, status, Request, Response
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from users import get_user_by_id, get_user

# to get a string like this run:
# openssl rand -hex 32
ACCESS_TOKEN_SECRET_KEY = "72c14e6b0ac97a6fe571cda98172f09e0bf630414677cb3a6456201544eb9b81"
REFRESH_TOKEN_SECRET_KEY = "cde58c4359c84767870148c9333542549aa58fa07eddab986a36a5e54f74a1c0"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

class TokenData(BaseModel):
    username: Union[str, None] = None


class User(BaseModel):
    username: str
    email: Union[str, None] = None
    full_name: Union[str, None] = None
    disabled: Union[bool, None] = None
    access_token: Union[str, None] = None


class UserInDB(User):
    hashed_password: str

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def authenticate_user(db: Session, username: str, password: str):
    user = get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user


def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, ACCESS_TOKEN_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict, expires_delta: timedelta | None = None):
    """
    Create a refresh token
    Args:
        data (dict): data to be encoded
        expires_delta (timedelta | None, optional): expiration time. Defaults to None.
    Returns:
        str: JWT token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, REFRESH_TOKEN_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, ACCESS_TOKEN_SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    user = get_user(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

router = APIRouter()

@router.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db)
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    refresh_token_expires = timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    refresh_token = create_refresh_token(
        data={"sub": user.username}, expires_delta=refresh_token_expires
    )
    response = RedirectResponse(url='/', status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(key="access_token", value=access_token, httponly=True)
    response.set_cookie(key="refresh_token", value=refresh_token, httponly=True)
    user.access_token = access_token
    return response

async def check_cookie(request: Request):
    cookie = request.cookies
    if not cookie:
        return None
    if cookie.get('refresh_token'):
        return cookie.get('refresh_token')
    
async def decode_token(token: str, key: str | None = None, type: str = 'access') -> str | None:
    """
    Decode a JWT token
    
    Args:
        token (str): JWT token
        key (str | None, optional): key to extract from the token. Defaults to None.
        type (str, optional): type of token [refresh or access]
    Returns:
        str | None: extracted data from the token or None if token is invalid.
    """
    try:
        if type == 'refresh':
            payload = jwt.decode(token, REFRESH_TOKEN_SECRET_KEY, algorithms=[ALGORITHM])
        else:    
            payload = jwt.decode(token, ACCESS_TOKEN_SECRET_KEY, algorithms=[ALGORITHM])     
        if key:
            return payload.get(key)
        return payload.get('sub')
    except PyJWKError as e:
        print(e)
        return None
    
def decode_token2(token: str, key: str | None = None, type: str = 'access') -> str | None:
    """
    Decode a JWT token
    
    Args:
        token (str): JWT token
        key (str | None, optional): key to extract from the token. Defaults to None.
        type (str, optional): type of token [refresh or access]
    Returns:
        str | None: extracted data from the token or None if token is invalid.
    """
    try:
        if type == 'refresh':
            payload = jwt.decode(token, REFRESH_TOKEN_SECRET_KEY, algorithms=[ALGORITHM])
        else:    
            payload = jwt.decode(token, ACCESS_TOKEN_SECRET_KEY, algorithms=[ALGORITHM])     
        if key:
            return payload.get(key)
        return payload.get('sub')
    except PyJWKError as e:
        print(e)
        return None
    
@router.post("/refresh")
async def refresh_token(refresh_token: str = Depends(check_cookie), db: Session = Depends(get_db)):
    """
    Create a refresh token route
    """
    if not refresh_token:
        raise HTTPException(status_code=401, detail="No refresh token")
    decoded_token = await decode_token(refresh_token, 'id', type='refresh')
    if not decoded_token:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    user = get_user_by_id(db, decoded_token)
    if not user:
        raise HTTPException(status_code=401, detail="User does not exist")
    access_token = create_access_token(data={"sub": user.email})
    return JSONResponse({"token": access_token, "email": user.email}, status_code=200)

@router.get("/users/me/", response_model=User)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return current_user


@router.get("/users/me/items/")
async def read_own_items(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return [{"item_id": "Foo", "owner": current_user.username}]
