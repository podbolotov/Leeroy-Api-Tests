from typing import Literal

from pydantic import BaseModel, ConfigDict, field_validator
from models.default_error import DefaultError


class StringResources:
    USER_NOT_FOUND = f"User with email %s is not found or password is incorrect"
    PASSWORD_IS_INCORRECT = USER_NOT_FOUND


class AuthUnauthorizedError(DefaultError):
    """ Универсальный ответ, возвращаемый в случае невозможности найти пользователя или в случае, если передан
    некорректный пароль. """
    model_config = ConfigDict(extra="forbid")
    status: Literal["UNAUTHORIZED"]
    description: str


class AuthSuccessfulResponse(BaseModel):
    """ Ожидаемая модель ответа для успешной авторизации """
    model_config = ConfigDict(extra="forbid")

    access_token: str
    refresh_token: str
