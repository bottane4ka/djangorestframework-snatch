import copy

from rest_framework.fields import Field

from snatch.wrappers import add_link_many


class SnatchSerializerMethodField(Field):
    """Метод сериализатора, который оборачивает данные в self и link.

    """

    def __init__(self, method_name=None, source=None, **kwargs):
        self.method_name = method_name
        kwargs["source"] = "*"
        kwargs["read_only"] = True
        super().__init__(**kwargs)
        self.source = source

    def bind(self, field_name, parent):
        if self.method_name is None:
            self.method_name = "get_{field_name}".format(field_name=field_name)

        self.field_name = field_name
        self.parent = parent

        if self.label is None:
            self.label = field_name.replace("_", " ").capitalize()

        if self.source is None:
            self.source = field_name

        self.source_attrs = [] if self.source == "*" else self.source.split(".")

    # @add_link_many
    def to_representation(self, value):
        method = getattr(self.parent, self.method_name)
        self.context["source"] = self.source
        return method(value)
