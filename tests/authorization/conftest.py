import random
import uuid

import allure
import jwt
import pytest
from faker import Faker
from data.framework_variables import FrameworkVariables as FrVars
from database.tokens import change_jwt_token_revoke_status
from helpers.jwt_tools import validate_and_decode_token

fake = Faker()


class RandomEndpointData:
    """
    Данный класс представляет собой модель, представляющую набор данных эндпоинта.
    """

    def __init__(self, method: str, url: str, json: dict | None):
        # Метод обращения к эндпоинту в формате строки
        self.method = method
        # URL эндпоинта в формате строки
        self.url = url
        # Опциональное тело эндпоинта в формате словаря
        self.json = json


@pytest.fixture(scope="class")
def get_random_endpoint_data() -> RandomEndpointData:
    """
    Данная фикстура возвращает данные одного из эндпоинтов, требующих передачи токена доступа.
    Эндпоинт выбирается из списка, заранее определённого в коде фикстуры.

    :return: Данные эндпоинта в соответствии с моделью RandomEndpointData.
    """
    random_endpoint_data = random.choice([
        RandomEndpointData(  # Запрос на создание пользователя
            method="POST",
            url=FrVars.APP_HOST + "/v1/users",
            json={
                "email": fake.email(),
                "firstname": fake.first_name(),
                "middlename": random.choice([fake.first_name(), None]),
                "surname": fake.last_name(),
                "password": fake.password()
            }
        ),
        RandomEndpointData(  # Запрос на получение информации пользователем о себе
            method="GET",
            url=FrVars.APP_HOST + "/v1/users/me",
            json=None
        )

    ])

    allure.attach(
        f"Method: {random_endpoint_data.method}\n"
        f"URL: {random_endpoint_data.url}\n"
        f"Body: {random_endpoint_data.json}",
        "Данные случайного запроса"
    )

    return random_endpoint_data


@pytest.fixture(scope="function")
def make_access_token_with_incorrect_signature(create_and_authorize_user) -> str:
    """
    Данная фикстура переподписывает корректный токен доступа, полученный при авторизации пользователя, при помощи
    заведомо некорректной подписи.

    :param create_and_authorize_user: Ссылка на фикстуру создания и авторизации пользователя.
    :return: JWT-токен доступа с корректным форматом, но некорректной подписью.
    """
    random_incorrect_signature = str(uuid.uuid4().hex)
    initial_correct_access_token = create_and_authorize_user.access_token
    decoded_access_token = validate_and_decode_token(initial_correct_access_token)
    token_payload = {
        "id": str(decoded_access_token.id),
        "user_id": str(decoded_access_token.user_id),
        "issued_at": str(decoded_access_token.issued_at),
        "expired_at": str(decoded_access_token.expired_at)
    }

    resigned_access_token_with_incorrect_signature = jwt.encode(
        token_payload,
        random_incorrect_signature,
        algorithm="HS256"
    )

    allure.attach(create_and_authorize_user.access_token, "Изначальный токен доступа")
    allure.attach(random_incorrect_signature, "Использованная некорректная подпись")
    allure.attach(resigned_access_token_with_incorrect_signature, "Токен доступа, подписанный некорректной подписью")

    return resigned_access_token_with_incorrect_signature

@pytest.fixture(scope="function")
def make_refresh_token_with_incorrect_signature(create_and_authorize_user) -> str:
    """
    Данная фикстура переподписывает корректный токен обновления, полученный при авторизации пользователя, при помощи
    заведомо некорректной подписи.

    :param create_and_authorize_user: Ссылка на фикстуру создания и авторизации пользователя.
    :return: JWT-токен обновления с корректным форматом, но некорректной подписью.
    """
    random_incorrect_signature = str(uuid.uuid4().hex)
    initial_correct_refresh_token = create_and_authorize_user.refresh_token
    decoded_refresh_token = validate_and_decode_token(initial_correct_refresh_token)
    token_payload = {
        "id": str(decoded_refresh_token.id),
        "user_id": str(decoded_refresh_token.user_id),
        "issued_at": str(decoded_refresh_token.issued_at),
        "expired_at": str(decoded_refresh_token.expired_at)
    }

    resigned_refresh_token_with_incorrect_signature = jwt.encode(
        token_payload,
        random_incorrect_signature,
        algorithm="HS256"
    )

    allure.attach(create_and_authorize_user.refresh_token, "Изначальный токен обновления")
    allure.attach(random_incorrect_signature, "Использованная некорректная подпись")
    allure.attach(
        resigned_refresh_token_with_incorrect_signature, "Токен обновления, подписанный некорректной подписью"
    )

    return resigned_refresh_token_with_incorrect_signature


