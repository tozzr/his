from fastapi import APIRouter, FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from uuid import uuid4
from fastapi.encoders import jsonable_encoder
from fastapi.responses import HTMLResponse, JSONResponse
from typing import Annotated, Union
from fastapi import FastAPI, Form, Header, Request, Header

from main import templates

class Doctor:
    def __init__(self, name: str):
        self.id = uuid4()
        self.name = name
        self.done = False

doctors = [Doctor("Dr. House")]

router = APIRouter()

# all routes under /doctors

@router.get("/widget", response_class=HTMLResponse)
async def list_doctors(request: Request, hx_request: Annotated[Union[str, None], Header()] = None):
    if hx_request:
        return templates.TemplateResponse(
            request=request, name="doctors_widget.html", context={}
        )
    return JSONResponse(content=jsonable_encoder(doctors))

@router.get("/", response_class=HTMLResponse)
async def list_doctors(request: Request, hx_request: Annotated[Union[str, None], Header()] = None):
    if hx_request:
        return templates.TemplateResponse(
            request=request, name="doctor.html", context={"doctors": doctors}
        )
    return JSONResponse(content=jsonable_encoder(doctors))

@router.post("/", response_class=HTMLResponse)
async def create_doctor(request: Request, name: Annotated[str, Form()]):
    doctors.append(Doctor(name))
    return templates.TemplateResponse(
        request=request, name="doctor.html", context={"doctors": doctors}
    )

@router.put("/{doctor_id}", response_class=HTMLResponse)
async def update_doctor(request: Request, doctor_id: str, name: Annotated[str, Form()]):
    for index, doctor in enumerate(doctors):
        if str(doctor.id) == doctor_id:
            doctor.name = name
            break
    return templates.TemplateResponse(
        request=request, name="doctor.html", context={"doctors": doctors}
    )

@router.post("/{doctor_id}/toggle", response_class=HTMLResponse)
async def toggle_doctor(request: Request, doctor_id: str):
    for index, doctor in enumerate(doctors):
        if str(doctor.id) == doctor_id:
            doctors[index].done = not doctors[index].done
            break
    return templates.TemplateResponse(
        request=request, name="doctor.html", context={"doctors": doctors}
    )

@router.post("/{doctor_id}/delete", response_class=HTMLResponse)
async def delete_doctor(request: Request, doctor_id: str):
    for index, doctor in enumerate(doctors):
        if str(doctor.id) == doctor_id:
            del doctors[index]
            break
    return templates.TemplateResponse(
        request=request, name="doctor.html", context={"doctors": doctors}
    )