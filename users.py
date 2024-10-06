from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID as UUIDSql
from sqlalchemy.orm import Session
from uuid import uuid4

from database import Base, get_db

class User(Base):
    __tablename__ = "users"
    id = Column(UUIDSql(as_uuid=True), primary_key=True, default=uuid4)
    username = Column(String, index=True)
    email = Column(String, index=True)
    password = Column(String, index=True)
    
def get_user_by_id(db: Session, id: int) -> User | None:
    """
    Get user by id
    Args:
        db (Session): database session
        id (int): user id
    Returns:
        User | None: user object if user exists, None otherwise (if user does not exist in the database, return None)
    """
    user = db.query(User).filter(User.id == id).first()
    if not user:
        return None
    return user  

def get_user(db: Session, username: str) -> User | None:
    """
    Get user by email
    Args:
        db (Session): database session
        email (str): user email
    Returns:
        User | None: user object if user exists, None otherwise.
    """
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return None
    return user