@pytest.fixture(scope="function")
def make_malformed_jwt_token() -> str:
    """
    Данная фикстура генерирует строку, визуально напоминающую JWT-токен, но не являющуюся им.
    :return: Заведомо некорректный JWT-токен.
    """
    malformed_access_token = f"{str(uuid.uuid4().hex)}.{str(uuid.uuid4().hex)}.{str(uuid.uuid4().hex)}"
    allure.attach(malformed_access_token, "Заведомо некорректный токен доступа")
    return malformed_access_token


@pytest.fixture(scope="function")
def make_expired_access_token(create_and_authorize_user) -> str:
    """
    Данная фикстура меняет значение времени истечения в JWT-токене таким образом, чтобы он считался истёкшим.
    :param create_and_authorize_user: Ссылка на фикстуру создания и авторизации пользователя.
    :return: Корректный JWT-токен с изменённым временем истечения.
    """
    initial_correct_access_token = create_and_authorize_user.access_token
    decoded_access_token = validate_and_decode_token(initial_correct_access_token)
    token_payload = {
        "id": str(decoded_access_token.id),
        "user_id": str(decoded_access_token.user_id),
        "issued_at": str(decoded_access_token.issued_at),
        "expired_at": str(decoded_access_token.issued_at)  # в качестве времени истечения присваивается время выпуска
    }

    resigned_access_token_with_modified_expired_at_time = jwt.encode(
        token_payload,
        FrVars.JWT_SIGNATURE_SECRET,
        algorithm="HS256"
    )

    allure.attach(create_and_authorize_user.access_token, "Изначальный токен доступа")
    allure.attach(token_payload['expired_at'], "Новое время истечения для переподписанного токена")
    allure.attach(resigned_access_token_with_modified_expired_at_time, "Токен доступа, c изменённым временем выпуска")

    return resigned_access_token_with_modified_expired_at_time


@pytest.fixture(scope="function")
def make_expired_refresh_token(create_and_authorize_user) -> str:
    """
    Данная фикстура меняет значение времени истечения в JWT-токене таким образом, чтобы он считался истёкшим.
    :param create_and_authorize_user: Ссылка на фикстуру создания и авторизации пользователя.
    :return: Корректный JWT-токен с изменённым временем истечения.
    """
    initial_correct_refresh_token = create_and_authorize_user.refresh_token
    decoded_refresh_token = validate_and_decode_token(initial_correct_refresh_token)
    token_payload = {
        "id": str(decoded_refresh_token.id),
        "user_id": str(decoded_refresh_token.user_id),
        "issued_at": str(decoded_refresh_token.issued_at),
        "expired_at": str(decoded_refresh_token.issued_at)  # в качестве времени истечения присваивается время выпуска
    }

    resigned_refresh_token_with_modified_expired_at_time = jwt.encode(
        token_payload,
        FrVars.JWT_SIGNATURE_SECRET,
        algorithm="HS256"
    )

    allure.attach(create_and_authorize_user.refresh_token, "Изначальный токен обновления")
    allure.attach(token_payload['expired_at'], "Новое время истечения для переподписанного токена")
    allure.attach(resigned_refresh_token_with_modified_expired_at_time, "Токен доступа, c изменённым временем выпуска")

    return resigned_refresh_token_with_modified_expired_at_time


@pytest.fixture(scope="function")
def make_unavailable_in_db_access_token(create_and_authorize_user) -> str:
    """
    Данная фикстура меняет значение идентификатора в JWT-токене доступа таким образом, чтобы его нельзя было найти в БД.
    :param create_and_authorize_user: Ссылка на фикстуру создания и авторизации пользователя.
    :return: Корректный JWT-токен с изменённым идентификатором.
    """
    initial_correct_access_token = create_and_authorize_user.access_token
    decoded_access_token = validate_and_decode_token(initial_correct_access_token)
    token_payload = {
        "id": str(uuid.uuid4()),  # для невозможности обнаружения токена в БД ему присваивается новый ID
        "user_id": str(decoded_access_token.user_id),
        "issued_at": str(decoded_access_token.issued_at),
        "expired_at": str(decoded_access_token.expired_at)
    }

    resigned_access_token_with_modified_id = jwt.encode(
        token_payload,
        FrVars.JWT_SIGNATURE_SECRET,
        algorithm="HS256"
    )

    allure.attach(create_and_authorize_user.access_token, "Изначальный токен доступа")
    allure.attach(token_payload['id'], "Новой ID для переподписанного токена")
    allure.attach(resigned_access_token_with_modified_id, "Токен доступа, c изменённым ID")

    return resigned_access_token_with_modified_id


