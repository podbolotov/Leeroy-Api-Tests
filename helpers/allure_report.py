import allure
import json
from requests import Response
from helpers.json_tools import format_json, is_json


def attach_request_data_to_report(response: Response):
    with allure.step("Данные запроса и ответа"):
        request_string = f"URL: {response.url}\n"
        request_string = request_string + f"Method: {response.request.method}\n"
        request_string = request_string + f"Headers:\n{format_json(json.dumps(dict(response.request.headers)))}\n"

        if is_json(response.request.body):
            request_string = request_string + f"Body:\n{format_json(response.request.body)}"
        elif isinstance(response.request.body, str):
            request_string = request_string + f"Body:\n{response.request.body}"
        else:
            request_string = request_string + f"Body: Request has no body\n"

        allure.attach(request_string, "Данные запроса")

        response_string = f"Status: {response.status_code}\n"
        response_string = response_string + f"Headers:\n{format_json(json.dumps(dict(response.headers)))}\n"

        if is_json(response.content):
            response_string = response_string + f"Body:\n{format_json(response.content)}"
        elif isinstance(response.content, str):
            response_string = response_string + f"Body:\n{str(response.content)}"
        else:
            response_string = response_string + f"Body: Response has no body\n"

        allure.attach(response_string, "Данные ответа")
