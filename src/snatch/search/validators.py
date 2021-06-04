import typing as t

from django.core.exceptions import FieldDoesNotExist
from django.db.models import Model

from snatch.exceptions import (
    BracketsError,
    NoAttributeInModelError,
    EndAttributeError,
    NotValidOperatorError,
)
from snatch.search.operators import converters
from snatch.search.operators.consts import DEFAULT_OPERATORS
from snatch.tuples import OperatorInfo

OPERATORS = _operator_dict = {
    operator[0]: OperatorInfo(*operator) for operator in DEFAULT_OPERATORS
}


def validate_brackets(input_str: str):
    """Валидация правильной последовательности скобок

    Args:
        input_str: входящая строка

    Returns:

    """
    if not (input_str and isinstance(input_str, str)):
        raise BracketsError(input_str)

    if not ("(" in input_str or ")" in input_str):
        return

    open_brackets, close_brackets = 0, 0
    for char in input_str:
        if char == "(":
            open_brackets += 1
        elif char == ")":
            close_brackets += 1
        if open_brackets < close_brackets:
            raise BracketsError(input_str)


def validate_attributes(attribute_list: t.List, model: Model):
    """Проверка на валидность списка атрибутов для поиска

    Args:
        attribute_list: список атрибутов
        model: модель Django для валидации

    Returns:

    """
    count_level = len(attribute_list)
    for i, attribute in enumerate(attribute_list):
        attribute = model._meta.pk.name if "pk" == attribute else attribute
        try:
            field = model._meta.get_field(attribute)
            if field.is_related:
                model = field.related_model
            elif i != count_level - 1:
                raise EndAttributeError(attribute, model._meta.name)
        except FieldDoesNotExist:
            raise NoAttributeInModelError(attribute, model._meta.name)


def validate_operators(operator: str, value: t.Any) -> t.Tuple[str, t.Any, bool]:
    """Валидация и преобразование оператора и значения оператора

    Args:
        operator: оператор
        value: значение оператора

    Returns:
        оператор, значение оператора, признак отрицания
    """
    if operator not in OPERATORS.keys():
        raise NotValidOperatorError(operator, value)
    func = getattr(converters, f"{operator}_convert", None)
    return func(value) if func else operator, value, False
