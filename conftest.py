import allure
import pytest
import requests
import random
from faker import Faker

from database.users import get_user_data_by_email, get_user_data_by_id
from helpers.allure_report import attach_request_data_to_report
from helpers.assertions import make_simple_assertion
from helpers.validate_response import validate_response_model
from helpers.varirable_manager import VariableManager
from database.db_baseclass import Database
from data.framework_variables import FrameworkVariables as FrVars
from models.authorization import AuthSuccessfulResponse
from models.books import DeleteBookSuccessfulResponse
from models.users import CreatedUserDataBundle, CreateUserSuccessfulResponse, DeleteUserSuccessfulResponse, \
    CreatedUserDataBundleWithTokens


@pytest.fixture(scope="session", autouse=True)
def database() -> Database:
    """
    Данная фикстура предоставляет единое подключение к базе данных.

    :return: Экземпляр класса Database.
    """
    db = Database()
    db.connect_to_database()
    yield db


@pytest.fixture(scope="session")
def variable_manager(database) -> VariableManager:
    """
    Данная фикстура предоставляет менеджер переменных.
    :return: Экземпляр класса VariableManager.
    """
    vman = VariableManager()
    yield vman


@pytest.fixture(scope="class")
def authorize_administrator(variable_manager) -> AuthSuccessfulResponse:
    """
    Данная фикстура авторизует стандартного администратора приложения.

    :param variable_manager: Ссылка на фикстуру "variable_manager".
    :return AuthSuccessfulResponse: (yield) Сериализованный ответ на запрос авторизации.
    """
    res = requests.post(
        url=FrVars.APP_HOST + "/v1/authorize",
        json={
            "email": FrVars.APP_DEFAULT_USER_EMAIL,
            "password": FrVars.APP_DEFAULT_USER_PASSWORD
        }
    )
    attach_request_data_to_report(res)

    make_simple_assertion(
        expected_value=200,
        actual_value=res.status_code,
        assertion_name="Код ответа на запрос фикстуры"
    )

    serialized_response = validate_response_model(
        model=AuthSuccessfulResponse,
        data=res.json()
    )

    yield serialized_response

    res = requests.delete(
        url=FrVars.APP_HOST + "/v1/logout",
        headers={
            "Access-Token": serialized_response.access_token
        }
    )
    attach_request_data_to_report(res)
    make_simple_assertion(
        expected_value=200,
        actual_value=res.status_code,
        assertion_name="Код ответа на запрос фикстуры"
    )


