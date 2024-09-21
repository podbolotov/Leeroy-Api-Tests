from uuid import UUID

from database.db_baseclass import Database
from models.users import DatabaseUserDataModel


def get_user_data_by_email(db: Database, email: str) -> DatabaseUserDataModel:
    db_result = db.execute_db_request(
        query='SELECT * from public.users WHERE email = %s;',
        params=(email,),
        fetchmode='one'
    )
    user_data = DatabaseUserDataModel(
        id=db_result[0],
        firstname=db_result[1],
        middlename=db_result[2],
        surname=db_result[3],
        email=db_result[4],
        hashed_password=db_result[5],
        is_admin=db_result[6]
    )
    return user_data

# TODO: Необходимо оптимизировать методы запроса пользовательских данных и свести их в один,
#  с опциональным поиском по email или id.
def get_user_data_by_id(db: Database, user_id: UUID) -> DatabaseUserDataModel:
    db_result = db.execute_db_request(
        query='SELECT * from public.users WHERE id = %s;',
        params=(str(user_id),),
        fetchmode='one'
    )
    user_data = DatabaseUserDataModel(
        id=db_result[0],
        firstname=db_result[1],
        middlename=db_result[2],
        surname=db_result[3],
        email=db_result[4],
        hashed_password=db_result[5],
        is_admin=db_result[6]
    )
    return user_data