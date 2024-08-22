import json
import allure
from pydantic import ValidationError
from helpers.json_tools import format_json


def validate_response_model(model, data: str):
    try:
        serialized_model = model.model_validate(data, strict=True)
        with allure.step("Валидация модели пройдена"):
            allure.attach(f"Использована модель: {model.__name__}\n"
                          f"Описание модели:{model.__doc__}",
                          "Детали валидации")
        return serialized_model
    except ValidationError as e:
        with allure.step("Валидация модели не пройдена"):
            allure.attach(f"Использована модель: {model.__name__}\n"
                          f"Описание модели:{model.__doc__}",
                          "Детали валидации")
            with allure.step("Ошибки валидации"):
                errors_list = e.errors()
                for error in errors_list:
                    error_as_json = json.dumps(error, indent=4)
                    allure.attach(format_json(error_as_json), f"{error['msg']} : {error['loc']}")
                raise AssertionError(f"Обнаружено ошибок валидации: {e.error_count()}")
