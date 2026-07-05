from pydantic import BaseModel, EmailStr, Field


class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str = Field(min_length=12)
    height: float | None = None
    weight: float | None = None
    gender: str | None = None
    age: int | None = None
    chest: float | None = None
    waist: float | None = None
    hip: float | None = None
    shoulder_width: float | None = None
    sleeve_length: float | None = None
    leg_length: float | None = None
    inseam: float | None = None
    neck: float | None = None
    shoe_size: float | None = None
    preferred_fit: str | None = None
    preferred_colors: list[str] = Field(default_factory=list)
    preferred_fabrics: list[str] = Field(default_factory=list)
    budget: float | None = None
    favorite_brands: list[str] = Field(default_factory=list)
    preferred_occasions: list[str] = Field(default_factory=list)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class MeasurementsSchema(BaseModel):
    height: float | None = None
    weight: float | None = None
    gender: str | None = None
    age: int | None = None
    chest: float | None = None
    waist: float | None = None
    hip: float | None = None
    shoulder_width: float | None = None
    sleeve_length: float | None = None
    leg_length: float | None = None
    inseam: float | None = None
    neck: float | None = None
    shoe_size: float | None = None


class PreferencesSchema(BaseModel):
    preferred_fit: str | None = None
    preferred_colors: list[str] = Field(default_factory=list)
    preferred_fabrics: list[str] = Field(default_factory=list)
    budget: float | None = None
    favorite_brands: list[str] = Field(default_factory=list)
    preferred_occasions: list[str] = Field(default_factory=list)


class UserImageSchema(BaseModel):
    image_type: str
    file_path: str
    uploaded_at: str | None = None


class ProfileResponse(BaseModel):
    id: int
    name: str
    email: str
    measurements: MeasurementsSchema
    preferences: PreferencesSchema
    images: list[UserImageSchema]


class ProfileUpdate(BaseModel):
    name: str | None = None
    measurements: MeasurementsSchema | None = None
    preferences: PreferencesSchema | None = None
