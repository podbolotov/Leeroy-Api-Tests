from uuid import UUID

from database.db_baseclass import Database
from models.users import DatabaseUserDataModel
from data.framework_variables import FrameworkVariables as FrVars


def get_user_data_by_email(db: Database, email: str) -> DatabaseUserDataModel | None:
    db_result = db.execute_db_request(
        query='SELECT * from public.users WHERE email = %s;',
        params=(email,),
        fetchmode='one'
    )
    if db_result is not None:
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
    else:
        return None

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


def get_all_administrators_ids(db: Database, mode: str | None = None) -> tuple:

    if mode == 'except_default':
        sql_query = "SELECT id FROM public.users WHERE is_admin = 'true' AND email != %s "
        sql_params=(str(FrVars.APP_DEFAULT_USER_EMAIL),)
    else:
        sql_query = "SELECT id FROM public.users WHERE is_admin = 'true'"
        sql_params = None

    db_result = db.execute_db_request(
        query=sql_query,
        params=sql_params,
        fetchmode='all'
    )
    ids_list = []
    for row in db_result:
        ids_list.append(row[0])
    return tuple(ids_list)

def get_all_nonadmin_users_ids(db: Database) -> tuple:

    sql_query = "SELECT id FROM public.users WHERE is_admin = 'false'"

    db_result = db.execute_db_request(
        query=sql_query,
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


def get_users_count(db: Database, mode: str = 'email_distinct') -> int:
    if mode == 'email_distinct':
        sql_query = "SELECT DISTINCT email FROM public.users;"
    elif mode == 'table_count':
        sql_query = "SELECT count(*) FROM public.users;"
    else:
        raise ValueError("Unexpected mode value!")

    db_result = db.execute_db_request(
        query=sql_query,
        fetchmode='all'
    )

    if mode == 'email_distinct':
        users_count = len(db_result)
    else:
        users_count = int(db_result[0][0])

    return users_count