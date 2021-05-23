from re import search

from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.db.models import Q
from rest_framework.exceptions import APIException

from snatch.old.exceptions import FilterParseException
from .parse_qs import QSParser

FILTER_CONDITION = ["and", "or", "not"]

FILTER_INSTANCE = {
    "eq": "exact",
    "gt": "gt",
    "gte": "gte",
    "lt": "lt",
    "lte": "lte",
    "like": "contains",
    "re": "regex",
    "in": "in",
    "is": "is",
    "year": "year",
    "month": "month",
    "day": "day",
    "ov": "overlap",
    "between": "range",
    "asc": "",
    "desc": "-",
    "isnull": "isnull"
}


def filter_for_model(**kwargs):
    model = kwargs.get("model")
    data = dict(kwargs.get("data", None))
    many = kwargs.get("many", False)

    try:
        limit = int(data.pop("limit", [0])[0])
        offset = int(data.pop("offset", [0])[0])
        order_by = data.pop("order", None)
        distinct = data.pop("distinct", False)
        data.pop('format', None)
        data.pop('max_level', None)

        filter_info = None
        if data:
            main_key = "and"
            value = None
            if len(data.keys()) == 1:
                for key in data.keys():
                    if key in FILTER_CONDITION:
                        main_key = key
                        value = data[main_key][0][1:-1]
                        break

            if not value:
                value = [
                    "{}{}".format(
                        key,
                        ".{}".format(
                            item[0]) if item[0] else "") for key,
                    item in data.items()]
                value = ",".join(value)

            value = "{}({})".format(main_key, value)

            parse_dict = QSParser(value)
            parse_dict = parse_dict.result
            filter_info = to_Q(parse_dict, model, main_key)

        order_info = list()
        if order_by:
            order_by = order_by[0]
            order_info = to_order(order_by, model)
            # order = FilterParser(model)
            # order.filter_to_tree(order_by)
            # order = order.tree
            # for line in order.get_instance():
            #     line.to_Q()
            # line.set_dj_attribute()
            # order_info.append(line.get_dj_attribute())
    except FilterParseException as ex:
        raise APIException(ex)

    try:
        if many:
            if order_info:
                model = model.objects.all().order_by(*order_info)
            else:
                model = model.objects.all()
            if filter_info:
                model = model.filter(filter_info)
            if distinct:
                model = model.distinct()
            if limit > 0:
                return model[offset:limit + offset]
            else:
                return model[offset:]
        else:
            if filter_info:
                try:
                    if distinct:
                        model = model.objects.filter(filter_info).distinct()
                        if model.count() == 0:
                            raise FilterParseException(
                                "Ошибка: не существует объекта с данными параметрами фильтрации")
                        elif model.count() == 1:
                            return model[0]
                        else:
                            raise FilterParseException(
                                "Ошибка: запрос с данными параметрами фильтрации возвращает список значений. "
                                "Используйте /list.")
                    return model.objects.get(filter_info)
                except ObjectDoesNotExist as ex:
                    raise FilterParseException(
                        "Ошибка: не существует объекта с данными параметрами фильтрации")
                except MultipleObjectsReturned as ex:
                    raise FilterParseException(
                        "Ошибка: запрос с данными параметрами фильтрации возвращает список значений."
                        " Используйте /list.")
            else:
                raise FilterParseException("Ошибка: нет параметров фильтрации")
    except FilterParseException as ex:
        raise APIException(ex)
    except Exception as ex:
        raise APIException("Неизвестная ошибка: {}".format(ex))


def check_attribute_array(attribute_list, model):
    """
    Проверка на валидность списка атрибутов для поиска
    :return: -
    """
    for i in range(len(attribute_list)):
        attribute = attribute_list[i]
        if 'pk' == attribute:
            attribute = model._meta.pk.name
        field_list = [field.name for field in model._meta.get_fields()]
        # Если атрибут существует в списке атрибутов модели, значит все верно
        if attribute in field_list:
            field = model._meta.get_field(attribute)
            # Если атрибут является ссылкой, то сохраняем модель, на которую ссылается атрибут
            # Иначе атрибут не является ссылкой, значит либо данный атрибут в списке последний и все хорошо,
            # либо атрибут не последний и пользователь ошибся с параметрами
            # фильтрации
            if field.many_to_one or field.one_to_many:
                model = field.related_model
            else:
                if i != len(attribute_list) - 1:
                    raise FilterParseException(
                        "Атрибут {} является конечной точкой поиска".format(attribute))
                else:
                    return True
        else:
            raise FilterParseException(
                "Не существует атрибута {} в информационном ресурсе {}".format(
                    attribute, model._meta.verbose_name))
    return True


