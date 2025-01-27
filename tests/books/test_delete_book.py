import uuid

import allure
import pytest
import requests
from faker import Faker

from data.framework_variables import FrameworkVariables as FrVars
from database.books import get_book_data_by_id, get_books_count
from helpers.allure_report import attach_request_data_to_report
from helpers.assertions import make_simple_assertion, make_bulk_assertion, AssertionBundle as Assertion, AssertionModes
from helpers.json_tools import format_json
from helpers.validate_response import validate_response_model
from models.books import DeleteBookLackOfPermissionError, BookNotFoundError, DeleteBookSuccessfulResponse

fake = Faker()

@allure.parent_suite("Домен «Книги»")
@allure.suite("Удаление книг")
@allure.sub_suite("Основные функциональные тесты удаления книг")
class TestDeleteBooks:

    @allure.title("Отказ при отсутствии прав администратора")
    @allure.severity(severity_level=allure.severity_level.CRITICAL)
    @allure.description(
        "Данный тест проверяет невозможность удаления книги пользователем, не имеющим прав администратора.\n\n"
        "При проведении теста проверяется:\n"
        "- Соответствие кода ответа ожидаемому\n"
        "- Соответствие структуры (модели) ответа ожидаемой\n"
        "- Сохранность в БД данных книги, которую пытались удалить"
    )
    def test_delete_book_without_administrator_permissions(
            self, database, create_and_authorize_user, create_book
    ):

        res = requests.delete(
            url=FrVars.APP_HOST + f"/v1/books/{create_book.book_id}",
            headers={
                "Access-Token": create_and_authorize_user.access_token
            }
        )
        attach_request_data_to_report(res)

        make_simple_assertion(expected_value=403, actual_value=res.status_code,
                              assertion_name="Проверка кода ответа")

        validate_response_model(
            model=DeleteBookLackOfPermissionError,
            data=res.json()
        )

        book_data_from_db = get_book_data_by_id(db=database, book_id=str(create_book.book_id))

        with allure.step("Верификация сохранности данных книги в БД"):
            allure.attach(
                format_json(book_data_from_db.model_dump_json()),
                'Данные книги, полученные из БД после попытки удаления книги'
            )

            make_bulk_assertion(
                group_name="Верификация данных книги",
                data=[
                    Assertion(
                        expected_value=create_book.book_id,
                        actual_value=book_data_from_db.id,
                        assertion_name="ID книги не был изменён"
                    ),
                    Assertion(
                        expected_value=create_book.title,
                        actual_value=book_data_from_db.title,
                        assertion_name="Заголовок (название) книги не было изменено"
                    ),
                    Assertion(
                        expected_value=create_book.author,
                        actual_value=book_data_from_db.author,
                        assertion_name="Автор (или авторы) книги не были изменены"
                    ),
                    Assertion(
                        expected_value=create_book.isbn,
                        actual_value=book_data_from_db.isbn,
                        assertion_name="ISBN книги не был изменён"
                    )
                ])


    @allure.title("Отказ при наличии забронированных экземпляров книги")
    @allure.severity(severity_level=allure.severity_level.CRITICAL)
    @allure.description(
        "Данный тест проверяет невозможность удаления книги экземпляры которой значатся забронированными (выданными "
        "читателям).\n\n"
        "При проведении теста проверяется:\n"
        "- Соответствие кода ответа ожидаемому\n"
        "- Соответствие структуры (модели) ответа ожидаемой\n"
        "- Сохранность в БД данных книги, которую пытались удалить\n"
        "- Неизменность количества записей о бронированиях экземпляров той книги, которую пытались удалить"
    )
    @pytest.mark.skip("Ожидается реализация функционала бронирований")
    def test_delete_book_with_active_reservations(
            self, database, create_and_authorize_user
    ):
        pass

    @allure.title("Отказ при попытке удаления несуществующей книги")
    @allure.severity(severity_level=allure.severity_level.CRITICAL)
    @allure.description(
        "Данный тест проверяет корректность обработки кейса с передачей ID книги, найти которую не удалось.\n\n"
        "При проведении теста проверяется:\n"
        "- Соответствие кода ответа ожидаемому\n"
        "- Соответствие структуры (модели) ответа ожидаемой\n"
        "- Неизменность количества книг в БД до и после запроса"
    )
    def test_non_existent_book_delete(
            self, database, authorize_administrator
    ):

        unavailable_in_db_book_id = str(uuid.uuid4())
        total_books_count_before_request = get_books_count(db=database)

        res = requests.delete(
            url=FrVars.APP_HOST + f"/v1/books/{unavailable_in_db_book_id}",
            headers={
                "Access-Token": authorize_administrator.access_token
            }
        )
        attach_request_data_to_report(res)

        total_books_count_after_request = get_books_count(db=database)

        make_simple_assertion(expected_value=404, actual_value=res.status_code,
                              assertion_name="Проверка кода ответа")

        serialized_response = validate_response_model(
            model=BookNotFoundError,
            data=res.json()
        )

        make_simple_assertion(
            expected_value=f"Book with ID {unavailable_in_db_book_id} is not found",
            actual_value=serialized_response.description,
            assertion_name="Детализация ошибки содержит переданный в запросе ID"
        )

        make_simple_assertion(
            expected_value=total_books_count_before_request,
            actual_value=total_books_count_after_request,
            assertion_name="Количество книг после запроса равно количеству книг до запроса"
        )

    @allure.title("Успешное удаление книги")
    @allure.severity(severity_level=allure.severity_level.CRITICAL)
    @allure.description(
        "Данный тест проверяет возможность корректного удаления книги стандартным администратором приложения.\n\n"
        "При проведении теста проверяется:\n"
        "- Соответствие кода ответа ожидаемому\n"
        "- Соответствие структуры (модели) ответа ожидаемой\n"
        "- Отсутствие в БД данных по книге, запрос на удаление которой был отправлен."
    )
    @pytest.mark.parametrize("create_book", ["fixture book deletion should be skipped"], indirect=True)
    def test_successful_book_deletion(
            self, database, authorize_administrator, create_book
    ):

        book_data_from_db_before_delete = get_book_data_by_id(db=database, book_id=str(create_book.book_id))

        res = requests.delete(
            url=FrVars.APP_HOST + f"/v1/books/{create_book.book_id}",
            headers={
                "Access-Token": authorize_administrator.access_token
            }
        )
        attach_request_data_to_report(res)

        make_simple_assertion(expected_value=200, actual_value=res.status_code,
                              assertion_name="Проверка кода ответа")

        validate_response_model(
            model=DeleteBookSuccessfulResponse,
            data=res.json()
        )

        book_data_from_db_after_delete = get_book_data_by_id(db=database, book_id=str(create_book.book_id))

        make_simple_assertion(
            expected_value=None,
            actual_value=book_data_from_db_before_delete,
            assertion_name="Данные по книге до отправки запроса должны существовать в БД",
            mode = AssertionModes.VALUES_ARE_NOT_EQUAL
        )

        make_simple_assertion(
            expected_value=None,
            actual_value=book_data_from_db_after_delete,
            assertion_name="Данные по книге должны отсутствовать в БД после отправки запроса"
        )