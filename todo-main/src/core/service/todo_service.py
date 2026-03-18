from fastapi import HTTPException, status, Depends
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List

from src.infra.repository.todo_repository import TodoRepository, get_db
from src.infra.repository.user_repository import UserRepository
from src.infra.repository.entities.todo_entity import Todo
from src.core.models.todo import TodoCreate

class TodoService:
    def __init__(self, db: Session = Depends(get_db)):
        self.repo = TodoRepository(db)
        self.user_repo = UserRepository(db)

    def list_todos(self) -> List[Todo]:
        return self.repo.all()

    def get_todo(self, todo_id: int) -> Todo:
        todo = self.repo.get(todo_id)
        if not todo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Todo not found"
            )
        return todo

    def get_todos_by_owner(self, owner_email: str) -> List[Todo]:
        return self.repo.get_by_owner(owner_email)

    def create_todo(self, todo_data: TodoCreate) -> Todo:
        new_todo = Todo(
            title=todo_data.title,
            description=todo_data.description,
            owner_email=todo_data.owner_email,
            created_at=datetime.utcnow()
        )
        return self.repo.create(new_todo)

    def delete_todo(self, todo_id: int) -> Todo:
        deleted_todo = self.repo.delete(todo_id)
        if not deleted_todo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Todo not found"
            )
        return deleted_todo