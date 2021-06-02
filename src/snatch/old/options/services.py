from django.db import DatabaseError

from snatch.old.exceptions import DataException
from utilities.command.general_functions import is_uuid
from utilities.serializer_utils_regular import filter_for_model


def capitalize_name(name):
    """
    Конкатенация слов, делая первую букву каждого слова заглавной
    :param name: строка для преобразования
    :return: преобразованная строка
    """
    if "_" in name:
        name = name.split("_")
    else:
        name = [name]
    return "".join([line.capitalize() for line in name])


def search_fk_in_data(data, attribute):
    """
    Поиск атрибута в описании сущности (info) и получение наименования модели,
    на которую ссылается данный атрибут
    :param data: описание сущности (info)
    :param attribute: системное наименование атрибута
    :return: наименовние модели, наименование схемы
    """
    for line in data:
        if line["systemName"] == attribute and line["reference"]:
            return line["reference"]["modelName"], line["reference"]["schema"]
    return None, None


def method_get(data, model, many=False, count=False):
    """
    Получение списка, экземпляра или количества элементов из модели.
    :param data: параметры фильтрации
    :param model: модель
    :param many: признак множественности (False - возвращать один элемент, True - возвращать множество)
    :param count: признак подсчета количества элементов (False - не производить подсчет, True - произвести подсчет)
    :return: список, экземпляр или число
    """
    if count:
        return filter_for_model(model=model, data=data, many=many).count()
    return filter_for_model(model=model, data=data, many=many)


def queryset_instance(data, model):
    """
    Преобразование и сбор данных для модели.
    :param data: данные
    :param model: модель
    :param many: признак множественности
    :return: экземпляр
    """
    post_keys = [f.name for f in model._meta.fields]
    post_data = {key: data[key] for key in data.keys() if key in post_keys}
    return post_data


def create_instance(data, model):
    """
    Создание записи в БД.
    :param data: данные
    :param model: модель
    :return: экземпляр
    """
    try:
        instance = model.objects.create(**data)
    except DatabaseError as ex:
        message = "ошибка в данных {}".format(ex)
        raise DataException(message)
    return instance


def get_or_create_instance(data, model, default_data=None):
    """
    Создание или получение записи из модели.
    :param data: данные для поиска записи
    :param model: модель
    :param default_data: данные для создания модели
    :return: экземпляр
    """
    try:
        pk_name = model._meta.pk.name
        if pk_name in data and not data[pk_name]:
            data.pop(pk_name)
        if default_data:
            instance, _ = model.objects.get_or_create(**data, defaults=default_data)
        else:
            instance, _ = model.objects.get_or_create(**data)
    except DatabaseError as ex:
        message = "ошибка в данных {}".format(ex)
        raise DataException(message)
    return instance


def update_or_create_instance(data, model, default_data=None):
    """
    Обновление или получение записи из модели
    :param data: данные для поиска записи
    :param model: модель
    :param default_data: данные для создания или обновления модели
    :return: экземпляр
    """
    try:
        pk_name = model._meta.pk.name
        if pk_name in data and not data[pk_name]:
            data.pop(pk_name)
        if pk_name in default_data and not default_data[pk_name]:
            default_data.pop(pk_name)
        if default_data:
            instance, _ = model.objects.update_or_create(**data, defaults=default_data)
        else:
            instance, _ = model.objects.update_or_create(**data)
    except DatabaseError as ex:
        message = "ошибка в данных {}".format(ex)
        raise DataException(message)
    return instance


def update_instance(instance, data, model, put_keys=None):
    """
    Обновление экзмпляра в БД с проверкой на то, что хотя бы одино поле изменилось.
    :param instance: экземпляр
    :param data: данные
    :param model: модель
    :param put_keys: ключи, которые необходимо изменить
    :return: экземпляр
    """
    try:
        if not put_keys:
            put_keys = [f.name for f in model._meta.fields]
        data = {key: data[key] for key in data.keys() if key in put_keys}
        flag_change = False
        for key, value in data.items():
            if getattr(instance, key) != value:
                flag_change = True
                setattr(instance, key, value)
        if flag_change:
            instance.save()
    except DatabaseError as ex:
        message = "ошибка в данных {}".format(ex)
        raise DataException(message)

    return instance


def drop_instance(instance):
    """
    Логическое удаление экземпляра.
    :param instance: экземпляр
    :return: измененный экземпляр
    """
    try:
        instance.deleted = True
        instance.save()

        # TODO проверка на то, что нет неудаленных элементов
    except DatabaseError as ex:
        message = "ошибка в данных {}".format(ex)
        raise DataException(message)

    return instance


def get_by_uuid(obj, model):
    """
    Функция позволяет получить объект модели, если входящие данные - это uuid
    :param obj: идентфикатор (или объект)
    :param model: модель
    :return: объект модели
    """
    try:
        return model.objects.get(pk=obj) if is_uuid(obj) else obj
    except model.DoesNotExist:
        message = "не существует объекта сущности {} с идентификатором {}".format(
            model._meta.verbose_name, obj
        )
        raise DataException(message)
