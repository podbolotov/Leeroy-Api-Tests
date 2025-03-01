from typing import Any


class VariableManager:
    """
    Данный класс представляет собой менеджер переменных,
    который может хранить переменные на протяжении всей сессии.
    """
    def __init__(self):
        self.info = "Hello from variable manager!"

    def set(self, name: str, value: Any) -> None:
        """
        Метод для создания переменной в менеджере переменных.
        Требует передачи названия переменной в виде строки и значения переменной (любого типа).

        Метод ничего не возвращает.

        :param name: Название создаваемой переменной
        :param value: Значение создаваемой переменной
        """
        setattr(self, name, value)

    def get(self, name: str) -> Any:
        """
        Метод для чтения переменной, ранее записанной в менеджере переменных.
        Требует передачи названия переменной, значение которой необходимо вернуть.

        Метод возвращает значение переменной (любого типа).

        :param name: Название запрашиваемой переменной
        :return: Содержимое запрошенной переменной
        """
        return getattr(self, name)

    def unset(self, name: str) -> None:
        """
        Метод для удаления переменной из менеджера переменных.
        Требует передачи названия переменной, которую необходимо удалить.

        Метод ничего не возвращает.

        :param name: Название удаляемой переменной.
        """
        delattr(self, name)
