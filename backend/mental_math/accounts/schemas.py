from pydantic import BaseModel, EmailStr, Field


class Credentials(BaseModel):
    email: EmailStr
    password: str = Field(min_length=12, max_length=128)


class PasswordConfirmation(BaseModel):
    password: str = Field(min_length=1, max_length=128)


class SessionView(BaseModel):
    email: EmailStr | None
    csrf_token: str
