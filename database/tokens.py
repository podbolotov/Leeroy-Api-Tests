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


def change_jwt_token_revoke_status(
        db: Database,
        token_id: UUID,
        new_value: bool,
        token_type: str = 'access_token'
) -> bool:
    """
    Данный метод реализует изменение статуса отзыва токена (как токена доступа, так и токена обновления) в базе данных.

    :param db: Экземпляр класса Database, предоставляющий подключение и методы взаимодействия с БД.
    :param token_id: UUIDv4 идентификатор токена, статус отзыва которого необходимо изменить.
    :param new_value: Желаемое значение статуса отзыва токена (True - токен отозван, False - токен не отозван).
    :param token_type: Тип токена ("access_token" или "refresh_token")
    :return: При отсутствии явных ошибок при исполнении запроса функция возвращает булево значение True.
    :raises RuntimeError: Исключение, возвращаемое в случае, если при попытке изменения статуса отзыва токена произошла
        ошибка.
    """

    try:
        if token_type == 'access_token':

            db.execute_db_request(
                query="UPDATE public.access_tokens SET revoked = %s::boolean WHERE id = %s;",
                params=(str(new_value), str(token_id),),
                fetchmode='nofetch'
            )
            db.commit()

        elif token_type == 'refresh_token':

            db.execute_db_request(
                query="UPDATE public.refresh_tokens SET revoked = %s::boolean WHERE id = %s;",
                params=(str(new_value), str(token_id),),
                fetchmode='nofetch'
            )
            db.commit()

        else:
            raise ValueError("Unsupported token type")

        return True

    except Exception as e:
        raise RuntimeError(f'Token revoke status changing is failed!\n{e}')


def get_tokens_count(db: Database, user_id: UUID, token_type: str = 'access_token') -> int:
    if token_type == 'access_token':
        db_result = db.execute_db_request(
            query="SELECT count(*) FROM public.access_tokens WHERE user_id = %s;",
            params=(str(user_id),),
            fetchmode='one'
        )
    elif token_type == 'refresh_token':
        db_result = db.execute_db_request(
            query="SELECT count(*) FROM public.access_tokens WHERE user_id = %s;",
            params=(str(user_id),),
            fetchmode='one'
        )
    else:
        raise ValueError("Unexpected mode value!")

    user_tokens_count = db_result[0]

    return user_tokens_count
