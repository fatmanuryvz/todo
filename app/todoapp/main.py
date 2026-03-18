from src.core.models import Base
from database import Base, engine
from fastapi import FastAPI
from src.api.controller import todo
from src.api.controller import auth

Base.metadata.create_all(bind=engine)
app = FastAPI()
app.include_router(auth.router)
app.include_router(todo.router)