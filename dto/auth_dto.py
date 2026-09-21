import re

from pydantic import BaseModel, ConfigDict, field_validator
from pydantic.alias_generators import to_camel

PASSWORD_PATTERN = re.compile(r"^(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).{8,}$")


class CamelModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class RegisterRequestDTO(CamelModel):
    email: str
    password: str
    display_name: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        if not PASSWORD_PATTERN.match(value):
            raise ValueError(
                "Password must be at least 8 characters and include an "
                "uppercase letter, a number, and a special character."
            )
        return value


class LoginRequestDTO(CamelModel):
    email: str
    password: str


class RefreshRequestDTO(CamelModel):
    refresh_token: str


class AuthResponseDTO(CamelModel):
    user_id: str
    token: str
    expires_in: int


class RefreshResponseDTO(CamelModel):
    token: str
    expires_in: int


class MeResponseDTO(CamelModel):
    user_id: str
    email: str
    display_name: str | None
    created_at: str
