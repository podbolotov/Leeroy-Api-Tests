from typing import Literal
from uuid import UUID

from pydantic import BaseModel


class DatabaseBookDataModel(BaseModel):
    """
    Модель для получения данных по книге из БД.
    """
    id: UUID
    """ ID книги """
    title: str
    """ Заголовок (название) книги """
    author: str
    """ Автор (или авторы) книги """
    isbn: str
    """ ISBN книги (10 или 13 символов) """


class DeleteBookSuccessfulResponse(BaseModel):
    """ Ожидаемая модель ответа при успешном удалении книги """
    status: Literal["Book successfully deleted"]


class CreateBookSuccessfulResponse(BaseModel):
    """ Ожидаемая модель ответа при успешном создании книги """
    status: Literal["Book successfully added"]
    book_id: UUID
