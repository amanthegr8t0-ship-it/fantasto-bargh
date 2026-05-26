import pymysql
from sqlalchemy import create_engine, Column, String, DateTime
from sqlalchemy.orm import declarative_base
from core.config import DB_URL
from sqlalchemy.orm import sessionmaker

Base = declarative_base()
class Job(Base):
    __tablename__ = "jobs"

    job_id= Column(String(36), primary_key=True)
    status = Column(String(50))
    error_message = Column(String(500))
    audio_path = Column(String(500))
    created_at = Column(DateTime)
    completed_at = Column(DateTime)

engine = create_engine(DB_URL,
        pool_pre_ping=True,
        pool_recycle=3600)
SessionLocal = sessionmaker(bind=engine)
Base.metadata.create_all(engine)
