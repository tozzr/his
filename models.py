from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from enum import Enum

class RoleEnum(str, Enum):
    admin = "admin"
    hr = "hr"
    doctor = "doctor"
    patient = "patient"
    
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True)
    hashed_password: str
    role: RoleEnum