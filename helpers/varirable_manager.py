class VariableManager:
    """
    Данный класс представляет собой менеджер переменных,
    который может хранить переменные на протяжении всей сессии.
    """
    def __init__(self):
        self.info = "Hello from variable manager!"

    def set(self, name: str, value):
        setattr(self, name, value)

    def get(self, name):
        return getattr(self, name)

    def unset(self, name):
        delattr(self, name)