@pytest.fixture(scope="function")
def make_unavailable_in_db_refresh_token(create_and_authorize_user) -> str:
    """
    Данная фикстура меняет значение идентификатора в JWT-токене обновления таким образом, чтобы его нельзя было найти
    в БД.
    :param create_and_authorize_user: Ссылка на фикстуру создания и авторизации пользователя.
    :return: Корректный JWT-токен с изменённым идентификатором.
    """
    initial_correct_refresh_token = create_and_authorize_user.refresh_token
    decoded_refresh_token = validate_and_decode_token(initial_correct_refresh_token)
    token_payload = {
        "id": str(uuid.uuid4()),  # для невозможности обнаружения токена в БД ему присваивается новый ID
        "user_id": str(decoded_refresh_token.user_id),
        "issued_at": str(decoded_refresh_token.issued_at),
        "expired_at": str(decoded_refresh_token.expired_at)
    }

    resigned_refresh_token_with_modified_id = jwt.encode(
        token_payload,
        FrVars.JWT_SIGNATURE_SECRET,
        algorithm="HS256"
    )

    allure.attach(create_and_authorize_user.refresh_token, "Изначальный токен обновления")
    allure.attach(token_payload['id'], "Новой ID для переподписанного токена")
    allure.attach(resigned_refresh_token_with_modified_id, "Токен доступа, c изменённым ID")

    return resigned_refresh_token_with_modified_id


@pytest.fixture(scope="function")
def make_revoked_access_token(database, create_and_authorize_user) -> str:
    """
    Данная фикстура предоставляет токен доступа, статус отзыва которого имеет значение "отозван" в БД.

    На стадии уборки данная фикстура возвращает предоставленному ранее токену значение "не отозван", для обеспечения
    корректной работы стадии уборки фикстуры "create_and_authorize_user".

    :param database: Ссылка на фикстуру, предоставляющую подключение к БД.
    :param create_and_authorize_user: Ссылка на фикстуру создания и авторизации пользователя.
    :return: Корректный JWT-токен доступа, помеченный отозванным в БД.
    """
    initial_correct_access_token = create_and_authorize_user.access_token
    decoded_access_token = validate_and_decode_token(initial_correct_access_token)

    change_jwt_token_revoke_status(
        db=database,
        token_id=decoded_access_token.id,
        token_type="access_token",
        new_value=True
    )

    yield initial_correct_access_token

    change_jwt_token_revoke_status(
        db=database,
        token_id=decoded_access_token.id,
        token_type="access_token",
        new_value=False
    )


@pytest.fixture(scope="function")
def make_revoked_refresh_token(database, create_and_authorize_user) -> str:
    """
    Данная фикстура предоставляет токен обновления, статус отзыва которого имеет значение "отозван" в БД.

    На стадии уборки данная фикстура возвращает предоставленному ранее токену значение "не отозван", для обеспечения
    корректной работы стадии уборки фикстуры "create_and_authorize_user".

    :param database: Ссылка на фикстуру, предоставляющую подключение к БД.
    :param create_and_authorize_user: Ссылка на фикстуру создания и авторизации пользователя.
    :return: Корректный JWT-токен обновления, помеченный отозванным в БД.
    """
    initial_correct_refresh_token = create_and_authorize_user.refresh_token
    decoded_refresh_token = validate_and_decode_token(initial_correct_refresh_token)

    change_jwt_token_revoke_status(
        db=database,
        token_id=decoded_refresh_token.id,
        token_type="refresh_token",
        new_value=True
    )

    yield initial_correct_refresh_token

    change_jwt_token_revoke_status(
        db=database,
        token_id=decoded_refresh_token.id,
        token_type="refresh_token",
        new_value=False
    )