from functools import wraps

from snatch.utils import get_link_many, get_link_one


def add_link_many(func):
    """Декоратор для оборачивания списка значений (кроме списка первого уровня) в self и link.
    При указании max_level (по-умолчанию max_level = 1) происходит ограничение по уровню вложенности,
    то есть self пустой, а link не пустой, если результат на самом деле не пустой.

    Примеры:
    ----------------------
    "action_list": {
        "self": [
            {
                "id": "1",
                "name": "Example"
            },
            ...
        ],
        "link": "/api/table_schema/table_name/list?query=parent.eq.23"
    }
    ----------------------
    "action_list": {
        "self": None,
        "link": "/api/table_schema/table_name/list?query=parent.eq.23"
    }

    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        self = args[0]
        data = args[1]
        if not self.parent:
            return func(self, data)

        source = self.source if self.source else self.context.get("source")
        level = self.context.pop("level")
        source_level = level.get(source, None) if level else None
        if not source_level or source_level["max_level"] < 2:
            result = {
                "link": get_link_many(data.field, data.instance)
                if data.count() > 0
                else None,
                "self": None,
            }
        else:
            self.context["level"] = source_level.get("children")

            result = func(self, data)
            result = {
                "link": get_link_many(data.field, data.instance) if result else None,
                "self": result if result else None,
            }

        self.context["level"] = level
        return result

    return wrapper


def add_link_one(func):
    """Декоратор для оборачивания одного значения в self и link.
    При указании max_level (по-умолчанию max_level = 1) происходит ограничение по уровню вложенности,
    то есть self пустой, а link не пустой, если результат на самом деле не пустой.

    Примеры:
    ----------------------
    "action_id": {
        "self": {
            "id": "1",
            "name": "Example"
        },
        "link": "/api/table_schema/table_name?query=id.eq.1"
    }
    ----------------------
    "action_id": {
        "self": None,
        "link": "/api/table_schema/table_name?query=id.eq.1"
    }

    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        self = args[0]
        value = args[1]
        # TODO Тут сломала
        if "max_level" in self.context.keys():
            max_level = self.context.pop("max_level")
            result = func(self, value)
            self.context["max_level"] = max_level
            return result if result else None

        source = self.source if self.source else self.context.get("source")
        level = self.context.pop("level")
        source_level = level.get(source, level) if level else None

        if not source_level or source_level.get("max_level", 1) == 0:
            result = {
                "link": get_link_one(self, value) if value else None,
                "self": None,
            }
        else:
            self.context["level"] = (
                source_level.get("children") if self.source else source_level
            )
            result = func(self, value)
            result = {
                "link": get_link_one(self, value) if value else None,
                "self": result if result else None,
            }

        self.context["level"] = level
        return result

    return wrapper
