from pydantic import BaseModel, EmailStr, Field


class RegisterForm(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=6, max_length=64)


class LoginForm(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=64)
