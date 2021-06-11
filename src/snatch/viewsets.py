import typing as t

from django.conf import settings
from django.db.models import Model, Q, QuerySet
from rest_framework.viewsets import GenericViewSet

from snatch import mixins
from snatch.exceptions import GetObjectException, ModelFilterException, FilterException
from snatch.search.parse_qs import StrongCreator


class SnatchGenericViewSet(GenericViewSet):

    page_size = settings.REST_FRAMEWORK.get("PAGE_SIZE", 20)

    def get_params(self):
        params = {
            "query": self.request.query_params.get("query", None),
            "order": self.request.query_params.get("order", None),
            "offset": int(self.request.query_params.get("offset", 0)),
            "limit": int(self.request.query_params.get("limit", self.page_size)),
            "distinct": True
            if "distinct" in self.request.query_params.keys()
            else False,
            "max_level": int(self.request.query_params.get("max_level", 1)),
            "level": self.request.query_params.get("level", None),
            "many": True if self.action in ["list", "size"] else False,
        }
        return params

    def get_queryset(self):
        queryset = GenericViewSet.get_queryset(self)
        model = queryset.model
        params = self.get_params()
        filter_ = self._get_filter(params, model)

        # TODO в зависимости от уровня вложенности указывать select_related

        return self._init_router(params["many"])(queryset, params, filter_)

    def get_serializer_context(self):
        params = self.get_params()
        data = {key: params[key] for key in ["max_level", "level"] if key in params}
        data.update(
            {"request": self.request, "format": self.format_kwarg, "view": self}
        )
        return data

    def _get_filter(self, params: t.Dict, model: Model) -> Q:
        try:
            filter_string = params.get("query")
            if filter_string:
                return StrongCreator()(filter_string, model)
        except FilterException as ex:
            raise ModelFilterException(model._meta.object_name, ex)

    def _get_order(self, params: t.Dict, model: Model) -> t.List[str]:
        try:
            order_string = params.get("order")
            if order_string:
                return StrongCreator()(order_string, model, is_filter=False)
        except FilterException as ex:
            raise ModelFilterException(model._meta.object_name, ex)

    def _init_router(self, many) -> t.Callable:
        return self._init_one if not many else self._init_many

    def _init_one(self, queryset: QuerySet, params: t.Dict, filter_: Q) -> QuerySet:
        model_name = queryset.model._meta.object_name

        if not filter_:
            raise GetObjectException(model_name, "no_filter")

        error_name = None
        if "distinct" in params.keys():
            queryset = queryset.filter(filter_).distinct()
            if queryset.count() == 0:
                error_name = "not_found"
            elif queryset.count() > 1:
                error_name = "many_found"
        else:
            try:
                queryset = queryset.get(filter_)
            except queryset.model.DoesNotExist:
                error_name = "not_found"
            except queryset.model.MultipleObjectsReturned:
                error_name = "many_found"

        if error_name:
            raise GetObjectException(model_name, error_name)
        return queryset

    def _init_many(self, queryset: QuerySet, params: t.Dict, filter_: Q) -> QuerySet:
        model_name = queryset.model._meta.object_name

        order_ = self._get_order(params, queryset.model)
        try:
            if filter_:
                queryset = queryset.filter(filter_)
            if params.get("distinct"):
                queryset = queryset.distinct()
            if order_:
                queryset = queryset.order_by(*order_)
            if "limit" in params or "offset" in params:
                queryset = queryset[
                    params.get("offset") : params.get("limit") + params.get("offset")
                ]
        except Exception as ex:
            raise GetObjectException(model_name, ex=ex)
        return queryset


class SnatchReadOnlyModelViewSet(
    mixins.SnatchInfoModelMixin,
    mixins.SnatchOptionsModelMixin,
    mixins.SnatchRetrieveModelMixin,
    mixins.SnatchListModelMixin,
    SnatchGenericViewSet,
):
    pass


class SnatchModelViewSet(
    mixins.SnatchInfoModelMixin,
    mixins.SnatchOptionsModelMixin,
    mixins.SnatchCreateModelMixin,
    mixins.SnatchRetrieveModelMixin,
    mixins.SnatchUpdateModelMixin,
    mixins.SnatchDestroyModelMixin,
    mixins.SnatchListModelMixin,
    SnatchGenericViewSet,
):
    pass
