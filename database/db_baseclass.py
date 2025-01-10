import psycopg2
from psycopg2 import DatabaseError, extras
from data.framework_variables import FrameworkVariables as FrVars


class Database:
    """
    Данный класс включает в себя базовые операции с БД,
    такие как: установка подключения, создание БД при необходимости,
    сброс БД.
    """

    def __init__(self):
        self.connection = None
        self.cursor = None
        self.user = str(FrVars.DB_USER)
        self.password = str(FrVars.DB_PASSWORD)
        self.host = str(FrVars.DB_HOST)
        self.port = str(FrVars.DB_PORT)

    def connect_to_database(self):
        # Первым шагом происходит подключение к стандартной базе данных "postgres". Это необходимо для проверки
        # существования базы данных приложения "leeroy".
        self.connection = psycopg2.connect(
            dbname='postgres', user=self.user, password=self.password, host=self.host, port=self.port
        )
        # Регистрируем расширение для работы с нативным UUID
        psycopg2.extras.register_uuid()
        # Создаём курсор
        self.cursor = self.connection.cursor()
        # Проверяем существование базы данных "leeroy".
        self.cursor.execute('SELECT datname FROM pg_database WHERE datname = \'leeroy\'')
        leeroy_in_exist = self.cursor.fetchone()

        if leeroy_in_exist is None:
            raise DatabaseError("Database Leeroy is not exist!")
        else:
            self.connection.close()
            self.connection = psycopg2.connect(
                dbname='leeroy', user=self.user, password=self.password, host=self.host, port=self.port
            )
            self.cursor = self.connection.cursor(cursor_factory=extras.NamedTupleCursor)

    def execute_db_request(self, query: str, params: tuple = None, fetchmode: str = 'all'):
        self.cursor.execute(query, params)
        if fetchmode == 'all':
            result = self.cursor.fetchall()
        elif fetchmode == 'one':
            result = self.cursor.fetchone()
        elif fetchmode == 'nofetch':
            result = None
        else:
            raise DatabaseError("Unsupported fetch mode type!")
        return result

    def commit(self):
        self.connection.commit()