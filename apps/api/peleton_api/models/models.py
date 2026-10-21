from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import relationship

from peleton_api.core.database import Base


class Company(Base):
    __tablename__ = "company"

    id = Column(Integer, primary_key=True, index=True)
    org_number = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    postal_code = Column(String, nullable=True)
    company_type = Column(String, nullable=True)
    company_category = Column(String, nullable=True)
    show_name_consent = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    users = relationship("User", back_populates="company")


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    auth_user_id = Column(String, unique=True, nullable=True)
    email = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=True)
    company_email = Column(String, nullable=True)
    verified_company = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    company_id = Column(Integer, ForeignKey("company.id", ondelete="SET NULL"), nullable=True)
    company = relationship("Company", back_populates="users")
    strava_connection = relationship("StravaConnection", back_populates="user", uselist=False)


class StravaConnection(Base):
    __tablename__ = "strava_connection"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), unique=True, nullable=False)
    athlete_id = Column(String, unique=True, nullable=False)
    access_token_ciphertext = Column(Text, nullable=False)
    access_token_iv = Column(String(24), nullable=False)
    access_token_tag = Column(String(24), nullable=False)
    refresh_token_ciphertext = Column(Text, nullable=False)
    refresh_token_iv = Column(String(24), nullable=False)
    refresh_token_tag = Column(String(24), nullable=False)
    scopes = Column(Text, nullable=False)
    token_expires_at = Column(DateTime(timezone=True), nullable=False)
    connected_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="strava_connection")