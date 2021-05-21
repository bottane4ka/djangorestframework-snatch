from collections import namedtuple

from rest_framework.routers import SimpleRouter
from rest_framework.settings import api_settings

Route = namedtuple("Route", ["url", "mapping", "name", "detail", "initkwargs"])


class CustomRouter(SimpleRouter):

    routes = [
        # List route.
        Route(
            url=r"^{prefix}/list$",
            mapping={"get": "list"},
            name="{basename}_list",
            detail=False,
            initkwargs={"suffix": "List"},
        ),
        # Detail route.
        Route(
            url=r"^{prefix}/$",
            mapping={
                "get": "retrieve",
                "post": "create",
                "put": "update",
                "delete": "destroy",
            },
            name="{basename}_detail",
            detail=True,
            initkwargs={"suffix": "Instance"},
        ),
    ]

    def __init__(self, *args, **kwargs):
        if "root_renderers" in kwargs:
            self.root_renderers = kwargs.pop("root_renderers")
        else:
            self.root_renderers = list(api_settings.DEFAULT_RENDERER_CLASSES)
        super().__init__(*args, **kwargs)

    def register_all(self, views):
        for view_name in views.__dict__:
            if "__" in view_name:
                continue
            view = getattr(views, view_name)
            if type(view) == type:
                schema_name, table_name = view.queryset.model._meta.db_table.split("\".\"")
                self.register(
                    f"{schema_name}/{table_name}",
                    view,
                    basename=f"{schema_name}_{table_name}",
                )