def like_resolver(value):
    """
    Эта функция запускается в случае если оригинальный operator == 'like'.
    Производится проверка value на наличие звездочки и выбор соответствующего ключевого слова для operator
    *dir = endswith
    dir* = startswith
    *dir* = contains
    dir = exact

    :param value:
    :return: (ключевое_слово_operator'а, очищенное_от_звездочек_value)
    """
    lookups = [
        (r'^[^\*]*$', 'exact', value),
        (r'^\*.*\*$', 'contains', value[1:-1]),
        (r'^\*.*$', 'endswith', value[1:]),
        (r'^.*\*$', 'startswith', value[:-1])
    ]
    for pattern, operator, val in lookups:
        if search(pattern, value):
            return operator, val


def check_operator(operator, value):
    """
    Проверка на валидность оператора
    :return: -
    """
    if operator not in FILTER_INSTANCE.keys():
        raise FilterParseException(
            "Неверная операция фильтрации {}. Введите одно из значений: {}".format(
                operator, ", ".join(
                    FILTER_INSTANCE.keys())))
    if value in ["desc", "asc"]:
        operator = value
    elif operator == "is":
        ntf = {
            "true": [
                "", True], "false": [
                "", False], "null": [
                "isnull", True]}
        if value in ntf.keys():
            operator, value = ntf[value]
        else:
            raise FilterParseException(
                "Неверные параметры фильтрации: для оператора is значение должно быть равно {}".format(
                    ", ".join(
                        ntf.keys())))

    elif operator == "eq" and value == "null":
        operator, value = "isnull", True

    elif operator == 'like':
        operator, value = like_resolver(value)

    else:
        operator = FILTER_INSTANCE[operator]

    return operator, value


def to_Q(data, model, main_key):
    new_data = list()
    query = Q()
    for line in data:
        for key in line.keys():
            if key not in FILTER_CONDITION:
                key_split = key.split("__")
                check_attribute_array(key_split[:-1], model)
                operator, value = check_operator(key_split[-1], line[key])
                new_key = "__".join(key_split[:-1])
                if operator != "":
                    new_key = "{}__{}".format(new_key, operator)
                new_data.append({new_key: value})
            else:
                if key in ["and", "not"]:
                    query &= to_Q(line[key], model, key)
                elif key == "or":
                    query |= to_Q(line[key], model, key)

    if main_key in ["and", "not"]:
        new_simple_dict = dict()
        if new_data:
            for line in new_data:
                for key in line.keys():
                    new_simple_dict[key] = line[key]
            query &= Q(**new_simple_dict)
    elif main_key == "or":
        if new_data:
            for line in new_data:
                query |= Q(**line)
    return ~Q(query) if main_key == "not" else Q(query)


def to_order(data, model):
    new_data = list()
    data = data.split(",") if "," in data else [data]
    for line in data:
        if "." in line:
            line = line.split(".")
        else:
            if line not in FILTER_INSTANCE.keys():
                raise FilterParseException(
                    "Неверные параметры сортировки: укажите направление сортировки desc или asc")
            else:
                raise FilterParseException(
                    "Неверные параметры сортировки: укажите атрибут для сортировки")

        check_attribute_array(line[:-1], model)
        operator = line[-1]
        if operator not in FILTER_INSTANCE.keys():
            raise FilterParseException(
                "Неверные параметры сортировки: укажите направление сортировки desc или asc")

        attribute = "-{}".format("__".join(line[:-1])
                                 ) if operator == "desc" else "__".join(line[:-1])
        new_data.append(attribute)
    return new_data
