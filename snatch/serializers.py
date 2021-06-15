from rest_framework.serializers import ModelSerializer, ListSerializer

from snatch.mixins import (
    SnatchSerializationMixin,
    SnatchDeserializationMixin,
    SnatchListSerializerMixin,
)


class SnatchSerializer(
    SnatchDeserializationMixin, SnatchSerializationMixin, ModelSerializer
):
    """Snatch сериализатор

    """
    @classmethod
    def many_init(cls, *args, **kwargs):
        kwargs["child"] = cls()
        return SnatchListSerializer(*args, **kwargs)


class SnatchListSerializer(SnatchListSerializerMixin, ListSerializer):
    """Snatch сериализатор для списка

    """
    pass