@pytest.fixture(scope="function")
def create_user(database, authorize_administrator, request) -> CreatedUserDataBundle:
    """
    Данная фикстура обеспечивает создание пользователя без прав администратора и его удаление после завершения
    тестирования.
    :param database: Ссылка на фикстуру "database".
        Необходима для запроса уровня прав пользователя перед отправкой запроса на удаление пользователя.
    :param authorize_administrator: Ссылка на фикстуру "variable_manager".
        Используется данной фикстурой, так как создание пользователя требует авторизации администратора.
    :return: Набор данных зарегистрированного пользователя.
    """
    # Стадия подготовки
    # Подготовка данных создаваемого пользователя
    fake = Faker()
    new_user_random_email = fake.email()
    new_user_random_firstname = fake.first_name()
    new_user_random_middlename = random.choice([fake.first_name(), None])
    new_user_random_surname = fake.last_name()
    new_user_random_password = fake.password()

    deletion_skip_directive = getattr(request, 'param', None)

    # Отправка запроса на создание пользователя
    with allure.step("Создание пользователя"):
        res = requests.post(
            url=FrVars.APP_HOST + "/v1/users",
            headers={
                "Access-Token": authorize_administrator.access_token
            },
            json={
                "email": new_user_random_email,
                "firstname": new_user_random_firstname,
                "middlename": new_user_random_middlename,
                "surname": new_user_random_surname,
                "password": new_user_random_password
            }
        )
        attach_request_data_to_report(res)

        make_simple_assertion(
            expected_value=200,
            actual_value=res.status_code,
            assertion_name="Код ответа на запрос создания пользователя в фикстуре"
        )

        serialized_response = validate_response_model(
            model=CreateUserSuccessfulResponse,
            data=res.json()
        )

    # Сериализация данных созданного пользователя в набор
    created_user_data = CreatedUserDataBundle(
        user_id=serialized_response.user_id,
        email=new_user_random_email,
        firstname=new_user_random_firstname,
        middlename=new_user_random_middlename,
        password=new_user_random_password,
        surname=new_user_random_surname
    )
    # Предоставление набора для использования в тестах
    yield created_user_data


    if deletion_skip_directive == "fixture user deletion should be skipped":
        allure.attach(
            f"Параметр фикстуры получил значение \"{request.param}\"",
            "Удаление пользователя было пропущено"
        )
    else:
        # Стадия очистки
        # Проверка наличия у пользователя прав администратора
        user_has_administrator_permissions = get_user_data_by_email(
            db=database,
            email=created_user_data.email
        ).is_admin

        # В случае, если пользователь за время жизни приобрёл права администратора - отзыв прав администратора
        if user_has_administrator_permissions is True:
            with allure.step("Отзыв у удаляемого пользователя прав администратора"):
                res = requests.patch(
                    url=FrVars.APP_HOST + f"/v1/users/admin-permissions/{created_user_data.user_id}/revoke",
                    headers={
                        "Access-Token": authorize_administrator.access_token
                    }
                )
                attach_request_data_to_report(res)

                make_simple_assertion(
                    expected_value=200,
                    actual_value=res.status_code,
                    assertion_name="Код ответа на запрос отзыва прав администратора у пользователя в фикстуре"
                )

        # Отправка запроса на удаление пользователя
        with allure.step("Удаление пользователя"):
            res = requests.delete(
                url=FrVars.APP_HOST + f"/v1/users/{created_user_data.user_id}",
                headers={
                    "Access-Token": authorize_administrator.access_token
                }
            )
            attach_request_data_to_report(res)

            make_simple_assertion(
                expected_value=200,
                actual_value=res.status_code,
                assertion_name="Код ответа на запрос удаления пользователя в фикстуре"
            )

            validate_response_model(
                model=DeleteUserSuccessfulResponse,
                data=res.json()
            )


