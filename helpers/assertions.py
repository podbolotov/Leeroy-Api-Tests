from typing import Any

import allure
from enum import Enum, auto


class AssertionModes(Enum):
    """ Данный класс содержит возможные режимы сравнения значений, производимых функцией make_simple_assertion() """

    VALUES_ARE_EQUAL = auto()
    """ Проверка на полную эквивалентность значений """

    VALUES_ARE_NOT_EQUAL = auto()
    """ Проверка отсутствия эквивалентности значений """

    EXPECTED_VALUE_GREATER_THAN_ACTUAL = auto()
    """ Проверка большинства ожидаемого значения над фактическим значением """

    EXPECTED_VALUE_GREATER_THAN_ACTUAL_OR_EQUAL_TO_IT = auto()
    """ Проверка большинства ожидаемого значения над фактическим значением либо равенства ему """

    ACTUAL_VALUE_GREATER_THAN_EXPECTED = auto()
    """ Проверка большинства фактического значения над ожидаемым значением """

    ACTUAL_VALUE_GREATER_THAN_EXPECTED_OR_EQUAL_TO_IT = auto()
    """ Проверка большинства фактического значения над ожидаемым значением либо равенства ему """

class AssertionBundle:
    """ Данный класс представляет собой коллекцию данных для массовой проверки.

    Используется в методе make_bulk_assertion.

    При инициализации экземпляра необходимо передать два значения для сравнения:
    ожидаемое, и сравниваемое (фактическое) и название сравнения. """

    def __init__(
            self,
            expected_value,
            actual_value,
            assertion_name: str,
            assertion_mode: AssertionModes = AssertionModes.VALUES_ARE_EQUAL
    ):
        """
        Набор данных для массового сравнения

        :param expected_value: Ожидаемое значение
        :param actual_value: Фактическое (сравниваемое) значение
        :param assertion_name: Название сравнения
        """
        self.expected_value = expected_value
        self.actual_value = actual_value
        self.assertion_name: str = assertion_name
        self.assertion_mode: AssertionModes = assertion_mode


def make_simple_assertion(
        expected_value: Any,
        actual_value: Any,
        assertion_name: str,
        mode: AssertionModes = AssertionModes.VALUES_ARE_EQUAL
):
    """
    Данный метод обеспечивает сравнение переданных ему данных.

    Метод имеет несколько режимов сравнения, как на эквивалентность данных,
    так и на большинство одних данных над другими (с доступными режимами можно ознакомиться в документации класса
    ``AssertionModes``).

    :param expected_value: Ожидаемое (первое) значение сравнения.
    :param actual_value: Фактическое (второе) значение сравнения.
    :param assertion_name: Название сравнения в отчёте.
    :param mode: Режим сравнения (по умолчанию производится сравнение на полную эквивалентность данных).
    :raises ValueError: Ошибка, возвращаемая в случае, если установленный режим сравнения не входит в перечень
        допустимых режимов.
    :returns: Метод ничего не возвращает.
    """
    with allure.step(assertion_name):

        def make_attachment(attachment_expected_value, attachment_actual_value, attachment_operation):
            allure.attach(f"Ожидаемое значение: [{type(attachment_expected_value).__name__}] "
                          f"{str(attachment_expected_value)}\n"
                          f"Фактическое значение: [{type(attachment_actual_value).__name__}] "
                          f"{str(attachment_actual_value)}\n"
                          f"Операция: {attachment_operation}",
                          "Детали сравнения")

        match mode:

            case AssertionModes.VALUES_ARE_EQUAL:
                try:
                    operation = 'Проверка эквивалентности значений'
                    assert expected_value == actual_value
                    make_attachment(expected_value, actual_value, operation)
                except Exception as e:
                    make_attachment(expected_value, actual_value, operation)
                    raise AssertionError(
                        f"Значения сравнения \"{assertion_name}\" должны быть эквивалентны.\n{e}"
                    )

            case AssertionModes.VALUES_ARE_NOT_EQUAL:
                try:
                    operation = 'Проверка отсутствия эквивалентности значений'
                    assert expected_value != actual_value
                    make_attachment(expected_value, actual_value, operation)
                except Exception as e:
                    make_attachment(expected_value, actual_value, operation)
                    raise AssertionError(
                        f"Значения сравнения \"{assertion_name}\" не должны быть эквивалентны.\n{e}"
                    )

            case AssertionModes.EXPECTED_VALUE_GREATER_THAN_ACTUAL:
                try:
                    operation = 'Проверка большинства ожидаемого значения над фактическим значением'
                    assert expected_value > actual_value
                    make_attachment(expected_value, actual_value, operation)
                except Exception as e:
                    make_attachment(expected_value, actual_value, operation)
                    raise AssertionError(
                        f"Фактическое значение сравнения \"{assertion_name}\" должно быть меньше ожидаемого.\n{e}"
                    )

            case AssertionModes.EXPECTED_VALUE_GREATER_THAN_ACTUAL_OR_EQUAL_TO_IT:
                try:
                    operation = 'Проверка большинства ожидаемого значения над фактическим значением либо равенства ему'
                    assert expected_value >= actual_value
                    make_attachment(expected_value, actual_value, operation)
                except Exception as e:
                    make_attachment(expected_value, actual_value, operation)
                    raise AssertionError(
                        f"Фактическое значение сравнения \"{assertion_name}\" должно быть меньше ожидаемого либо равно "
                        f"ему.\n{e}"
                    )

            case AssertionModes.ACTUAL_VALUE_GREATER_THAN_EXPECTED:
                try:
                    operation = 'Проверка большинства фактического значения над ожидаемым значением'
                    assert expected_value < actual_value
                    make_attachment(expected_value, actual_value, operation)
                except Exception as e:
                    make_attachment(expected_value, actual_value, operation)
                    raise AssertionError(
                        f"Фактическое значение сравнения \"{assertion_name}\" должно быть больше ожидаемого.\n{e}"
                    )

            case AssertionModes.ACTUAL_VALUE_GREATER_THAN_EXPECTED_OR_EQUAL_TO_IT:
                try:
                    operation = 'Проверка большинства фактического значения над ожидаемым значением либо равенства ему'
                    assert expected_value <= actual_value
                    make_attachment(expected_value, actual_value, operation)
                except Exception as e:
                    make_attachment(expected_value, actual_value, operation)
                    raise AssertionError(
                        f"Фактическое значение сравнения \"{assertion_name}\" должно быть больше ожидаемого либо равно "
                        f"ему.\n{e}"
                    )

            case _:
                raise ValueError(
                    f"Режим сравнения \"{mode}\" не является допустимым."
                )


def make_bulk_assertion(data: list[AssertionBundle], group_name: str = "Сравнение группы данных"):
    with allure.step(group_name):
        for bundle in data:
            make_simple_assertion(
                expected_value=bundle.expected_value,
                actual_value=bundle.actual_value,
                assertion_name=bundle.assertion_name,
                mode=bundle.assertion_mode
            )
