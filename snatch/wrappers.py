from functools import wraps

from snatch.exceptions import ModelFilterException
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
        old_max_level = self.context.get("max_level")

        result = func(self, data)

        if not self.parent:
            return result

        link = get_link_many(data.field, data.instance)

        if result and old_max_level > 0:
            return {"link": link, "self": result if result else None}
        elif result and old_max_level == 0:
            return {"link": link, "self": None}
        else:
            return {"link": None, "self": None}

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
        old_max_level = self.context.get("max_level", 1)
        if old_max_level == 0:
            if not self.source and not self.context.get("is_child", False):
                raise ModelFilterException(
                    value._meta.model._meta.object_name,
                    "параметр 'max_level' не может быть равен 0",
                )
            else:
                return {
                    "link": get_link_one(self, value) if value else None,
                    "self": None,
                }
        self.context["max_level"] -= 1
        result = func(self, value)
        self.context["max_level"] = old_max_level
        if not self.source and not self.context.get("is_child", False):
            return result
        return {
            "link": get_link_one(self, value) if value else None,
            "self": result if result else None,
        }

    return wrapper
