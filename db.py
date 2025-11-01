from datetime import datetime
from typing import Generator

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, create_engine, UniqueConstraint
from sqlalchemy.orm import declarative_base, sessionmaker, Session

# SQLite database in project root
SQLALCHEMY_DATABASE_URL = "sqlite:///./app.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},  # needed for SQLite with threads
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint("username", name="uq_users_username"),
        UniqueConstraint("email", name="uq_users_email"),
    )

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(150), nullable=False, index=True)
    email = Column(String(255), nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class UserVerification(Base):
    __tablename__ = "user_verification"

    user_id = Column(Integer, primary_key=True, index=True)
    verified = Column(Boolean, default=False, nullable=False)
    code_hash = Column(String(255), nullable=True)
    expires_at = Column(DateTime, nullable=True)
    last_sent_at = Column(DateTime, nullable=True)


class UserPasswordReset(Base):
    __tablename__ = "user_password_reset"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    used = Column(Boolean, default=False, nullable=False)
    code_hash = Column(String(255), nullable=True)
    expires_at = Column(DateTime, nullable=True)
    last_sent_at = Column(DateTime, nullable=True)


def init_db() -> None:
    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
