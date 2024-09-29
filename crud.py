from sqlmodel import Session, select
from security import verify_password

def get_user_by_username(session: Session, username: str):
    return session.exec(select(User).where(User.username == username)).first()

def authenticate_user(session: Session, username: str, password: str):
    user = get_user_by_username(session, username)
    if not user or not verify_password(password, user.hashed_password):
        return False
    return user