from database import SessionLocal
from fastapi import HTTPException, status
from jose import JWTError, jwt
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session
from src.infra.config.app_config import ALGORITHM, SECRET_KEY
from src.infra.repository.entities.user_entity import User
from typing import Optional

class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_email(self, email: str) -> Optional[User]:
        query = select(User).where(User.email == email)
        result = self.db.execute(query)
        row = result.scalars().first()
        return self.to_model(row, User) if row else None

    def create(self, user_data: User) -> User:
        new_user = User(
            email=user_data.email,
            hashed_password=user_data.hashed_password
        )
        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)
        return self.to_model(new_user, User)
    
    def get_current_user_db(self, token: str, db: Session) -> Optional[User]:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            email: str = payload.get("sub")
            if email is None:
                raise credentials_exception
        except JWTError:
            raise credentials_exception

        user = db.query(User).filter(User.email == email).first()
        if user is None:
            raise credentials_exception

        return self.to_model(user, User)

    def to_model(self, entity, model: BaseModel, allow_none: bool = True):
        if entity is None:
            if not allow_none:
                raise ValueError("Entity cannot be None")
            return None
        
        data = {column.name: getattr(entity, column.name) for column in entity.__table__.columns}
        return model(**data)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
