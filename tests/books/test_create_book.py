import random

import allure
import requests
from faker import Faker

from data.framework_variables import FrameworkVariables as FrVars
from database.books import get_book_data_by_id, get_books_count, get_book_data_by_isbn
from helpers.allure_report import attach_request_data_to_report
from helpers.assertions import make_simple_assertion, make_bulk_assertion, AssertionBundle as Assertion
from helpers.json_tools import format_json
from helpers.validate_response import validate_response_model
from models.books import CreateBookSuccessfulResponse, CreateBookLackOfPermissionError, CreateBookNotUniqueIsbnError

fake = Faker()

@allure.parent_suite("Домен «Книги»")
@allure.suite("Создание книг")
@allure.sub_suite("Основные функциональные тесты создания книг")
class TestCreateBooks:

    @allure.title("Отказ при отсутствии прав администратора")
    @allure.severity(severity_level=allure.severity_level.CRITICAL)
    @allure.description(
        "Данный тест проверяет невозможность создания книги пользователем, не имеющим прав администратора.\n\n"
        "При проведении теста проверяется:\n"
        "- Соответствие кода ответа ожидаемому\n"
        "- Соответствие структуры (модели) ответа ожидаемой\n"
        "- Отсутствие изменений списка добавленных книг (проверяется, что длина таблицы с книгами после отправки "
        "запроса не изменилась)."
        "- Отсутствие данных по книге при попытке найти её по ISBN."
    )
    def test_create_book_without_administrator_permissions(
            self, database, create_and_authorize_user
    ):
        book_title = fake.catch_phrase()
        book_author = fake.name()
        book_isbn = random.choice([
            fake.isbn10(separator=""),
            fake.isbn13(separator="")
        ])

        total_books_count_before_request = get_books_count(db=database)

        res = requests.post(
            url=FrVars.APP_HOST + "/v1/books",
            headers={
                "Access-Token": create_and_authorize_user.access_token
            },
            json={
                "title": book_title,
                "author": book_author,
                "isbn": book_isbn
            }
        )
        attach_request_data_to_report(res)

        total_books_count_after_request = get_books_count(db=database)

        make_simple_assertion(expected_value=403, actual_value=res.status_code,
                              assertion_name="Проверка кода ответа")

        validate_response_model(
            model=CreateBookLackOfPermissionError,
            data=res.json()
        )

        book_data_from_db = get_book_data_by_isbn(db=database, isbn=book_isbn)

        make_bulk_assertion(
            group_name="Проверка состояния таблицы книг в БД",
            data=[
                Assertion(
                    expected_value=total_books_count_before_request,
                    actual_value=total_books_count_after_request,
                    assertion_name="Количество книг после запроса равно количеству книг до запроса"
                ),
                Assertion(
                    expected_value=None,
                    actual_value=book_data_from_db,
                    assertion_name="Книгу не удаётся найти по ISBN"
                )
            ])

    @allure.title("Отказ при попытке создания дубликата")
    @allure.severity(severity_level=allure.severity_level.CRITICAL)
    @allure.description(
        "Данный тест проверяет невозможность создания книги с ISBN, который уже присвоен любой существующей в БД "
        "книге.\n\n"
        "При проведении теста проверяется:\n"
        "- Соответствие кода ответа ожидаемому\n"
        "- Соответствие структуры (модели) ответа ожидаемой\n"
        "- Отсутствие изменений списка добавленных книг (проверяется, что длина таблицы с книгами после отправки "
        "запроса не изменилась)."
        "- Отсутствие изменений данных существующей книги, ISBN которой был передан"
    )
    def test_create_book_isbn_is_not_unique(
            self, database, authorize_administrator, create_book
    ):
        book_title = fake.catch_phrase()
        book_author = fake.name()
        book_isbn = create_book.isbn

        existent_book_data_from_db_before_request = get_book_data_by_isbn(db=database, isbn=book_isbn)
        total_books_count_before_request = get_books_count(db=database)

        res = requests.post(
            url=FrVars.APP_HOST + "/v1/books",
            headers={
                "Access-Token": authorize_administrator.access_token
            },
            json={
                "title": book_title,
                "author": book_author,
                "isbn": book_isbn
            }
        )
        attach_request_data_to_report(res)

        existent_book_data_from_db_after_request = get_book_data_by_isbn(db=database, isbn=book_isbn)
        total_books_count_after_request = get_books_count(db=database)

        make_simple_assertion(expected_value=400, actual_value=res.status_code,
                              assertion_name="Проверка кода ответа")

        serialized_response = validate_response_model(
            model=CreateBookNotUniqueIsbnError,
            data=res.json()
        )

        make_simple_assertion(
            expected_value=f"Book with ISBN {book_isbn} already exist",
            actual_value=serialized_response.description,
            assertion_name="Детализация ошибки содержит занятый ISBN"
        )

        make_simple_assertion(
            expected_value=total_books_count_before_request,
            actual_value=total_books_count_after_request,
            assertion_name="Количество книг после запроса равно количеству книг до запроса"
        )

        make_bulk_assertion(
            group_name="Проверка неизменности данных существующей книги в БД",
            data=[
                Assertion(
                    expected_value=existent_book_data_from_db_before_request.id,
                    actual_value=existent_book_data_from_db_after_request.id,
                    assertion_name="ID существующей книги не изменился после запроса"
                ),
                Assertion(
                    expected_value=existent_book_data_from_db_before_request.author,
                    actual_value=existent_book_data_from_db_after_request.author,
                    assertion_name="Автор существующей книги не изменился после запроса"
                ),
                Assertion(
                    expected_value=existent_book_data_from_db_before_request.title,
                    actual_value=existent_book_data_from_db_after_request.title,
                    assertion_name="Заглавие существующей книги не изменилось после запроса"
                ),
                Assertion(
                    expected_value=existent_book_data_from_db_before_request.isbn,
                    actual_value=existent_book_data_from_db_after_request.isbn,
                    assertion_name="ISBN существующей книги не изменился после запроса"
                )
            ])

    @allure.title("Успешное создание книги")
    @allure.severity(severity_level=allure.severity_level.CRITICAL)
    @allure.description(
        "Данный тест проверяет возможность создания новой книги стандартным администратором приложения.\n\n"
        "При проведении теста проверяется:\n"
        "- Соответствие кода ответа ожидаемому\n"
        "- Соответствие структуры (модели) ответа ожидаемой\n"
        "- Корректность записи данных созданной книги в БД, совпадение записанных в БД данных с "
        "данными полученными в ответе (в случае id) и данными переданными в запросе (в случае со всеми остальными "
        "данными)"
    )
    def test_successful_book_creation(self, database, variable_manager, authorize_administrator, delete_book):
        book_title = fake.catch_phrase()
        book_author = fake.name()
        book_isbn = random.choice([
            fake.isbn10(separator=""),
            fake.isbn13(separator="")
        ])

        res = requests.post(
            url=FrVars.APP_HOST + "/v1/books",
            headers={
                "Access-Token": authorize_administrator.access_token
            },
            json={
                "title": book_title,
                "author": book_author,
                "isbn": book_isbn
            }
        )
        attach_request_data_to_report(res)

        make_simple_assertion(expected_value=200, actual_value=res.status_code,
                              assertion_name="Проверка кода ответа")

        serialized_response = validate_response_model(
            model=CreateBookSuccessfulResponse,
            data=res.json()
        )

        book_data_from_db = get_book_data_by_id(db=database, book_id=serialized_response.book_id)

        with allure.step("Верификация сохранённых в БД данных книги"):
            allure.attach(
                format_json(book_data_from_db.model_dump_json()),
                'Данные созданной книги из БД'
            )

            make_bulk_assertion(
                group_name="Верификация данных книги",
                data=[
                    Assertion(
                        expected_value=serialized_response.book_id,
                        actual_value=book_data_from_db.id,
                        assertion_name="ID созданной книги соответствует полученному в ответе"
                    ),
                    Assertion(
                        expected_value=book_title,
                        actual_value=book_data_from_db.title,
                        assertion_name="Заголовок (название) книги соответствует переданному в запросе"
                    ),
                    Assertion(
                        expected_value=book_author,
                        actual_value=book_data_from_db.author,
                        assertion_name="Автор (или авторы) книги соответствуют переданным в запросе"
                    ),
                    Assertion(
                        expected_value=book_isbn,
                        actual_value=book_data_from_db.isbn,
                        assertion_name="ISBN книги соответствует переданному в запросе"
                    )
                ])

        # Переменная book_id назначается для дальнейшей обработки в фикстуре delete_book.
        variable_manager.set("book_id", serialized_response.book_id)
