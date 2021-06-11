from collections import OrderedDict

from django.contrib.postgres.fields import JSONField
from django.core.exceptions import PermissionDenied, FieldDoesNotExist
from django.db import models
from django.http import Http404
from rest_framework import exceptions, serializers
from rest_framework.request import clone_request
from rest_framework.utils.field_mapping import ClassLookupDict

from snatch.options.info_config import DEFAULT_METHODS_CONFIG
from snatch.options.schema import MethodsConfig


class SnatchInfo:
    label_lookup = ClassLookupDict(
        {
            JSONField: "jsonb",
            models.Field: "field",
            models.BooleanField: "boolean",
            models.NullBooleanField: "boolean",
            models.CharField: "character varying",
            models.UUIDField: "uuid",
            models.URLField: "character varying",
            models.EmailField: "character varying",
            models.SlugField: "slug",
            models.IntegerField: "integer",
            models.FloatField: "float",
            models.DecimalField: "decimal",
            models.DateField: "date",
            models.DateTimeField: "datetime",
            models.TimeField: "time",
            models.FileField: "file upload",
            models.ImageField: "image upload",
        }
    )

    ref_type_lookup = ("many_to_one", "one_to_one", "one_to_many", "many_to_many")
    methods_config = DEFAULT_METHODS_CONFIG

    def determine_metadata(self, request, view):
        model = view.queryset.model
        metadata = OrderedDict()
        metadata["name"] = self._get_name(model)
        metadata["version"] = None
        metadata["schema"], metadata["systemName"] = self._get_db_table_info(
            model._meta.db_table
        )
        metadata["attributes"] = self.get_serializer_info(view.get_serializer())
        metadata["service"] = self._get_methods_info(view)
        return metadata

    def determine_actions(self, request, view):
        actions = {}
        for method in {"PUT", "POST"} & set(view.allowed_methods):
            view.request = clone_request(request, method)
            try:
                if hasattr(view, "check_permissions"):
                    view.check_permissions(view.request)
                if method == "PUT" and hasattr(view, "get_object"):
                    view.get_object()
            except (exceptions.APIException, PermissionDenied, Http404):
                pass
            else:
                serializer = view.get_serializer()
                actions[method] = self.get_serializer_info(serializer)
            finally:
                view.request = request

        return actions

    def get_serializer_info(self, serializer):
        model = serializer.Meta.model
        if hasattr(serializer, "child"):
            serializer = serializer.child
        result = list()
        for field_name, field in serializer.fields.items():
            if not isinstance(field, serializers.HiddenField):
                try:
                    model_field = model._meta.get_field(field.source)
                    if model_field.is_relation:
                        result.append(self.get_ref_field_info(field, model_field))
                    else:
                        result.append(self.get_field_info(field, model_field))
                except FieldDoesNotExist:
                    pass
        return result

    def get_field_info_by_name(self, view, field_name):
        serializer = view.get_serializer()
        model = serializer.Meta.model
        if hasattr(serializer, "child"):
            serializer = serializer.child
        field = serializer.fields.get(field_name, None)
        if field and not isinstance(field, serializers.HiddenField):
            model_field = model._meta.get_field(field.source)
            if model_field.is_relation:
                return self.get_ref_field_info(field, model_field)
            else:
                return self.get_field_info(field, model_field)

    def get_field_info(self, field, model_field):
        return OrderedDict(
            {
                "systemName": model_field.db_column,
                "alias": field.field_name,
                "name": model_field.verbose_name,
                "idField": model_field.primary_key,
                "type": self.label_lookup[model_field],
                "reference": None,
            }
        )

    def get_ref_field_info(self, field, model_field):
        return OrderedDict(
            {
                "systemName": getattr(model_field, "db_column", model_field.name),
                "alias": field.field_name,
                "name": self._get_name(model_field.related_model),
                "idField": False,
                "type": self.label_lookup[model_field.target_field],
                "reference": self._get_reference_info(model_field),
            }
        )

    def _get_name(self, model):
        return model._meta.verbose_name_plural or model._meta.verbose_name

    def _get_db_table_info(self, db_table):
        schema = "resource"
        table_name = db_table
        if '"."' in db_table:
            db_table = db_table.split('"."')
            schema = db_table[0]
            table_name = db_table[1]

        return schema, table_name

    def _get_reference_info(self, model_field):
        field_info = OrderedDict()
        for ref_type in self.ref_type_lookup:
            if getattr(model_field, ref_type, False):
                field_info["refType"] = " ".join(ref_type.split("_")).upper()
                break
        field_info["schema"], field_info["systemName"] = self._get_db_table_info(
            model_field.related_model._meta.db_table
        )
        field_info["name"] = self._get_name(model_field.related_model)
        return field_info

    def _get_methods_info(self, view):
        conf = MethodsConfig(**self.methods_config)
        return [
            conf.methods[name].dict()
            for name in view.__dir__()
            if name in conf.methods.keys()
        ]
