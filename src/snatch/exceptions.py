class GetObjectException(Exception):
    """ Ошибка получения объекта. """

    _error_type_list = {
        "not_found": "объект не найден",
        "no_filter": "не указаны параметры фильтрации",
        "many_found": "найдено больше одного объекта",
    }

    def __init__(self, class_name, error_type=None):
        self.message = (
            self._error_type_list.get(error_type, None) if error_type else None
        )
        self.class_name = class_name

    def __str__(self):
        if not self.message:
            return f"<GetObjectException> Неизвестная ошибка получения объекта из модели {self.class_name}."
        return f"<GetObjectException> Ошибка получения объекта из модели {self.class_name}: {self.message}."


class FilterException(Exception):
    """ Ошибка при построении параметров фильтрации. """

    def __init__(self, class_name, ex):
        self.class_name = class_name
        self.ex = ex

    def __str__(self):
        return f"<GetObjectException> Ошибка в параметрах фильтрации для модели {self.class_name}: {self.ex}."
