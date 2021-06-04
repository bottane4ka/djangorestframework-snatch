from rest_framework.serializers import ListField

from snatch.mixins import CustomListFieldMixin


class CustomListField(CustomListFieldMixin, ListField):
    pass
