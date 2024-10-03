from fastapi import APIRouter, Depends, FastAPI, Request, Form, Header
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from uuid import uuid4, UUID
from fastapi.encoders import jsonable_encoder
from fastapi.responses import HTMLResponse, JSONResponse
from typing import Annotated, Union
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import UUID as UUIDSql
from main import templates

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import Session

from database import Base, get_db

class Patient(Base):
    __tablename__ = "patients"
    id = Column(UUIDSql(as_uuid=True), primary_key=True, default=uuid4)
    firstname = Column(String, index=True)
    lastname = Column(String, index=True)
    
    def __init__(self, firstname, lastname):
        self.firstname = firstname
        self.lastname = lastname
    
router = APIRouter()

# all routes under /patients
def get_patients(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Patient).offset(skip).limit(limit).all()

@router.get("/widget", response_class=HTMLResponse)
async def widget_patients(request: Request, hx_request: Annotated[Union[str, None], Header()] = None, db: Session = Depends(get_db)):
    if hx_request:
        return templates.TemplateResponse(
            request=request, name="patients_widget.html", context={}
        )
    return JSONResponse(content=jsonable_encoder(get_patients(db)))

@router.get("/modal/create", response_class=HTMLResponse)
async def widget_patients(request: Request, hx_request: Annotated[Union[str, None], Header()] = None):
    if hx_request:
        return templates.TemplateResponse(
            request=request, name="patients_form.html", context={}
        )
    return JSONResponse(content=jsonable_encoder(patients))

@router.get("/", response_class=HTMLResponse)
async def list_patients(request: Request, hx_request: Annotated[Union[str, None], Header()] = None, db: Session = Depends(get_db)):
    if hx_request:
        return templates.TemplateResponse(
            request=request, name="patient.html", context={"patients": get_patients(db)}
        )
    return JSONResponse(content=jsonable_encoder(get_patients(db)))

@router.post("/", response_class=HTMLResponse)
async def create_patient(request: Request, firstname: Annotated[str, Form()], lastname: Annotated[str, Form()], db: Session = Depends(get_db)):
    patient = Patient(firstname, lastname)
    patient.id = uuid4()
    db.add(patient)
    db.commit()
    return templates.TemplateResponse(
        request=request, name="patients_widget.html", context={"patients": get_patients(db)}
    )




def get_patient(db: Session, patient_id: UUID):
    return db.query(Patient).filter(Patient.id == patient_id).first()

@router.put("/{patient_id}", response_class=HTMLResponse)
async def update_patient(request: Request, patient_id: UUID, firstname: Annotated[str, Form()], lastname: Annotated[str, Form()], db: Session = Depends(get_db)):
    patient = get_patient(db, id)
    patient.firstname = firstname
    patient.lastname = lastname
    db.update(patient)
    db.commit()
    db.refresh(patient)
    return templates.TemplateResponse(
        request=request, name="patient.html", context={"patients": get_patients(db)}
    )

@router.post("/{patient_id}/delete", response_class=HTMLResponse)
async def delete_patient(request: Request, patient_id: UUID, db: Session = Depends(get_db)):
    patient = get_patient(db, patient_id)
    db.delete(patient)
    db.commit()
    return templates.TemplateResponse(
        request=request, name="patient.html", context={"patients": get_patients(db)}
    )