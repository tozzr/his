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

class Patient:
    def __init__(self, name: str):
        self.id = uuid4()
        self.name = name
        self.done = False

patients = [Patient("Peter Parker")]

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@app.get("/patients", response_class=HTMLResponse)
async def list_patients(request: Request, hx_request: Annotated[Union[str, None], Header()] = None):
    if hx_request:
        return templates.TemplateResponse(
            request=request, name="patient.html", context={"patients": patients}
        )
    return JSONResponse(content=jsonable_encoder(patients))

@app.post("/patients", response_class=HTMLResponse)
async def create_patient(request: Request, patient: Annotated[str, Form()]):
    patients.append(patient(patient))
    return templates.TemplateResponse(
        request=request, name="patients.html", context={"patients": patients}
    )

@app.put("/patients/{patient_id}", response_class=HTMLResponse)
async def update_patient(request: Request, patient_id: str, text: Annotated[str, Form()]):
    for index, patient in enumerate(patients):
        if str(patient.id) == patient_id:
            patient.text = text
            break
    return templates.TemplateResponse(
        request=request, name="patients.html", context={"patients": patients}
    )

@app.post("/patients/{patient_id}/toggle", response_class=HTMLResponse)
async def toggle_patient(request: Request, patient_id: str):
    for index, patient in enumerate(patients):
        if str(patient.id) == patient_id:
            patients[index].done = not patients[index].done
            break
    return templates.TemplateResponse(
        request=request, name="patients.html", context={"patients": patients}
    )

@app.post("/patients/{patient_id}/delete", response_class=HTMLResponse)
async def delete_patient(request: Request, patient_id: str):
    for index, patient in enumerate(patients):
        if str(patient.id) == patient_id:
            del patients[index]
            break
    return templates.TemplateResponse(
        request=request, name="patients.html", context={"patients": patients}
    )