from rest_framework.serializers import ModelSerializer

from .mixins import (
    CustomSerializationMixin,
    CustomDeserializationMixin,
)


class CustomSerializer(
    CustomDeserializationMixin, CustomSerializationMixin, ModelSerializer
):
    pass
