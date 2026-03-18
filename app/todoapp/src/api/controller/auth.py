from fastapi import APIRouter, Depends, HTTPException
from app.src.core.models.user import UserCreate, UserLogin, Token
from app.src.core.service.user_service import UserService, create_access_token

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=Token)
def register(user: UserCreate, user_service: UserService = Depends()):
    new_user = user_service.create_user(email=user.email, password=user.password)
    access_token = create_access_token(data={"sub": new_user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login", response_model=Token)
def login(user: UserLogin, user_service: UserService = Depends()):
    authenticated_user = user_service.authenticate_user(email=user.email, password=user.password)
    if not authenticated_user:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    access_token = create_access_token(data={"sub": authenticated_user.email})
    return {"access_token": access_token, "token_type": "bearer"}
