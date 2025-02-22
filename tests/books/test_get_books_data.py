import json

import allure
import requests
from faker import Faker

from data.framework_variables import FrameworkVariables as FrVars
from database.books import get_all_books_data
from helpers.allure_report import attach_request_data_to_report
from helpers.assertions import make_simple_assertion, make_bulk_assertion, AssertionBundle as Assertion
from helpers.json_tools import format_json
from helpers.validate_response import validate_response_model
from models.books import MultipleBooks, SingleBook

fake = Faker()


@allure.parent_suite("Домен «Книги»")
@allure.suite("Получение информации по книгам")
@allure.sub_suite("Основные функциональные тесты получения информации по книгам")
class TestGetBooksData:

    @allure.title("Успешное получение информации по всем книгам")
    @allure.severity(severity_level=allure.severity_level.CRITICAL)
    @allure.description(
        "Данный тест проверяет возможность запроса списка книг пользователем без прав администратора.\n\n"
        "При проведении теста проверяется:\n"
        "- Соответствие кода ответа ожидаемому\n"
        "- Соответствие структуры (модели) ответа ожидаемой\n"
        "- Соответствие списка книг, возвращённому в ответе списку, полученному из БД"
    )
    def test_successful_all_books_data_get(self, database, create_and_authorize_user, create_book):

        res = requests.get(
            url=FrVars.APP_HOST + "/v1/books",
            headers={
                "Access-Token": create_and_authorize_user.access_token
            }
        )
        attach_request_data_to_report(res)

        make_simple_assertion(expected_value=200, actual_value=res.status_code,
                              assertion_name="Проверка кода ответа")

        serialized_response = validate_response_model(
            model=MultipleBooks,
            data=res.json()
        )

        books_data_from_response = serialized_response.root
        books_data_from_db = get_all_books_data(db=database)

        with allure.step("Сравнение списка книг из ответа и из БД"):
            allure.attach(
                format_json(serialized_response.model_dump_json()),
                'Список книг полученный в ответе на запрос'
            )

            prettified_list_from_database = json.dumps(
                [json.loads(book_from_db_as_json.model_dump_json()) for book_from_db_as_json in books_data_from_db]
            )
            allure.attach(
                format_json(prettified_list_from_database),
                'Список книг полученный в ответе из БД'
            )

            books_lists_assertions = []

            for book_from_response in books_data_from_response:
                book_from_db = books_data_from_db.pop(0)
                serialized_book_from_db = SingleBook(
                    id=book_from_db.id,
                    title=book_from_db.title,
                    author=book_from_db.author,
                    isbn=book_from_db.isbn
                )

                books_lists_assertions.append(
                    Assertion(
                        expected_value=book_from_response,
                        actual_value=serialized_book_from_db,
                        assertion_name=f"Данные книги \"{book_from_response.title}\" (ISBN: {book_from_response.isbn}) "
                                       f"одинаковы в ответе и в БД"
                    )
                )

            make_bulk_assertion(
                group_name="Сравнение отдельных книг",
                data=books_lists_assertions
            )
