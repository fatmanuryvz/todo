from datetime import datetime
from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
import redis
import json
from src.core.models.todo import TodoCreate, TodoResponse
from src.core.service.todo_service import TodoService
from src.core.service.user_service import UserService
from src.infra.repository.entities.user_entity import User
from src.infra.config.app_config import REDIS_HOST
from urllib.parse import urlparse

router = APIRouter(prefix="/todos", tags=["Todos"])

# Redis istemcisi oluşturuluyor.
parsed_url = urlparse(REDIS_HOST)
redis_client = redis.Redis(host=parsed_url.hostname, port=parsed_url.port, db=0, decode_responses=True)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme),
                     user_service: UserService = Depends()) -> User:
    """
    Gelen token bilgisini UserService içerisindeki get_current_user metodunu kullanarak doğrular.
    Eğer token geçersizse veya kullanıcı bulunamazsa, HTTP 401 hatası fırlatır.
    """
    return user_service.get_current_user(token)

@router.post("/", response_model=TodoResponse)
def create_todo(
    todo: TodoCreate,
    todo_service: TodoService = Depends(),
    current_user: User = Depends(get_current_user)
):
    """
    Yeni bir todo oluşturur. 
    Oluşturulacak todo'nun owner_email alanı, doğrulanmış kullanıcının email'ine ayarlanır.
    """
    # Servis katmanında todo oluşturma işlemini yapmadan önce owner_email güncelleniyor.
    todo.owner_email = current_user.email
    new_todo = todo_service.create_todo(todo)
    cache_key = f"todos:{current_user.email}"
    redis_client.delete(cache_key)
    return new_todo

@router.get("/", response_model=list[TodoResponse])
def get_todos(
    todo_service: TodoService = Depends(),
    current_user: User = Depends(get_current_user)
):
    """
    Kullanıcıya ait todo'ları döner. 
    Eğer Redis cache'de varsa, oradan okunur; yoksa veritabanından çekilip cache'e yazılır.
    """
    cache_key = f"todos:{current_user.email}"
    cached_todos = redis_client.get(cache_key)
    if cached_todos:
        # Cache'deki veriyi parse edip döndürüyoruz.
        return json.loads(cached_todos)

    # Servis katmanı üzerinden kullanıcıya ait todo'lar çekiliyor.
    todos = todo_service.get_todos_by_owner(current_user.email)
    # Cache'e yazmadan önce, SQLAlchemy modelinden JSON uyumlu yapılara çeviriyoruz.
    todos_serialized = [TodoResponse.model_validate(todo).model_dump() for todo in todos]
    json_data = json.dumps(todos_serialized, default=lambda o: o.isoformat() if isinstance(o, datetime) else o)
    redis_client.setex(cache_key, 300, json_data)
    return todos_serialized

@router.delete("/{todo_id}", response_model=TodoResponse)
def delete_todo(
    todo_id: int,
    todo_service: TodoService = Depends(),
    current_user: User = Depends(get_current_user)
):
    """
    Belirtilen ID'ye sahip todo öğesini siler. 
    Silme işleminden önce, todo'nun doğrulanmış kullanıcıya ait olup olmadığı kontrol edilir.
    """
    # Önce silinecek todo'yu servis üzerinden çekiyoruz
    todo = todo_service.get_todo(todo_id)
    if todo.owner_email != current_user.email:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bu todo öğesini silmeye yetkiniz yok."
        )
    deleted_todo = todo_service.delete_todo(todo_id)
    cache_key = f"todos:{current_user.email}"
    redis_client.delete(cache_key)
    return deleted_todo