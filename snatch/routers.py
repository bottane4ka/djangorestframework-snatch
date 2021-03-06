from collections import namedtuple

from rest_framework.routers import SimpleRouter
from rest_framework.settings import api_settings

Route = namedtuple("Route", ["url", "mapping", "name", "detail", "initkwargs"])


class SnatchRouter(SimpleRouter):
    """Snatch роутер для получения эндпойнтов в следующей нотации:
        - table_schema/table_name/list
            - GET - получение списка объектов
        - table_schema/table_name/size
            - GET - получение количества объектов в списке
        - table_schema/table_name/
            - GET - получение объекта
            - POST - создание объекта
            - PUT - изменение объекта
            - DELETE - удаление объекта
        - table_schema/table_name/info/
            - GET - получение информации о таблице
        - table_schema/table_name/info/table_attribute
            - GET - редирект на список элементов из родительской таблицы (если поля является ссылкой)

    """
    routes = [
        Route(
            url=r"^{prefix}/list$",
            mapping={"get": "list"},
            name="{basename}_list",
            detail=False,
            initkwargs={"suffix": "List"},
        ),
        Route(
            url=r"^{prefix}/size$",
            mapping={"get": "size"},
            name="{basename}_size",
            detail=False,
            initkwargs={"suffix": "Size"},
        ),
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
        Route(
            url=r"^{prefix}/info/$",
            mapping={"get": "info"},
            name="{basename}_info",
            detail=True,
            initkwargs={"suffix": "Info"},
        ),
        Route(
            url=r"^{prefix}/info/{lookup}$",
            mapping={"get": "info_redirect"},
            name="{basename}_redirect",
            detail=True,
            initkwargs={},
        ),
    ]

    def __init__(self, *args, **kwargs):
        if "root_renderers" in kwargs:
            self.root_renderers = kwargs.pop("root_renderers")
        else:
            self.root_renderers = list(api_settings.DEFAULT_RENDERER_CLASSES)
        super().__init__(*args, **kwargs)

    def register_all(self, views):
        """Инициация всех эндпойнтов по списку представлений

        Args:
            views: список представлений

        Returns:

        """
        for view_name in views.__dict__:
            if "__" in view_name:
                continue
            view = getattr(views, view_name)
            if type(view) == type:
                schema_name, table_name = view.queryset.model._meta.db_table.split(
                    '"."'
                )
                self.register(
                    f"{schema_name}/{table_name}",
                    view,
                    basename=f"{schema_name}_{table_name}",
                )
