from . import mixins
from rest_framework.viewsets import GenericViewSet
from .exceptions import GetObjectException, FilterException


class CustomGenericViewSet(GenericViewSet):
    def get_params(self):
        params = {key: item for key, item in self.request.query_params.items()}
        params["many"] = True if self.action in ["list"] else False
        return params

    def get_queryset(self):
        queryset = GenericViewSet.get_queryset(self)
        model_name = queryset.model._meta.object_name
        params = self.get_params()

        many = params.pop("many", False)
        limit = params.pop("limit", None)
        offset = params.pop("offset", None)
        order = params.pop("order", None)
        format = params.pop("format", None)
        max_level = int(params.pop("max_level", 1))
        level = params.pop("level", None)

        # TODO Добавить нормальный парсинг параметров фильтрации
        # TODO в зависимости от уровня вложенности указывать select_related

        if max_level > 0 and not level:
            select_related_list = [
                field.name
                for field in queryset.model._meta.get_fields()
                if field.many_to_one
            ]
            if select_related_list:
                queryset = queryset.select_related(*select_related_list)

        if not many:
            if not params:
                raise GetObjectException(model_name, "no_filter")
            try:
                queryset = queryset.get(**params)
            except queryset.model.DoesNotExist:
                raise GetObjectException(model_name, "not_found")
            except queryset.model.MultipleObjectsReturned:
                raise GetObjectException(model_name, "many_found")
        else:
            if params:
                try:
                    queryset = queryset.filter(**params)
                except Exception as ex:
                    raise FilterException(model_name, ex)
        return queryset

    def get_serializer_context(self):
        data = {
            key: self.request.query_params[key]
            for key in ["max_level", "level"]
            if key in self.request.query_params
        }
        data.update(
            {"request": self.request, "format": self.format_kwarg, "view": self}
        )
        return data


class CustomReadOnlyModelViewSet(
    mixins.CustomRetrieveModelMixin, mixins.CustomListModelMixin, CustomGenericViewSet
):
    pass


class CustomModelViewSet(
    mixins.CustomCreateModelMixin,
    mixins.CustomRetrieveModelMixin,
    mixins.CustomUpdateModelMixin,
    mixins.CustomDestroyModelMixin,
    mixins.CustomListModelMixin,
    CustomGenericViewSet,
):
    pass
