import random

import allure
import pytest
import requests
from faker import Faker

from data.framework_variables import FrameworkVariables as FrVars
from helpers.allure_report import attach_request_data_to_report
from helpers.assertions import make_simple_assertion
from helpers.validate_response import validate_response_model
from models.books import DeleteBookSuccessfulResponse, CreateBookSuccessfulResponse, CreatedBookDataBundle


@pytest.fixture(scope="function")
@allure.title("Создание тестовой книги")
def create_book(database, authorize_administrator, request) -> CreatedBookDataBundle:
    """
    Данная фикстура обеспечивает создание книги и её удаление после завершения тестирования.

    Удаление книги, реализуемое этой фикстурой, может быть пропущено путём параметризации фикстуры следующим образом::

        @pytest.mark.parametrize("create_book", ["fixture book deletion should be skipped"], indirect=True)

    :param authorize_administrator: Ссылка на фикстуру "authorize_administrator".
        Используется данной фикстурой, так как создание книги требует прав администратора.
    :param database: Ссылка на фикстуру "database".
        Используется для проверки наличия бронирований экземпляров книги перед её удалением.
    :param request: Ссылка на объект вызова фикстуры.
        Если в параметре передана строка "fixture book deletion should be skipped", то вызов эндпоинта
        DELETE /books/{book_id} на этапе уборки будет пропущен.
    :return: Набор данных созданной книги.
    """
    # Стадия подготовки
    # Подготовка данных книги
    fake = Faker()
    book_title = fake.catch_phrase()
    book_author = fake.name()
    book_isbn = random.choice([
        fake.isbn10(separator=""),
        fake.isbn13(separator="")
    ])

    deletion_skip_directive = getattr(request, 'param', None)

    # Отправка запроса на создание книги
    with allure.step("Создание книги"):
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

        make_simple_assertion(
            expected_value=200,
            actual_value=res.status_code,
            assertion_name="Код ответа на запрос создания книги в фикстуре"
        )

        serialized_response = validate_response_model(
            model=CreateBookSuccessfulResponse,
            data=res.json()
        )

    # Сериализация данных созданной книги в набор
    created_book_data = CreatedBookDataBundle(
        book_id=serialized_response.book_id,
        title=book_title,
        author=book_author,
        isbn=book_isbn
    )
    # Предоставление набора для использования в тестах
    yield created_book_data

    if deletion_skip_directive == "fixture book deletion should be skipped":
        allure.attach(
            f"Параметр фикстуры получил значение \"{request.param}\"",
            "Удаление книги было пропущено"
        )
    else:
        # Стадия очистки
        # Проверка наличия у пользователя прав администратора
        # TODO: Добавить проверку на наличие бронирований экземпляров книги, которая запланирована к удалению
        book_has_reserved_items = False # до реализации функционала бронирования экземпляров всегда возвращаем False;

        # В случае, если у книги имеются забронированные экземпляры - вызываем метод возвращения экземпляров
        if book_has_reserved_items is True:
            with allure.step("Возвращение забронированных экземпляров книги"):
                pass # тут будет реализован метод возвращения забронированных экземпляров

        # Отправка запроса на удаление книги
        with allure.step("Удаление книги"):
            res = requests.delete(
                url=FrVars.APP_HOST + f"/v1/books/{created_book_data.book_id}",
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


@pytest.fixture(scope="function")
@allure.title("Удаление тестовой книги")
def delete_book(variable_manager, authorize_administrator) -> None:
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

    allure.attach("Фикстура инициализирована и ожидает стадии уборки.", "Ожидание стадии уборки")

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