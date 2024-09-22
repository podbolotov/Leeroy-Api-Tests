from uuid import UUID

from database.db_baseclass import Database
from models.users import DatabaseUserDataModel
from data.framework_variables import FrameworkVariables as FrVars


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


def get_all_administrators_ids_except_default(db: Database) -> tuple:
    db_result = db.execute_db_request(
        query='''
        SELECT id FROM public.users WHERE is_admin = 'true' AND email != %s
        ''',
        params=(str(FrVars.APP_DEFAULT_USER_EMAIL),),
        fetchmode='all'
    )
    ids_list = []
    for row in db_result:
        ids_list.append(row[0])
    return tuple(ids_list)


def bulk_change_administrator_permissions(db: Database, ids: tuple[UUID], is_admin: bool):
    if len(ids) >= 1:
        db.execute_db_request(
        query='''
            UPDATE public.users 
            SET is_admin = %s 
            WHERE id in %s
            ''',
        params=(is_admin,ids),
        fetchmode='nofetch'
        )
        db.commit()
    else:
        pass