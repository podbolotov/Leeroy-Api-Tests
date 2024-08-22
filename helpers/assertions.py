import allure


def make_assertion(expected_value, actual_value, assertion_name: str):
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
