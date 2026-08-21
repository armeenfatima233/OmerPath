from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class SignUpRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)


class SignUpResponse(BaseModel):
    user_id: UUID
    email: EmailStr
    email_confirmation_required: bool
    message: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1, max_length=128)
    remember: bool = False


class LoginResponse(BaseModel):
    user_id: UUID
    email: EmailStr
    message: str


class CurrentUserResponse(BaseModel):
    user_id: UUID
    email: EmailStr
    first_name: str | None = None
    last_name: str | None = None
    nationality: str | None = None
    country_of_residence: str | None = None


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordUpdateRequest(BaseModel):
    password: str = Field(..., min_length=8, max_length=128)


class AuthCodeExchangeRequest(BaseModel):
    code: str = Field(..., min_length=1, max_length=2048)
