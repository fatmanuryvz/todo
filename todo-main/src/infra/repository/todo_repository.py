from database import SessionLocal
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import select
from src.infra.repository.entities.todo_entity import Todo
from pydantic import BaseModel
from typing import List, Optional

class TodoRepository:
    def __init__(self, db: Session):
        self.db = db

    def all(self) -> List[Todo]:
        query = select(Todo)
        result = self.db.execute(query)
        rows = result.scalars().all()
        return [self.to_model(row, Todo) for row in rows]

    def get(self, todo_id: int) -> Optional[Todo]:
        query = select(Todo).where(Todo.id == todo_id)
        result = self.db.execute(query)
        row = result.scalars().first()
        return self.to_model(row, Todo) if row else None

    def get_by_owner(self, owner_email: str) -> List[Todo]:
        query = select(Todo).where(Todo.owner_email == owner_email)
        result = self.db.execute(query)
        rows = result.scalars().all()
        return [self.to_model(row, Todo) for row in rows]

    def create(self, todo_data: Todo) -> Todo:
        new_todo = Todo(
            title=todo_data.title,
            description=todo_data.description,
            owner_email=todo_data.owner_email,
            created_at=datetime.utcnow()
        )
        self.db.add(new_todo)
        self.db.commit()
        self.db.refresh(new_todo)
        return self.to_model(new_todo, Todo)

    def delete(self, todo_id: int) -> Optional[Todo]:
        query = select(Todo).where(Todo.id == todo_id)
        result = self.db.execute(query)
        todo = result.scalars().first()
        if not todo:
            return None
        self.db.delete(todo)
        self.db.commit()
        return self.to_model(todo, Todo)
    
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
