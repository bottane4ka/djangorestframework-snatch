from django.db.models import Model, Field
from rest_framework.reverse import reverse
from rest_framework.serializers import ModelSerializer


def get_link_many(field: Field, instance: Model) -> str:
    """Получение ссылки для множества объектов

    Args:
        field: поле дочерней модели, которое ссылается на родительскую модель
        instance: объект родительской модели

    Returns:
        ссылка на список дочерних объектов
    """
    table_schema, table_name = field.model._meta.db_table.split('"."')
    url = reverse(f"{table_schema}_{table_name}_list")
    return f"{url}?query={field.name}.eq.{instance.pk}"


def get_link_one(serializer: ModelSerializer, instance: Model) -> str:
    """Получение ссылки для одного объекта

    Args:
        serializer: сериализатор
        instance: объект модели

    Returns:
        ссылка на объект
    """
    pk_name = instance._meta.pk.name
    table_schema, table_name = serializer.Meta.model._meta.db_table.split('"."')
    url = reverse(f"{table_schema}_{table_name}_detail")
    return f"{url}?query={pk_name}.eq.{instance.pk}"
