from datetime import datetime
from uuid import UUID

from database.db_baseclass import Database
from models.jwt import DatabaseAccessToken, DatabaseRefreshToken


def get_access_token_by_id(db: Database, token_id: UUID) -> DatabaseAccessToken:
    db_result = db.execute_db_request(
        query='SELECT * from public.access_tokens WHERE id = %s;',
        params=(str(token_id),),
        fetchmode='one'
    )
    token_data = DatabaseAccessToken(
        id=db_result[0],
        user_id=db_result[1],
        issued_at=db_result[2].isoformat(),
        expired_at=db_result[3].isoformat(),
        refresh_token_id=db_result[4],
        revoked=db_result[5]
    )
    return token_data


def get_refresh_token_by_id(db: Database, token_id: UUID) -> DatabaseRefreshToken:
    db_result = db.execute_db_request(
        query='SELECT * from public.refresh_tokens WHERE id = %s;',
        params=(str(token_id),),
        fetchmode='one'
    )
    token_data = DatabaseRefreshToken(
        id=db_result[0],
        user_id=db_result[1],
        issued_at=db_result[2].isoformat(),
        expired_at=db_result[3].isoformat(),
        access_token_id=db_result[4],
        revoked=db_result[5]
    )
    return token_data
