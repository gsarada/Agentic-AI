from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from sqlalchemy.orm import Session

from backend.config import get_settings
from backend.models.user import User, UserMeasurements, UserPreferences
from backend.schemas.user import ProfileResponse, ProfileUpdate, UserRegister
from backend.utils.llm import deserialize_list, serialize_list

import bcrypt

ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def create_access_token(user_id: int) -> str:
    settings = get_settings()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {"sub": str(user_id), "exp": expire}
    return jwt.encode(payload, settings.secret_key, algorithm=ALGORITHM)


def decode_token(token: str) -> int | None:
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
        return int(payload.get("sub", 0))
    except (JWTError, ValueError):
        return None


def register_user(db: Session, data: UserRegister) -> User:
    if db.query(User).filter(User.email == data.email).first():
        raise ValueError("Email already registered")

    user = User(
        name=data.name,
        email=data.email,
        password_hash=hash_password(data.password),
    )
    db.add(user)
    db.flush()

    measurements = UserMeasurements(
        user_id=user.id,
        height=data.height,
        weight=data.weight,
        gender=data.gender,
        age=data.age,
        chest=data.chest,
        waist=data.waist,
        hip=data.hip,
        shoulder_width=data.shoulder_width,
        sleeve_length=data.sleeve_length,
        leg_length=data.leg_length,
        inseam=data.inseam,
        neck=data.neck,
        shoe_size=data.shoe_size,
    )
    preferences = UserPreferences(
        user_id=user.id,
        preferred_fit=data.preferred_fit,
        preferred_colors=serialize_list(data.preferred_colors),
        preferred_fabrics=serialize_list(data.preferred_fabrics),
        budget=data.budget,
        favorite_brands=serialize_list(data.favorite_brands),
        preferred_occasions=serialize_list(data.preferred_occasions),
    )
    db.add(measurements)
    db.add(preferences)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.password_hash):
        return None
    return user


def build_profile_response(user: User) -> ProfileResponse:
    m = user.measurements
    p = user.preferences
    return ProfileResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        measurements={
            "height": m.height if m else None,
            "weight": m.weight if m else None,
            "gender": m.gender if m else None,
            "age": m.age if m else None,
            "chest": m.chest if m else None,
            "waist": m.waist if m else None,
            "hip": m.hip if m else None,
            "shoulder_width": m.shoulder_width if m else None,
            "sleeve_length": m.sleeve_length if m else None,
            "leg_length": m.leg_length if m else None,
            "inseam": m.inseam if m else None,
            "neck": m.neck if m else None,
            "shoe_size": m.shoe_size if m else None,
        },
        preferences={
            "preferred_fit": p.preferred_fit if p else None,
            "preferred_colors": deserialize_list(p.preferred_colors if p else None),
            "preferred_fabrics": deserialize_list(p.preferred_fabrics if p else None),
            "budget": p.budget if p else None,
            "favorite_brands": deserialize_list(p.favorite_brands if p else None),
            "preferred_occasions": deserialize_list(p.preferred_occasions if p else None),
        },
        images=[
            {
                "image_type": img.image_type,
                "file_path": img.file_path,
                "uploaded_at": img.uploaded_at.isoformat() if img.uploaded_at else None,
            }
            for img in user.images
        ],
    )


def update_profile(db: Session, user: User, data: ProfileUpdate) -> User:
    if data.name:
        user.name = data.name
    if data.measurements:
        m = user.measurements or UserMeasurements(user_id=user.id)
        for field, value in data.measurements.model_dump(exclude_unset=True).items():
            setattr(m, field, value)
        db.add(m)
    if data.preferences:
        p = user.preferences or UserPreferences(user_id=user.id)
        payload = data.preferences.model_dump(exclude_unset=True)
        for field, value in payload.items():
            if field in {"preferred_colors", "preferred_fabrics", "favorite_brands", "preferred_occasions"}:
                setattr(p, field, serialize_list(value))
            else:
                setattr(p, field, value)
        db.add(p)
    db.commit()
    db.refresh(user)
    return user
