from pydantic import BaseModel, EmailStr


class AuthSuccessfulResponse(BaseModel):
    """ Ожидаемая модель ответа для успешной авторизации """
    access_token: str = None
    refresh_token: str = None