# TODO: Оптимизировать фикстуры создания пользователей таким образом, чтобы одна фикстура создавала и удаляла сразу
#  двоих тестовых пользователей.
@pytest.fixture(scope="function")
def create_second_user(database, authorize_administrator) -> CreatedUserDataBundle:
    """
    Данная фикстура обеспечивает создание ещё одного пользователя без прав администратора и его удаление после
    завершения тестирования.
    :param database: Ссылка на фикстуру "database".
        Необходима для запроса уровня прав пользователя перед отправкой запроса на удаление пользователя.
    :param authorize_administrator: Ссылка на фикстуру "variable_manager".
        Используется данной фикстурой, так как создание пользователя требует авторизации администратора.
    :return: Набор данных зарегистрированного пользователя.
    """
    # Стадия подготовки
    # Подготовка данных создаваемого пользователя
    fake = Faker()
    new_user_random_email = fake.email()
    new_user_random_firstname = fake.first_name()
    new_user_random_middlename = random.choice([fake.first_name(), None])
    new_user_random_surname = fake.last_name()
    new_user_random_password = fake.password()

    # Отправка запроса на создание пользователя
    with allure.step("Создание пользователя"):
        res = requests.post(
            url=FrVars.APP_HOST + "/v1/users",
            headers={
                "Access-Token": authorize_administrator.access_token
            },
            json={
                "email": new_user_random_email,
                "firstname": new_user_random_firstname,
                "middlename": new_user_random_middlename,
                "surname": new_user_random_surname,
                "password": new_user_random_password
            }
        )
        attach_request_data_to_report(res)

        make_simple_assertion(
            expected_value=200,
            actual_value=res.status_code,
            assertion_name="Код ответа на запрос создания пользователя в фикстуре"
        )

        serialized_response = validate_response_model(
            model=CreateUserSuccessfulResponse,
            data=res.json()
        )

    # Сериализация данных созданного пользователя в набор
    created_user_data = CreatedUserDataBundle(
        user_id=serialized_response.user_id,
        email=new_user_random_email,
        firstname=new_user_random_firstname,
        middlename=new_user_random_middlename,
        password=new_user_random_password,
        surname=new_user_random_surname
    )
    # Предоставление набора для использования в тестах
    yield created_user_data

    # Стадия очистки
    # Проверка наличия у пользователя прав администратора
    user_has_administrator_permissions = get_user_data_by_email(
        db=database,
        email=created_user_data.email
    ).is_admin

    # В случае, если пользователь за время жизни приобрёл права администратора - отзыв прав администратора
    if user_has_administrator_permissions is True:
        with allure.step("Отзыв у удаляемого пользователя прав администратора"):
            res = requests.patch(
                url=FrVars.APP_HOST + f"/v1/users/admin-permissions/{created_user_data.user_id}/revoke",
                headers={
                    "Access-Token": authorize_administrator.access_token
                }
            )
            attach_request_data_to_report(res)

            make_simple_assertion(
                expected_value=200,
                actual_value=res.status_code,
                assertion_name="Код ответа на запрос отзыва прав администратора у пользователя в фикстуре"
            )

    # Отправка запроса на удаление пользователя
    with allure.step("Удаление пользователя"):
        res = requests.delete(
            url=FrVars.APP_HOST + f"/v1/users/{created_user_data.user_id}",
            headers={
                "Access-Token": authorize_administrator.access_token
            }
        )
        attach_request_data_to_report(res)

        make_simple_assertion(
            expected_value=200,
            actual_value=res.status_code,
            assertion_name="Код ответа на запрос удаления пользователя в фикстуре"
        )

        validate_response_model(
            model=DeleteUserSuccessfulResponse,
            data=res.json()
        )

@pytest.fixture(scope="function")
def create_and_authorize_user(create_user, request) -> CreatedUserDataBundleWithTokens:
    """
    Данная фикстура обеспечивает создание пользователя без прав администратора и его авторизацию, а также его выход из
    системы и удаление после завершения тестирования.
    Для создания пользователя данная фикстура вызывает существующую фикстуру "create_user", реализуя на своей стороне
    только авторизацию и выход из системы.

    Выход из системы, реализуемый этой фикстурой, может быть пропущен путём параметризации фикстуры следующим образом::

        @pytest.mark.parametrize("create_and_authorize_user", ["fixture logout should be skipped"], indirect=True)

    :param create_user: Ссылка на фикстуру "create_user".
        Используется для создания и удаления пользователя.
    :param request: Ссылка на объект вызова фикстуры.
        Если в параметре передана строка "fixture logout should be skipped", то вызов эндпоинта DELETE /logout на этапе
        уборки будет пропущен.
    :return: Набор данных зарегистрированного пользователя.
    """
    logout_skip_directive = getattr(request, 'param', None)
    res = requests.post(
        url=FrVars.APP_HOST + "/v1/authorize",
        json={
            "email": create_user.email,
            "password": create_user.password
        }
    )
    attach_request_data_to_report(res)

    make_simple_assertion(
        expected_value=200,
        actual_value=res.status_code,
        assertion_name="Код ответа на запрос фикстуры"
    )

    serialized_response = validate_response_model(
        model=AuthSuccessfulResponse,
        data=res.json()
    )

    yield CreatedUserDataBundleWithTokens(
        user_id=create_user.user_id,
        email=create_user.email,
        firstname=create_user.firstname,
        middlename=create_user.middlename,
        password=create_user.password,
        surname=create_user.surname,
        access_token=serialized_response.access_token,
        refresh_token=serialized_response.refresh_token
    )

    # Данное условие реализует возможность пропуска выхода из учётной записи путём передачи в значении параметра
    # фикстуры "create_and_authorize_user" строки с содержимым "fixture logout should be skipped".
    if logout_skip_directive == "fixture logout should be skipped":
        allure.attach(
            f"Параметр фикстуры получил значение \"{request.param}\"",
            "Выход из учётной записи был пропущен"
        )
    else:
        res = requests.delete(
            url=FrVars.APP_HOST + "/v1/logout",
            headers={
                "Access-Token": serialized_response.access_token
            }
        )
        attach_request_data_to_report(res)
        make_simple_assertion(
            expected_value=200,
            actual_value=res.status_code,
            assertion_name="Код ответа на запрос фикстуры"
        )

