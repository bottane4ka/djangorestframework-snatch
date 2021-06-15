from collections import OrderedDict

from django.db.models import Manager
from django.http import HttpResponseRedirect
from rest_framework import status, mixins
from rest_framework.exceptions import ValidationError
from rest_framework.fields import SkipField, empty
from rest_framework.relations import PKOnlyObject
from rest_framework.response import Response
from rest_framework.reverse import reverse

from snatch.exceptions import GetObjectException, ModelFilterException
from snatch.options.info import SnatchInfo
from snatch.wrappers import add_link_many, add_link_one


class SnatchCreateModelMixin(mixins.CreateModelMixin):
    """Создание объекта модели

    """
    pass


class SnatchRetrieveModelMixin:
    """Получение объекта модели

    """
    def retrieve(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except (GetObjectException, ModelFilterException) as ex:
            return Response(data={"detail": str(ex)}, status=status.HTTP_404_NOT_FOUND)


class SnatchListModelMixin:
    """Получение списка объектов и их количества в списке

    """
    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except (GetObjectException, ModelFilterException) as ex:
            return Response(data={"detail": str(ex)}, status=status.HTTP_404_NOT_FOUND)

    def size(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            count = queryset.count() if queryset else 0
            return Response(count, status=status.HTTP_200_OK)
        except (GetObjectException, ModelFilterException) as ex:
            return Response(data={"detail": str(ex)}, status=status.HTTP_404_NOT_FOUND)


class SnatchUpdateModelMixin:
    """Обновление объекта модели

    """
    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_queryset(**kwargs)
            serializer = self.get_serializer(instance, data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except (GetObjectException, ModelFilterException) as ex:
            return Response(data={"detail": str(ex)}, status=status.HTTP_404_NOT_FOUND)

    def perform_update(self, serializer):
        serializer.save()


class SnatchDestroyModelMixin:
    """Удаление объекта модели

    """
    def destroy(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            self.perform_destroy(queryset)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except (GetObjectException, ModelFilterException) as ex:
            return Response(data={"detail": str(ex)}, status=status.HTTP_404_NOT_FOUND)

    def perform_destroy(self, instance):
        instance.delete()


class SnatchInfoModelMixin:
    """Получение информации о таблице с возможностью редиректа на родительскую таблицу

    """
    info_class = SnatchInfo

    def info(self, request, *args, **kwargs):
        data = self.info_class().determine_metadata(self)
        return Response(data, status=status.HTTP_200_OK)

    def info_redirect(self, request, *args, **kwargs):
        field_name = kwargs.get("pk")
        field_info = self.info_class().get_field_info_by_name(self, field_name)
        if not field_info:
            return Response(
                {"detail": f"Атрибута {field_name} не существует"},
                status=status.HTTP_404_NOT_FOUND,
            )
        reference = field_info.get("reference")
        if not reference:
            return Response(field_info, status=status.HTTP_200_OK)
        params = request.query_params
        view_name = f"{reference['schema']}_{reference['systemName']}_list"
        if params:
            params = ["{}={}".format(key, params[key]) for key in params.keys()]
            url = "{}?{}".format(reverse(view_name), "&".join(params))
        else:
            url = reverse(view_name)
        return HttpResponseRedirect(url)


class SnatchOptionsModelMixin:
    """Получение информации через HTTP метод OPTIONS

    """
    def options(self, request, *args, **kwargs):
        data = self.info_class().determine_metadata(self)
        return Response(data, status=status.HTTP_200_OK)


class SnatchDeserializationMixin:
    """Десериализация объектов модели с учетом self и link.
    Преобразование вложенных структур в объекты модели.

    """
    def run_validation(self, data):
        model_field = (
            self.parent.Meta.model._meta.get_field(self.source) if self.parent else None
        )
        data = empty if not data else data
        if model_field and data and isinstance(data, dict) and model_field.many_to_one:
            if "self" in data.keys():
                data = data["self"]
            pk_name = model_field.related_model._meta.pk.name
            pk_data = data.get(pk_name)
            if not pk_data:
                raise ValidationError(detail=f"KeyError, key '{pk_name}' not found.")
            try:
                validated_value = model_field.related_model.objects.get(
                    **{pk_name: pk_data}
                )
            except model_field.related_model.DoesNotExist as ex:
                raise ValidationError(
                    detail=f"Destination {data} matching query does not exist."
                )
        else:
            validated_value = super(SnatchDeserializationMixin, self).run_validation(
                data
            )

        return validated_value


class SnatchSerializationMixin:
    """Сериализация объекта модели с добавлением self и link.

    """
    @add_link_one
    def to_representation(self, instance):
        ret = OrderedDict()
        fields = self._readable_fields
        model = instance._meta.model
        for field in fields:
            try:
                attribute = field.get_attribute(instance)
            except SkipField:
                continue

            check_for_none = (
                attribute.pk if isinstance(attribute, PKOnlyObject) else attribute
            )
            if check_for_none is None:
                model_field = model._meta.get_field(field.source)
                ret[field.field_name] = (
                    {"link": None, "self": None} if model_field.is_relation else None
                )
            else:
                ret[field.field_name] = field.to_representation(attribute)

        return ret


class SnatchListSerializerMixin:
    """Сериализация списка объектов модели с добавлением self и link.

    """
    @add_link_many
    def to_representation(self, data):
        iterable = data.all() if isinstance(data, Manager) else data

        return [self.child.to_representation(item) for item in iterable]

    def run_validation(self, data=empty):
        related_manager = getattr(self.parent.instance, self.source, None)
        value = related_manager.all()
        self.run_validators(value)
        return value
