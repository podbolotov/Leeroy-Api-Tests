import json
from json import JSONDecodeError


def format_json(json_str):
    json_obj = json.loads(json_str)
    json_str_formatted = json.dumps(json_obj, indent=3, ensure_ascii=False)
    return json_str_formatted


def is_json(myjson):
    try:
        json.loads(myjson)
    except ValueError:
        return False
    except TypeError:
        return False
    return True
