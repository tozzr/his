from datetime import datetime
from fastapi import Cookie, Depends, FastAPI, HTTPException, Request, status
from fastapi_pagination import add_pagination
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import Annotated, Union
from pydantic import BaseModel

from database import SessionLocal
from authentication import decode_token

app = FastAPI()
add_pagination(app)
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

from authentication import router as auth_router
app.include_router(auth_router, prefix="/auth", tags=["authentication"])

from patients import router as patient_router
app.include_router(patient_router, prefix="/patients", tags=["patients"])

from doctors import router as doctor_router
app.include_router(doctor_router, prefix="/doctors", tags=["doctors"])

def check_auth(access_token: Annotated[Union[str, None], Cookie()] = None):
    return access_token

@app.get("/auth/login.html", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(request=request, name="login.html")

@app.get("/auth/logout.html", response_class=HTMLResponse)
async def index(request: Request):
    response = templates.TemplateResponse(request=request, name="logout_success.html")
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return response

###
class Cookies(BaseModel):
    access_token: str
    refresh_token: str

def check_cookie(request: Request):
    cookie = request.cookies
    if not cookie:
        return None
    if cookie.get('refresh_token'):
        return cookie.get('refresh_token')
    
class UserAnonymousException(Exception):
    def __init__(self, message: str):
        self.message = message
        
def check_authentication(request: Request) -> str | None:
    token = check_cookie(request)
    if token != None:
        user = decode_token(token, 'sub', 'refresh')
        expires = decode_token(token, 'exp', 'refresh')
        print(f"expires: {datetime.fromtimestamp(expires)}")
        if user:
            return user
    raise UserAnonymousException(message="user not authenticated")

@app.exception_handler(UserAnonymousException)
async def user_anonymous_exception_handler(request: Request, exc: UserAnonymousException):
    return RedirectResponse(
        '/auth/login.html?auth=false',
        status_code=status.HTTP_302_FOUND
    )

@app.get("/", response_class=HTMLResponse)
async def index(request: Request, username: Annotated[str, Depends(check_authentication)]):
    return templates.TemplateResponse(request=request, name="index.html", context={"user": username})

@app.get("/protected.html", response_class=HTMLResponse)
async def index2(request: Request, username: Annotated[str, Depends(check_authentication)]):
    return templates.TemplateResponse(request=request, name="protected.html", context={"user": username})
