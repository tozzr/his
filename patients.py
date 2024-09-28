

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

class Patient:
    def __init__(self, name: str):
        self.id = uuid4()
        self.name = name
        self.done = False

patients = [Patient("Peter Parker")]

router = APIRouter()

# all routes under /patients

@router.get("/", response_class=HTMLResponse)
async def list_patients(request: Request, hx_request: Annotated[Union[str, None], Header()] = None):
    if hx_request:
        return templates.TemplateResponse(
            request=request, name="patient.html", context={"patients": patients}
        )
    return JSONResponse(content=jsonable_encoder(patients))

@router.post("/", response_class=HTMLResponse)
async def create_patient(request: Request, name: Annotated[str, Form()]):
    patients.append(Patient(name))
    return templates.TemplateResponse(
        request=request, name="patient.html", context={"patients": patients}
    )

@router.put("/{patient_id}", response_class=HTMLResponse)
async def update_patient(request: Request, patient_id: str, name: Annotated[str, Form()]):
    for index, patient in enumerate(patients):
        if str(patient.id) == patient_id:
            patient.name = name
            break
    return templates.TemplateResponse(
        request=request, name="patient.html", context={"patients": patients}
    )

@router.post("/{patient_id}/toggle", response_class=HTMLResponse)
async def toggle_patient(request: Request, patient_id: str):
    for index, patient in enumerate(patients):
        if str(patient.id) == patient_id:
            patients[index].done = not patients[index].done
            break
    return templates.TemplateResponse(
        request=request, name="patient.html", context={"patients": patients}
    )

@router.post("/{patient_id}/delete", response_class=HTMLResponse)
async def delete_patient(request: Request, patient_id: str):
    for index, patient in enumerate(patients):
        if str(patient.id) == patient_id:
            del patients[index]
            break
    return templates.TemplateResponse(
        request=request, name="patient.html", context={"patients": patients}
    )