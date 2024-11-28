import allure
import pytest
import requests

from data.framework_variables import FrameworkVariables as FrVars
from database.users import get_user_data_by_email, get_all_administrators_ids, \
    bulk_change_administrator_permissions
from helpers.allure_report import attach_request_data_to_report
from helpers.assertions import make_simple_assertion


@pytest.fixture
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
                url=FrVars.APP_HOST + f"/users/admin-permissions/{create_user.user_id}/{action}",
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