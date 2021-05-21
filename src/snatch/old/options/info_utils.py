import re

from django.contrib.postgres.fields import JSONField
from django.db import models

INFO_SERVICE_LIST = {
    "GET": {
        "parameterType": "FILTER",
        "httpMethod": "GET",
        "responseContentType": "application/json",
        "systemName": "getList",
        "path": "/list"
    },
    "POST": {
        "parameterType": "DTO_LIST",
        "httpMethod": "POST",
        "responseContentType": "application/json",
        "systemName": "saveList",
        "path": "/list"
    },
    "PUT": {
        "parameterType": "DTO_LIST",
        "httpMethod": "PUT",
        "responseContentType": "application/json",
        "systemName": "updateList",
        "path": "/list"
    },
    "DELETE": {
        "parameterType": "FILTER",
        "httpMethod": "DELETE",
        "responseContentType": "application/json",
        "systemName": "deleteList",
        "path": "/list"
    }
}

INFO_SERVICE_DETAIL = {
    "GET": {
        "parameterType": "FILTER",
        "httpMethod": "GET",
        "responseContentType": "application/json",
        "systemName": "getEntity",
        "path": "/"
    },
    "POST": {
        "parameterType": "DTO",
        "httpMethod": "POST",
        "responseContentType": "application/json",
        "systemName": "save",
        "path": "/"
    },
    "PUT": {
        "parameterType": "DTO",
        "httpMethod": "PUT",
        "responseContentType": "application/json",
        "systemName": "update",
        "path": "/"
    },
    "DELETE": {
        "parameterType": "FILTER",
        "httpMethod": "DELETE",
        "responseContentType": "application/json",
        "systemName": "delete",
        "path": "/"
    }
}

INFO_SERVICE_SIZE = {
    "GET": {
        "parameterType": "FILTER",
        "httpMethod": "GET",
        "responseContentType": "text/plain",
        "systemName": "getListSize",
        "path": "/size"
    }
}

INFO_REPO = {
    "name": "Дистрибутив",
    "semanticLinks": None,
    "version": None,
    "systemName": "iso",
    "type": "resource",
    "schema": "repo",
    "modelName": "iso",
    "service": {
        "path": "/rest/repo/iso",
        "methods": [
            {
                "parameterType": "FILTER",
                "httpMethod": "GET",
                "responseContentType": "application/json",
                "systemName": "getList",
                "path": "/list"
            },
            {
                "parameterType": "FILTER",
                "httpMethod": "GET",
                "responseContentType": "application/json",
                "systemName": "getEntity",
                "path": "/"
            },
            {
                "parameterType": "DTO",
                "httpMethod": "POST",
                "responseContentType": "application/json",
                "systemName": "save",
                "path": "/"
            }
        ]
    },
    "attributes": [
        {
            "access": None,
            "alias": None,
            "idField": True,
            "systemName": "s_id",
            "reference": None,
            "type": "uuid",
            "name": "Идентификатор"
        },
        {
            "access": None,
            "alias": None,
            "idField": False,
            "systemName": "name",
            "reference": None,
            "type": "character varying",
            "name": "Наименование"
        }
    ]
}


