from uuid import UUID
from pydantic import BaseModel


class DecodedJsonWebToken(BaseModel):
    id: UUID
    user_id: UUID
    issued_at: str
    expired_at: str


class DatabaseAccessToken(BaseModel):
    id: UUID
    user_id: UUID
    issued_at: str
    expired_at: str
    refresh_token_id: UUID
    revoked: bool


class DatabaseRefreshToken(BaseModel):
    id: UUID
    user_id: UUID
    issued_at: str
    expired_at: str
    access_token_id: UUID
    revoked: bool
