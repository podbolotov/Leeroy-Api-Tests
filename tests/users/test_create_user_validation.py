import allure
import pytest
import requests

from data.framework_variables import FrameworkVariables as FrVars
from database.users import get_users_count
from helpers.allure_report import attach_request_data_to_report
from helpers.assertions import make_simple_assertion
from helpers.validate_response import validate_response_model
from models.authorization import AccessTokenNotProvidedError


@allure.parent_suite("Домен «Пользователи»")
@allure.suite("Создание пользователей")
@allure.sub_suite("Основные нефункциональные тесты создания пользователей")
class TestCreateUsersValidation:

    cases_list = [
        'without_access_token',
        'without_email',
        'email_incorrect_data_type',
        'without_firstname',
        'firstname_incorrect_data_type',
        'without_surname',
        'surname_incorrect_data_type',
        'without_password',
        'password_incorrect_data_type'
    ]

    @pytest.mark.parametrize('prepare_request_for_user_creation_validation', cases_list, indirect=True)
    @allure.severity(severity_level=allure.severity_level.CRITICAL)
    def test_user_creation_request_validation(self, prepare_request_for_user_creation_validation, database):

        prepared_request = prepare_request_for_user_creation_validation

        allure.dynamic.title(prepared_request.case_title)
        allure.dynamic.description(prepared_request.case_description)

        headers, json = (prepared_request.headers_template,
                         prepared_request.body_template)

        users_count_before_request = get_users_count(db=database, mode='table_count')

        res = requests.post(
            url=FrVars.APP_HOST + "/v1/users",
            headers=headers,
            json=json
        )
        attach_request_data_to_report(res)

        make_simple_assertion(
            expected_value=prepared_request.expected_code,
            actual_value=res.status_code,
            assertion_name="Проверка кода ответа"
        )

        if prepared_request.case == "without_access_token":
            validate_response_model(
                model=AccessTokenNotProvidedError,
                data=res.json()
            )

        users_count_after_request = get_users_count(db=database, mode='table_count')

        make_simple_assertion(
            expected_value=users_count_before_request,
            actual_value=users_count_after_request,
            assertion_name=f"Общее количество записей в таблице пользователей не изменилось после запроса"
        )
