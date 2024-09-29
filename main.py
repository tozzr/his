from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from uuid import uuid4
from fastapi.encoders import jsonable_encoder
from fastapi.responses import HTMLResponse, JSONResponse
from typing import Annotated, Union
from fastapi import FastAPI, Form, Header, Request, Header

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

from patients import router as patient_router
app.include_router(patient_router, prefix="/patients", tags=["patients"])

from doctors import router as doctor_router
app.include_router(doctor_router, prefix="/doctors", tags=["doctors"])