def to_info(view_name, schema, model_name, search_attribute=False):
    """
    Получение информации о информационном ресурсе:
        список атрибутов
        список сервисов с разрешнными методами
    :param view_name: наименование предстваления
    :param schema: схема
    :param model_name: наименование модели
    :param search_attribute: признак поиска атрибута: если True, то список сервисов не рассматриваются
    :return: информация о информационном ресурсе
    """
    module = __import__("{}.serializers".format(schema), fromlist="schema.serializers")
    serializer = getattr(module, "{}Serializer".format(model_name))

    data = dict()
    data["name"] = serializer.Meta.model._meta.verbose_name
    data["semanticLinks"] = None
    data["version"] = None
    if serializer.Meta.model._meta.db_table.find("\".\"") > 0:
        data["systemName"] = serializer.Meta.model._meta.db_table.split("\".\"")[1]
    else:
        data["systemName"] = serializer.Meta.model._meta.db_table
    data["type"] = "classifier" if "classifier" in schema else "resource"
    data["schema"] = schema
    model_class_name = re.sub(r"([A-Z])", r" \1", serializer.Meta.model.__name__).split()[:-1]
    data["modelName"] = "_".join([f.lower() for f in model_class_name])

    if not search_attribute:
        module = __import__("{}.views".format(schema), fromlist="schema.views")
        class_list = getattr(module, "{}List".format(model_name))
        class_detail = getattr(module, "{}Detail".format(model_name))
        class_size = getattr(module, "{}Size".format(model_name))

        data["service"] = {
            "path": '/'.join(view_name.split("/")[:-2]),
            "methods": list()
        }
        class_list = [[class_list, INFO_SERVICE_LIST],
                      [class_detail, INFO_SERVICE_DETAIL],
                      [class_size, INFO_SERVICE_SIZE]]

        allowed_methods = list()
        for line in class_list:
            if line[0]:
                allowed_methods.extend(line[0]().allowed_methods)
                for method_key in line[1].keys():
                    if method_key in allowed_methods:
                        data["service"]["methods"].append(line[1][method_key])

    data["attributes"] = list()
    field_list = serializer.Meta.fields
    for field in field_list:
        model_field, is_field, type_ref = get_info_in_model_by_serializer(field, serializer.Meta.model)
        line = dict()
        line["access"] = None
        line["alias"] = None
        line["idField"] = True if field in ["id", "s_id", "guid"] else False
        line["systemName"] = field
        line["reference"] = None
        if model_field:
            if "id" == field or "_id" in field or "_list" in field:
                line["type"] = "uuid"
            else:
                types_list = [[models.TextField, "character varying"], [models.IntegerField, "integer"],
                              [models.BooleanField, "boolean"], [models.DateField, "date"],
                              [models.DateTimeField, "datetime"], [JSONField, "jsonb"], [models.FloatField, "float"]]
                for type_instance in types_list:
                    if isinstance(model_field, type_instance[0]):
                        line["type"] = type_instance[1]
                        break
            if not is_field:
                line["name"] = model_field._meta.verbose_name
                # line["schema"] = model_field._meta.db_table.split(".")[0]
                model_class_name = re.sub(r"([A-Z])", r" \1", model_field.__name__).split()[:-1]
                # line["modelName"] = "_".join([f.lower() for f in model_class_name])
                line["reference"] = {
                    "refType": type_ref,
                    "type": "resource" if "classifier" not in model_field._meta.db_table else "classifier",
                    "schema": model_field._meta.db_table.split("\".\"")[0],
                    "systemName": model_field._meta.db_table.split("\".\"")[1],
                    "name": model_field._meta.verbose_name,
                    "modelName": "_".join([f.lower() for f in model_class_name]),
                    "direction": None
                }
            elif model_field.one_to_many:
                line["name"] = model_field.related_model._meta.verbose_name
                model_class_name = re.sub(r"([A-Z])", r" \1", model_field.related_model.__name__).split()[:-1]
                line["reference"] = {
                    "refType": type_ref,
                    "type": "resource" if "classifier" not in model_field.related_model._meta.db_table else "classifier",
                    "schema": model_field.related_model._meta.db_table.split("\".\"")[0],
                    "systemName": model_field.related_model._meta.db_table.split("\".\"")[1],
                    "name": model_field.related_model._meta.verbose_name,
                    "modelName": "_".join([f.lower() for f in model_class_name]),
                    "direction": None
                }
            elif model_field.many_to_one:
                line["name"] = model_field.verbose_name
                model_class_name = re.sub(r"([A-Z])", r" \1", model_field.related_model.__name__).split()[:-1]
                # line["modelName"] = "_".join([f.lower() for f in model_class_name])
                line["reference"] = {
                    "refType": type_ref,
                    "type": "resource" if "classifier" not in model_field.related_model._meta.db_table else "classifier",
                    "schema": model_field.related_model._meta.db_table.split("\".\"")[0],
                    "systemName": model_field.related_model._meta.db_table.split("\".\"")[1],
                    "name": model_field.related_model._meta.verbose_name,
                    "modelName": "_".join([f.lower() for f in model_class_name]),
                    "direction": None
                }
            else:
                line["name"] = model_field.verbose_name
        data["attributes"].append(line)
    return data


def get_info_in_model_by_serializer(field, model):
    """
    Получение информации по наименованию атрибута в сериализаторе по модели
    :param field: наименование поля из сериализатора
    :param model: модель
    :return: поле модели, признак поля, тип связи
    """
    try:
        model_field = model._meta.get_field(field)
        if not (model_field.one_to_many or model_field.many_to_many):
            return model_field, True, "MANY_TO_ONE"
        else:
            return model_field, True, "ONE_TO_MANY"
    except:
        rel_model_field_list = [f for f in model._meta.get_fields() if f.one_to_many or f.many_to_many]
        for rel_model_field in rel_model_field_list:
            if rel_model_field.related_model._meta.db_table.split("\".\"")[1] in field:
                return rel_model_field.related_model._meta.model, False, "ONE_TO_MANY"

        for rel_model_field in rel_model_field_list:
            model_field_list = rel_model_field.related_model._meta.get_fields()
            for model_field in model_field_list:
                if "_id" in model_field.name:
                    search_str = model_field.name.replace("_id", "")
                    if search_str in field:
                        return model_field, True, "MANY_TO_MANY"
    return None, None, None
