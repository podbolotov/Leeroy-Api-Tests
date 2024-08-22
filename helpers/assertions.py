from typing import Any
import allure


class AssertionBundle:
    """ Данный класс представляет собой коллекцию данных для массовой проверки.

    Используется в методе make_bulk_assertion.

    При инициализации экземпляра необходимо передать два значения для сравнения:
    ожидаемое, и сравниваемое (фактическое) и название сравнения. """
    def __init__(self, expected_value, actual_value, assertion_name: str):
        """
        Набор данных для массового сравнения

        :param expected_value: Ожидаемое значение
        :param actual_value: Фактическое (сравниваемое) значение
        :param assertion_name: Название сравнения
        """
        self.expected_value = expected_value
        self.actual_value = actual_value
        self.assertion_name: str = assertion_name


def make_simple_assertion(expected_value, actual_value, assertion_name: str):
    with allure.step(assertion_name):
        try:
            assert expected_value == actual_value
            allure.attach(f"Ожидаемое значение: {str(expected_value)}\n"
                          f"Фактическое значение: {str(actual_value)}\n",
                          "Детали сравнения")
        except Exception as e:
            allure.attach(f"Ожидаемое значение: {str(expected_value)}\n"
                          f"Фактическое значение: {str(actual_value)}\n",
                          "Детали сравнения")
            raise AssertionError(f"Фактическое значение сравнения \"{assertion_name}\" не соответствует ожидаемому")


def make_bulk_assertion(data: list[AssertionBundle], group_name: str = "Сравнение группы данных"):
    with allure.step(group_name):
        for bundle in data:
            make_simple_assertion(
                expected_value=bundle.expected_value,
                actual_value=bundle.actual_value,
                assertion_name=bundle.assertion_name
            )
