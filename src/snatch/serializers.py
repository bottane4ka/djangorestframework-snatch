from rest_framework.serializers import ModelSerializer

from snatch.mixins import CustomSerializationMixin, CustomDeserializationMixin


class CustomSerializer(
    CustomDeserializationMixin, CustomSerializationMixin, ModelSerializer
):
    pass

