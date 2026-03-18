from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.src.infra.config.app_config import POSTGRES_DB, POSTGRES_IP, POSTGRES_PASSWORD, POSTGRES_PORT, POSTGRES_USERNAME

SQLALCHEMY_DATABASE_URL = f"postgresql://{POSTGRES_IP}:{POSTGRES_PORT}/{POSTGRES_DB}?user={POSTGRES_USERNAME}&password={POSTGRES_PASSWORD}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
