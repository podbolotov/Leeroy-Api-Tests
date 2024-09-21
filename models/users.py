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

class CreatedUserDataBundle(BaseModel):
    """
    Набор данных регистрируемого пользователя.
    Модель предназначена для возвращения данных регистрируемого пользователя фикстурой регистрации (при успехе запроса
    на регистрацию).
    """
    user_id: UUID
    """ UUIDv4-идентификатор пользователя"""
    email: EmailStr
    """ Адрес электронной почты пользователя """
    firstname: str
    """ Имя пользователя"""
    middlename: str | None
    """ Отчество или среднее имя пользователя (при наличии)"""
    password: str
    """ Пароль пользователя (в исходном виде) """
    surname: str
    """ Фамилия пользователя """


class CreateUserSuccessfulResponse(BaseModel):
    """ Ожидаемая модель ответа при успешном создании пользователя """
    status: Literal["User successfully created"]
    user_id: UUID

class UserPermissionsChangeSuccessfulResponse(BaseModel):
    """ Ожидаемая модель ответа при успешном изменении уровня прав пользователя """
    status: str
    is_admin: bool

class DeleteUserSuccessfulResponse(BaseModel):
    """ Ожидаемая модель ответа при успешном удалении пользователя """
    status: Literal["User successfully deleted"]