# TODO: Оптимизировать фикстуры создания пользователей таким образом, чтобы одна фикстура создавала и удаляла сразу
#  двоих тестовых пользователей.
@pytest.fixture(scope="function")
def create_and_authorize_second_user(create_second_user) -> CreatedUserDataBundleWithTokens:
    """
    Данная фикстура обеспечивает создание ещё одного пользователя без прав администратора и его авторизацию,
    а также его выход из системы и удаление после завершения тестирования.
    Для создания пользователя данная фикстура вызывает существующую фикстуру "create_second_user", реализуя на своей
    стороне только авторизацию и выход из системы.
    :param create_second_user: Ссылка на фикстуру "create_user".
        Используется для создания и удаления пользователя.
    :return: Набор данных зарегистрированного пользователя.
    """
    res = requests.post(
        url=FrVars.APP_HOST + "/v1/authorize",
        json={
            "email": create_second_user.email,
            "password": create_second_user.password
        }
    )
    attach_request_data_to_report(res)

    make_simple_assertion(
        expected_value=200,
        actual_value=res.status_code,
        assertion_name="Код ответа на запрос фикстуры"
    )

    serialized_response = validate_response_model(
        model=AuthSuccessfulResponse,
        data=res.json()
    )

    yield CreatedUserDataBundleWithTokens(
        user_id=create_second_user.user_id,
        email=create_second_user.email,
        firstname=create_second_user.firstname,
        middlename=create_second_user.middlename,
        password=create_second_user.password,
        surname=create_second_user.surname,
        access_token=serialized_response.access_token,
        refresh_token=serialized_response.refresh_token
    )

    res = requests.delete(
        url=FrVars.APP_HOST + "/v1/logout",
        headers={
            "Access-Token": serialized_response.access_token
        }
    )
    attach_request_data_to_report(res)
    make_simple_assertion(
        expected_value=200,
        actual_value=res.status_code,
        assertion_name="Код ответа на запрос фикстуры"
    )


@pytest.fixture(scope="function")
def logout(variable_manager) -> None:
    """
    Данная фикстура обеспечивает вызов эндпоинта /logout для тестовых функций, которые завершились корректной
    авторизацией и требуют погашения выданных токенов.

    Обратите внимание, что данная фикстура читает другую фикстуру, variable_manager, и для успешной работы фикстуры
    logout требуется, чтобы перед её вызовом в variable_manager была записана переменная 'access_token' с токеном,
    который необходимо погасить.

    :param variable_manager: Ссылка на фикстуру "variable_manager"
    :return: Данная фикстура ничего не возвращает.
    """
    yield
    try:
        access_token = variable_manager.get('access_token')
    except AttributeError:
        raise RuntimeError("access_token variable in variable_manager is not setted")
    res = requests.delete(
        url=FrVars.APP_HOST + "/v1/logout",
        headers={
            "Access-Token": access_token
        }
    )
    attach_request_data_to_report(res)
    make_simple_assertion(
        expected_value=200,
        actual_value=res.status_code,
        assertion_name="Код ответа на запрос фикстуры"
    )
    # Очистка переменной access_token из менеджера переменных
    variable_manager.unset('access_token')


