from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from passlib.context import CryptContext

from src.infra.repository.entities.user_entity import User
from src.infra.repository.user_repository import UserRepository, get_db

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(data: dict) -> str:
    import jwt
    from src.infra.config.app_config import SECRET_KEY, ALGORITHM
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
class UserService:
    def __init__(self, db: Session = Depends(get_db)):
        self.user_repository = UserRepository(db)

    def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Belirtilen e-mail adresine sahip kullanıcıyı döndürür.
        Eğer kullanıcı bulunamazsa 404 hatası fırlatır.
        """
        user = self.user_repository.get_by_email(email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Kullanıcı bulunamadı"
            )
        return user

    def create_user(self, email: str, password: str) -> User:
        """
        Yeni kullanıcı oluşturur.
        E-mail adresi daha önceden kayıtlı ise 400 hatası döner.
        Parola bcrypt ile hash'lenir.
        """
        if self.user_repository.get_by_email(email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Bu e-mail adresi ile kayıtlı kullanıcı zaten mevcut"
            )
        hashed_password = pwd_context.hash(password)
        # User modelinin yapısına uygun şekilde nesne oluşturuyoruz
        user_data = User(email=email, hashed_password=hashed_password)
        return self.user_repository.create(user_data)

    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """
        Girilen e-mail ve parola bilgilerine göre kullanıcıyı doğrular.
        E-mail ya da parola yanlışsa None döner.
        """
        user = self.user_repository.get_by_email(email)
        if not user:
            return None
        if not pwd_context.verify(password, user.hashed_password):
            return None
        return user

    def get_current_user(self, token: str) -> User:
        """
        Token bilgisine göre mevcut kullanıcıyı döndürür.
        Token doğrulanamazsa ilgili hata fırlatılır.
        """
        # Repository içerisindeki statik method kullanılıyor
        return self.user_repository.get_current_user_db(token, self.user_repository.db)
