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
class Doctor(Base):
    __tablename__ = "doctors"
    id = Column(UUIDSql(as_uuid=True), primary_key=True, default=uuid4)
    firstname = Column(String, index=True)
    lastname = Column(String, index=True)
    
    def __init__(self, firstname, lastname):
        self.firstname = firstname
        self.lastname = lastname
   
router = APIRouter()

# all routes under /doctors
def get_doctors(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Doctor).offset(skip).limit(limit).all()

@router.get("/widget", response_class=HTMLResponse)
async def list_doctors(request: Request, hx_request: Annotated[Union[str, None], Header()] = None, db: Session = Depends(get_db)):
    if hx_request:
        return templates.TemplateResponse(
            request=request, name="doctors_widget.html", context={}
        )
    return JSONResponse(content=jsonable_encoder(get_doctors(db)))

@router.get("/", response_class=HTMLResponse)
async def list_doctors(request: Request, hx_request: Annotated[Union[str, None], Header()] = None, db: Session = Depends(get_db)):
    if hx_request:
        return templates.TemplateResponse(
            request=request, name="doctor.html", context={"doctors": get_doctors(db)}
        )
    return JSONResponse(content=jsonable_encoder(get_doctors(db)))

@router.post("/", response_class=HTMLResponse)
async def create_doctor(request: Request, firstname: Annotated[str, Form()], lastname: Annotated[str, Form()], db: Session = Depends(get_db)):
    doctor = Doctor(firstname, lastname)
    doctor.id = uuid4()
    db.add(doctor)
    db.commit()
    return templates.TemplateResponse(
        request=request, name="doctor.html", context={"doctors": get_doctors(db)}
    )

def get_doctor(db: Session, patient_id: UUID):
    return db.query(Doctor).filter(Doctor.id == patient_id).first()

@router.put("/{doctor_id}", response_class=HTMLResponse)
async def update_doctor(request: Request, doctor_id: str, firstname: Annotated[str, Form()], lastname: Annotated[str, Form()], db: Session = Depends(get_db)):
    doctor = get_doctor(db, doctor_id)
    doctor.firstname = firstname
    doctor.lastname = lastname
    db.merge(doctor)
    db.commit()
    return templates.TemplateResponse(
        request=request, name="doctor.html", context={"doctors": get_doctors(db)}
    )

@router.post("/{doctor_id}/delete", response_class=HTMLResponse)
async def delete_doctor(request: Request, doctor_id: str, db: Session = Depends(get_db)):
    doctor = get_doctor(db, doctor_id)
    db.delete(doctor)
    db.commit()
    return templates.TemplateResponse(
        request=request, name="doctor.html", context={"doctors": get_doctors(db)}
    )