from fastapi import APIRouter, Depends, FastAPI, Request, Form, Header, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from uuid import uuid4, UUID
from fastapi.encoders import jsonable_encoder
from fastapi.responses import HTMLResponse, JSONResponse
from typing import Annotated, Union
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import UUID as UUIDSql
from main import templates
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, select, or_
from sqlalchemy.orm import Session

from database import Base, get_db

from fastapi_pagination.ext.sqlalchemy import paginate
from fastapi_pagination.links import Page
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

# create
@router.get("/form.html", response_class=HTMLResponse)
async def create_patient_form(request: Request):
    return templates.TemplateResponse(
        request=request, name="patients_form.html", context={"patient": Patient('','')}
    )

@router.post("/", response_class=HTMLResponse)
async def create_patient(request: Request, firstname: Annotated[str, Form()], lastname: Annotated[str, Form()], db: Session = Depends(get_db)):
    patient = Patient(firstname, lastname)
    patient.id = uuid4()
    db.add(patient)
    db.commit()
    return RedirectResponse(
        '/patients/list.html?page=1&size=10', 
        status_code=status.HTTP_302_FOUND)
   
# list 
@router.get("/", response_class=HTMLResponse)
async def list_patients(request: Request, hx_request: Annotated[Union[str, None], Header()] = None, search: Union[str, None] = '', db: Session = Depends(get_db)) -> Page[Patient]:
    print('search: ' + search)
    if hx_request:
        return templates.TemplateResponse(
            request=request, name="patients_list_full.html",
            context={
                "patients": paginate(db,
                                select(Patient)
                                .where(or_(Patient.lastname.ilike(f'%{search}%'), Patient.firstname.ilike(f'%{search}%')))
                                .order_by(Patient.lastname, Patient.firstname)
                            ),
                "search": search
            }
        )
    return JSONResponse(content=jsonable_encoder(paginate(db, select(Patient).order_by(Patient.lastname, Patient.firstname)).items))

@router.get("/list.html", response_class=HTMLResponse)
async def list_patients_html(request: Request, hx_request: Annotated[Union[str, None], Header()] = None, search: Union[str, None] = '', db: Session = Depends(get_db)) -> Page[Patient]:
    if hx_request:
        return templates.TemplateResponse(
            request=request, name="patients_list_table.html",
            context={
                "patients": paginate(db,
                                select(Patient)
                                .where(or_(Patient.lastname.ilike(f'%{search}%'), Patient.firstname.ilike(f'%{search}%')))
                                .order_by(Patient.lastname, Patient.firstname)
                            ),
                "search": search
            }
        )
    return templates.TemplateResponse(
        request=request, name="patients_list_full.html",
        context={
            "patients": paginate(db,
                            select(Patient)
                            .where(or_(Patient.lastname.ilike(f'%{search}%'), Patient.firstname.ilike(f'%{search}%')))
                            .order_by(Patient.lastname, Patient.firstname)
                        ),
            "search": search
        }
    )

def get_patient(db: Session, patient_id: UUID):
    return db.query(Patient).filter(Patient.id == patient_id).first()

@router.get("/{patient_id}/form.html", response_class=HTMLResponse)
async def get_patient_form(request: Request, patient_id: UUID, db: Session = Depends(get_db)):
    return templates.TemplateResponse(
        request=request, name="patients_form.html", context={"patient": get_patient(db, patient_id)}
    )


@router.post("/{patient_id}", response_class=HTMLResponse)
async def update_patient(request: Request, patient_id: UUID, firstname: Annotated[str, Form()], lastname: Annotated[str, Form()], db: Session = Depends(get_db)):
    patient = get_patient(db, patient_id)
    patient.firstname = firstname
    patient.lastname = lastname
    db.merge(patient)
    db.commit()
    return RedirectResponse(
        '/patients/list.html?page=1&size=10', 
        status_code=status.HTTP_302_FOUND)

# delete
@router.get("/{patient_id}/delete-confirm.html", response_class=HTMLResponse)
async def delete_patient_confirm(request: Request, patient_id: UUID, db: Session = Depends(get_db)) -> Page[Patient]:
    return templates.TemplateResponse(
        request=request, name="patients_delete.html", context={"patient": get_patient(db, patient_id)}
    )
    
@router.post("/{patient_id}/delete", response_class=HTMLResponse)
async def delete_patient(request: Request, patient_id: UUID, db: Session = Depends(get_db)) -> Page[Patient]:
    patient = get_patient(db, patient_id)
    db.delete(patient)
    db.commit()
    return RedirectResponse(
        '/patients/list.html?page=1&size=10', 
        status_code=status.HTTP_302_FOUND)