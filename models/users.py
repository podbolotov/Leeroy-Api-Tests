import uuid
from typing import Literal, Annotated
from uuid import UUID

from pydantic import BaseModel, EmailStr


class DatabaseUserDataModel(BaseModel):
    """
    Модель для получения данных по пользователю из БД.
    """
    id: UUID
    """ UUIDv4-идентификатор пользователя"""
    firstname: str
    """ Имя пользователя"""
    middlename: str | None
    """ Отчество пользователя (при наличии)"""
    surname: str
    """ Фамилия пользователя """
    email: EmailStr
    """ Адрес электронной почты пользователя """
    hashed_password: str
    """ Хэш пароля пользователя """
    is_admin: bool
    """ Признак прав администратора у пользователя """


class CreateUserSuccessfulResponse(BaseModel):
    """ Ожидаемая модель ответа при успешном создании пользователя """
    status: Literal["User successfully created"]
    user_id: UUID
