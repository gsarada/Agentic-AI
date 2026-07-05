from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database.connection import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    measurements: Mapped["UserMeasurements | None"] = relationship(back_populates="user", uselist=False)
    preferences: Mapped["UserPreferences | None"] = relationship(back_populates="user", uselist=False)
    images: Mapped[list["UserImage"]] = relationship(back_populates="user")
    recommendations: Mapped[list["Recommendation"]] = relationship(back_populates="user")
    generated_images: Mapped[list["GeneratedImage"]] = relationship(back_populates="user")
    chat_messages: Mapped[list["ChatMessage"]] = relationship(back_populates="user")


class UserMeasurements(Base):
    __tablename__ = "user_measurements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, nullable=False)
    height: Mapped[float | None] = mapped_column(nullable=True)
    weight: Mapped[float | None] = mapped_column(nullable=True)
    gender: Mapped[str | None] = mapped_column(String(50), nullable=True)
    age: Mapped[int | None] = mapped_column(Integer, nullable=True)
    chest: Mapped[float | None] = mapped_column(nullable=True)
    waist: Mapped[float | None] = mapped_column(nullable=True)
    hip: Mapped[float | None] = mapped_column(nullable=True)
    shoulder_width: Mapped[float | None] = mapped_column(nullable=True)
    sleeve_length: Mapped[float | None] = mapped_column(nullable=True)
    leg_length: Mapped[float | None] = mapped_column(nullable=True)
    inseam: Mapped[float | None] = mapped_column(nullable=True)
    neck: Mapped[float | None] = mapped_column(nullable=True)
    shoe_size: Mapped[float | None] = mapped_column(nullable=True)

    user: Mapped["User"] = relationship(back_populates="measurements")


class UserPreferences(Base):
    __tablename__ = "user_preferences"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, nullable=False)
    preferred_fit: Mapped[str | None] = mapped_column(String(100), nullable=True)
    preferred_colors: Mapped[str | None] = mapped_column(Text, nullable=True)
    preferred_fabrics: Mapped[str | None] = mapped_column(Text, nullable=True)
    budget: Mapped[float | None] = mapped_column(nullable=True)
    favorite_brands: Mapped[str | None] = mapped_column(Text, nullable=True)
    preferred_occasions: Mapped[str | None] = mapped_column(Text, nullable=True)

    user: Mapped["User"] = relationship(back_populates="preferences")


class UserImage(Base):
    __tablename__ = "user_images"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    image_type: Mapped[str] = mapped_column(String(20), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="images")
