import allure
import pytest
import requests
import random
from faker import Faker

from data.framework_variables import FrameworkVariables as FrVars
from database.users import get_user_data_by_email, get_all_administrators_ids, \
    bulk_change_administrator_permissions
from helpers.allure_report import attach_request_data_to_report
from helpers.assertions import make_simple_assertion
from models.users import CreateUserValidationCaseData

fake = Faker()

@pytest.fixture(scope='function')
@allure.title("Изменение уровня прав пользователя")
def before_test_user_has_administrator_permissions(
        database, authorize_administrator, create_user, request
) -> bool:
    """
    Данная фикстура обеспечивает подготовку тестовых данных путём приведения наличия прав администратора у пользователя
    к значению, определённому в параметре тестовой функции (с применением indirect-параметризации).

    :param database: Ссылка на фикстуру "database".
        Необходима для запроса уровня прав пользователя перед отправкой запроса на его изменение.
    :param authorize_administrator: Ссылка на фикстуру "variable_manager".
        Используется данной фикстурой, так как изменение уровня прав пользователя требует авторизации администратора.
    :param create_user: Ссылка на фикстуру "create_user".
        Используется данной фикстурой для получения данных созданного пользователя,
        уровень прав которого требуется изменить.
    :param request: Ссылка на объект вызова фикстуры, содержащий параметр, который определяет действие над уровнем
        прав пользователя. Ожидается, что в параметре будет передано значение с типом bool.
    :return: Ожидаемое значение признака наличия прав администратора у пользователя.
    """
    user_should_be_administrator = request.param
    user_already_has_correct_permissions_state = get_user_data_by_email(
        db=database,
        email=create_user.email
    ).is_admin

    if user_should_be_administrator != user_already_has_correct_permissions_state:
        with allure.step("Изменение уровня прав пользователя"):
            if user_should_be_administrator is True:
                action = "grant"
            elif user_should_be_administrator is False:
                action = "revoke"
            else:
                raise RuntimeError("Incorrect expected user permissions state!")

            res = requests.patch(
                url=FrVars.APP_HOST + f"/v1/users/admin-permissions/{create_user.user_id}/{action}",
                headers={
                    "Access-Token": authorize_administrator.access_token
                }
            )
            attach_request_data_to_report(res)

            make_simple_assertion(
                expected_value=200,
                actual_value=res.status_code,
                assertion_name="Код ответа на запрос изменения прав администратора пользователя в фикстуре"
            )

    return user_should_be_administrator


@pytest.fixture(scope='function')
@allure.title("Отзыв прав администратора у всех администраторов кроме стандартного")
def revoke_all_administrators_permissions_except_default(database):
    # Запрашиваем список всех существующих администраторов, за исключением стандартного и сохраняем его в переменную.
    initial_administrators_ids = get_all_administrators_ids(db=database, mode='except_default')
    allure.attach(str(initial_administrators_ids), "Изначальный список ID администраторов, "
                                              "за исключением стандартного администратора")
    # Осуществляем отзыв полномочий администратора у всех администраторов, кроме стандартного.
    bulk_change_administrator_permissions(db=database, ids=initial_administrators_ids, is_admin=False)
    yield
    # Возвращаем права всем администраторам, у которых права были отозваны.
    bulk_change_administrator_permissions(db=database, ids=initial_administrators_ids, is_admin=True)
    # Запрашиваем список всех администраторов, кроме стандартного, после восстановления прав.
    administrators_ids_after_restore = get_all_administrators_ids(db=database, mode='except_default')
    allure.attach(str(initial_administrators_ids), "Список ID администраторов, за исключением стандартного "
                                                   "администратора, после восстановления прав")
    # Проверяем, что права администратора возвращены всем существовавшим до отзыва прав администраторам.
    make_simple_assertion(
        expected_value=initial_administrators_ids,
        actual_value=administrators_ids_after_restore,
        assertion_name="Список администраторов после восстановления уровня прав эквивалентен изначальному списку"
    )


