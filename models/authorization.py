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

class AccessTokenErrorTokenBadSignature(DefaultError):
    """ Ожидаемый ответ при попытке передачи токена доступа с некорректной подписью. """
    status: Literal["TOKEN_BAD_SIGNATURE"]
    description: Literal["Access-Token has incorrect signature"]

class AccessTokenErrorTokenMalformed(DefaultError):
    """ Ожидаемый ответ при попытке передачи повреждённого токена доступа, либо случайных данных не являющимися
    корректным JWT-токеном. """
    status: Literal["TOKEN_MALFORMED"]
    description: Literal["Access-Token is malformed or has incorrect format"]

class AccessTokenErrorTokenExpired(DefaultError):
    """ Ожидаемый ответ при попытке передачи токена доступа, срок действия которого истёк. """
    status: Literal["TOKEN_EXPIRED"]
    description: Literal["Provided Access-Token is expired"]

class AccessTokenErrorTokenNotFoundInDatabase(DefaultError):
    """ Ожидаемый ответ при попытке передачи токена доступа, запись о выпуске которого не удалось найти в БД. """
    status: Literal["TOKEN_NOT_FOUND"]
    description: Literal["Access-Token data is not found in database"]

class AccessTokenErrorTokenRevoked(DefaultError):
    """ Ожидаемый ответ при попытке передачи токена доступа, имеющего в записи о выпуске в БД признак отзыва. """
    status: Literal["TOKEN_REVOKED"]
    description: Literal["Access-Token is revoked"]

class AuthSuccessfulResponse(BaseModel):
    """ Ожидаемая модель ответа для успешной авторизации """
    model_config = ConfigDict(extra="forbid")

    access_token: str
    refresh_token: str