@pytest.fixture(scope="function")
def delete_user(database, variable_manager, authorize_administrator) -> None:
    """
    Данная фикстура обеспечивает вызов эндпоинта DELETE /users/{user_id} для тестовых функций, которые завершились
    корректным созданием пользователя и требуют его удаления.

    Обратите внимание, что данная фикстура читает другую фикстуру, variable_manager, и для успешной работы фикстуры
    delete_user требуется, чтобы перед её вызовом в variable_manager была записана переменная 'user_id' c ID,
    пользователя, которого необходимо удалить.

    :param database: Ссылка на фикстуру "database".
        Необходима для запроса уровня прав пользователя перед отправкой запроса на удаление пользователя.
    :param authorize_administrator: Ссылка на фикстуру "authorize_administrator".
        Используется данной фикстурой, так как удаление пользователя требует авторизации администратора.
    :param variable_manager: Ссылка на фикстуру "variable_manager"
    :return: Данная фикстура ничего не возвращает.
    """
    yield
    try:
        user_id = variable_manager.get('user_id')
    except AttributeError:
        raise RuntimeError("user_id variable in variable_manager is not setted")

    user_has_administrator_permissions = get_user_data_by_id(
        db=database,
        user_id=user_id
    ).is_admin

    if user_has_administrator_permissions is True:
        with allure.step("Отзыв у удаляемого пользователя прав администратора"):
            res = requests.patch(
                url=FrVars.APP_HOST + f"/v1/users/admin-permissions/{user_id}/revoke",
                headers={
                    "Access-Token": authorize_administrator.access_token
                }
            )
            attach_request_data_to_report(res)

            make_simple_assertion(
                expected_value=200,
                actual_value=res.status_code,
                assertion_name="Код ответа на запрос отзыва прав администратора у пользователя в фикстуре"
            )

    # Отправка запроса на удаление пользователя
    with allure.step("Удаление пользователя"):
        res = requests.delete(
            url=FrVars.APP_HOST + f"/v1/users/{user_id}",
            headers={
                "Access-Token": authorize_administrator.access_token
            }
        )
        attach_request_data_to_report(res)

        make_simple_assertion(
            expected_value=200,
            actual_value=res.status_code,
            assertion_name="Код ответа на запрос удаления пользователя в фикстуре"
        )

        validate_response_model(
            model=DeleteUserSuccessfulResponse,
            data=res.json()
        )

    # Очистка переменной user_id из менеджера переменных
    variable_manager.unset('user_id')

@pytest.fixture(scope="function")
def delete_book(database, variable_manager, authorize_administrator) -> None:
    """
    Данная фикстура обеспечивает вызов эндпоинта DELETE /books/{book_id} для тестовых функций, которые завершились
    корректным созданием книги и требуют её удаления.

    Обратите внимание, что данная фикстура читает другую фикстуру, variable_manager, и для успешной работы фикстуры
    delete_book требуется, чтобы перед её вызовом в variable_manager была записана переменная 'book_id' c ID,
    книги, которую необходимо удалить.

    :param authorize_administrator: Ссылка на фикстуру "authorize_administrator".
        Используется данной фикстурой, так как удаление книги требует наличия прав администратора.
    :param variable_manager: Ссылка на фикстуру "variable_manager".
    :return: Данная фикстура ничего не возвращает.
    """
    yield
    try:
        book_id = variable_manager.get('book_id')
    except AttributeError:
        raise RuntimeError("book_id variable in variable_manager is not setted")

    # Отправка запроса на удаление книги
    with allure.step("Удаление книги"):
        res = requests.delete(
            url=FrVars.APP_HOST + f"/v1/books/{book_id}",
            headers={
                "Access-Token": authorize_administrator.access_token
            }
        )
        attach_request_data_to_report(res)

        make_simple_assertion(
            expected_value=200,
            actual_value=res.status_code,
            assertion_name="Код ответа на запрос удаления книги в фикстуре"
        )

        validate_response_model(
            model=DeleteBookSuccessfulResponse,
            data=res.json()
        )

    # Очистка переменной book_id из менеджера переменных
    variable_manager.unset('book_id')