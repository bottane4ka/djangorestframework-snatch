class GetObjectException(Exception):
    """ Ошибка получения объекта. """

    _error_type_list = {
        "not_found": "объект не найден",
        "no_filter": "не указаны параметры фильтрации",
        "many_found": "найдено больше одного объекта",
    }

    def __init__(self, class_name, error_type=None, ex=None):
        self.message = (
            self._error_type_list.get(error_type, None) if error_type else None
        )
        self.class_name = class_name
        self.ex = ex

    def __str__(self):
        if not self.message and not self.ex:
            return f"<GetObjectException> Неизвестная ошибка получения объекта из модели {self.class_name}."
        elif not self.message and self.ex:
            return f"<GetObjectException> Неизвестная ошибка получения объекта из модели {self.class_name}: {self.ex}."
        return f"<GetObjectException> Ошибка получения объекта из модели {self.class_name}: {self.message}."


class ModelFilterException(Exception):
    def __init__(self, class_name, ex):
        self.class_name = class_name
        self.ex = ex

    def __str__(self):
        return f"<ModelFilterException> Ошибка в параметрах фильтрации для модели {self.class_name}: {self.ex}."


class FilterException(Exception):
    """ Ошибка при построении параметров фильтрации. """

    def __init__(self, input_string):
        self.input_string = input_string


class BracketsError(FilterException):
    """ Ошибка при валидации скобок. """

    def __str__(self):
        return f"<BracketsError> Невалидное количество скобок в строке {self.input_string}."


class AttributesException(FilterException):
    """ Ошибка при валидации атрибутов модели. """

    def __init__(self, attribute, model_name):
        self.attribute = attribute
        self.model_name = model_name


class OperatorsException(FilterException):
    def __init__(self, operator, value):
        self.operator = operator
        self.value = value


class EndAttributeError(AttributesException):
    def __str__(self):
        return f"<EndAttributeError> Атрибут {self.attribute} является конечной точкой поиска."


class NoAttributeInModelError(AttributesException):
    def __str__(self):
        return f"<NoAttributeInModelError> Не существует атрибута {self.attribute} в модели {self.model_name}."


class NotValidOperatorError(OperatorsException):
    def __str__(self):
        return f"<NotValidOperatorError> Неверная оператор для фильтрации: {self.operator}."