@pytest.fixture(scope='function')
@allure.title("Подготовка данных для валидации запроса на создание пользователя")
def prepare_request_for_user_creation_validation(
        request, authorize_administrator
) -> CreateUserValidationCaseData | RuntimeError:
    new_user_random_email = fake.email()
    new_user_random_firstname = fake.first_name()
    new_user_random_middlename = random.choice([fake.first_name(), None])
    new_user_random_surname = fake.last_name()
    new_user_random_password = fake.password()

    headers_template = {
        "Access-Token": authorize_administrator.access_token
    }

    body_template = {
            "email": new_user_random_email,
            "firstname": new_user_random_firstname,
            "middlename": new_user_random_middlename,
            "surname": new_user_random_surname,
            "password": new_user_random_password
    }

    case_type = getattr(request, 'param', None)

    match case_type:
        case 'without_access_token':
            del headers_template["Access-Token"]
            return CreateUserValidationCaseData(
                case=case_type,
                headers_template=headers_template,
                body_template=body_template,
                case_title = "Отказ при передаче запроса без токена доступа",
                case_description = "Данный кейс проверяет отказ в создании пользователя при отсутствии в запросе "
                                   "токена доступа.\n\n"
                                   "При проведении теста проверяется:\n"
                                   "- Соответствие кода ответа ожидаемому\n"
                                   "- Соответствие структуры (модели) ответа ожидаемой\n"
                                   "- Неизменность числа пользователей в таблице пользователей в БД",
                expected_code = 400
            )

        case 'without_email':
            del body_template["email"]
            return CreateUserValidationCaseData(
                case=case_type,
                headers_template=headers_template,
                body_template=body_template,
                case_title="Отказ при передаче запроса без поля email",
                case_description="Данный кейс проверяет отказ в создании пользователя при отсутствии в запросе поля "
                                 "email.\n\n"
                                 "При проведении теста проверяется:\n"
                                 "- Соответствие кода ответа ожидаемому\n"
                                 "- Неизменность числа пользователей в таблице пользователей в БД"
            )

        case 'email_incorrect_data_type':
            body_template["email"] = random.choice([
                random.randint(1, 9999),
                [],
                {},
                None
            ])
            return CreateUserValidationCaseData(
                case=case_type,
                headers_template=headers_template,
                body_template=body_template,
                case_title="Отказ при передаче некорректного типа данных в поле email",
                case_description="Данный кейс проверяет отказ в создании пользователя при передаче поля email с "
                                 "некорректным типом данных.\n\n"
                                 "При проведении теста проверяется:\n"
                                 "- Соответствие кода ответа ожидаемому\n"
                                 "- Неизменность числа пользователей в таблице пользователей в БД"
            )

        case 'without_firstname':
            del body_template["firstname"]
            return CreateUserValidationCaseData(
                case=case_type,
                headers_template=headers_template,
                body_template=body_template,
                case_title="Отказ при передаче запроса без поля firstname",
                case_description="Данный кейс проверяет отказ в создании пользователя при отсутствии в запросе поля "
                                 "firstname.\n\n"
                                 "При проведении теста проверяется:\n"
                                 "- Соответствие кода ответа ожидаемому\n"
                                 "- Неизменность числа пользователей в таблице пользователей в БД"
            )

        case 'firstname_incorrect_data_type':
            body_template["firstname"] = random.choice([
                random.randint(1, 9999),
                [],
                {},
                None
            ])
            return CreateUserValidationCaseData(
                case=case_type,
                headers_template=headers_template,
                body_template=body_template,
                case_title="Отказ при передаче некорректного типа данных в поле firstname",
                case_description="Данный кейс проверяет отказ в создании пользователя при передаче поля firstname с "
                                 "некорректным типом данных.\n\n"
                                 "При проведении теста проверяется:\n"
                                 "- Соответствие кода ответа ожидаемому\n"
                                 "- Неизменность числа пользователей в таблице пользователей в БД"
            )

        case 'without_surname':
            del body_template["surname"]
            return CreateUserValidationCaseData(
                case=case_type,
                headers_template=headers_template,
                body_template=body_template,
                case_title="Отказ при передаче запроса без поля surname",
                case_description="Данный кейс проверяет отказ в создании пользователя при отсутствии в запросе поля "
                                 "surname.\n\n"
                                 "При проведении теста проверяется:\n"
                                 "- Соответствие кода ответа ожидаемому\n"
                                 "- Неизменность числа пользователей в таблице пользователей в БД"
            )

        case 'surname_incorrect_data_type':
            body_template["surname"] = random.choice([
                random.randint(1, 9999),
                [],
                {},
                None
            ])
            return CreateUserValidationCaseData(
                case=case_type,
                headers_template=headers_template,
                body_template=body_template,
                case_title="Отказ при передаче некорректного типа данных в поле surname",
                case_description="Данный кейс проверяет отказ в создании пользователя при передаче поля surname с "
                                 "некорректным типом данных.\n\n"
                                 "При проведении теста проверяется:\n"
                                 "- Соответствие кода ответа ожидаемому\n"
                                 "- Неизменность числа пользователей в таблице пользователей в БД"
            )

        case 'without_password':
            del body_template["password"]
            return CreateUserValidationCaseData(
                case=case_type,
                headers_template=headers_template,
                body_template=body_template,
                case_title="Отказ при передаче запроса без поля password",
                case_description="Данный кейс проверяет отказ в создании пользователя при отсутствии в запросе поля "
                                 "password.\n\n"
                                 "При проведении теста проверяется:\n"
                                 "- Соответствие кода ответа ожидаемому\n"
                                 "- Неизменность числа пользователей в таблице пользователей в БД"
            )

        case 'password_incorrect_data_type':
            body_template["password"] = random.choice([
                random.randint(1, 9999),
                [],
                {},
                None
            ])
            return CreateUserValidationCaseData(
                case=case_type,
                headers_template=headers_template,
                body_template=body_template,
                case_title="Отказ при передаче некорректного типа данных в поле password",
                case_description="Данный кейс проверяет отказ в создании пользователя при передаче поля password с "
                                 "некорректным типом данных.\n\n"
                                 "При проведении теста проверяется:\n"
                                 "- Соответствие кода ответа ожидаемому\n"
                                 "- Неизменность числа пользователей в таблице пользователей в БД"
            )

        case _:
            return RuntimeError("Данный тип кейса не может быть обработан")
