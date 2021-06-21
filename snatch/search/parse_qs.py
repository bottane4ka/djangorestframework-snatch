import re
import typing as t

from django.db.models import Q, Model

from snatch.search.operators.consts import DEFAULT_OPERATORS
from snatch.search.validators import (
    validate_brackets,
    validate_attributes,
    convert_operator,
)
from snatch.search.tuples import BracketParser


class StrongCreator:
    """Создание сложного запроса с помощью объекта Q

    """

    def __call__(
        self, input_sting: str, model: type(Model), is_filter=True
    ) -> t.Union[Q, t.List[str]]:
        parse_data = StrongParser()(input_sting, model, is_filter=is_filter)
        if is_filter:
            return self._to_Q_filter(parse_data, model)
        return self._to_Q_order(parse_data, model)

    def _to_Q_filter(
        self, data: t.List[t.Dict[str, t.Any]], model: type(Model), main_key=None
    ) -> Q:
        query = Q()
        for line in data:
            key_list = list(line.keys())
            for key in key_list:
                if key in ["and", "not"]:
                    query &= self._to_Q_filter(line[key], model, main_key=key)
                elif key in ["or"]:
                    query |= self._to_Q_filter(line[key], model, main_key=key)
                else:
                    item = line.pop(key)
                    attribute_list = key.split("__")[:-1]
                    operator = key.split("__")[-1]
                    validate_attributes(attribute_list, model)
                    operator, item, is_not = convert_operator(operator, item)
                    new_key = "{}{}".format(
                        "__".join(attribute_list), f"__{operator}" if operator else ""
                    )
                    if is_not:
                        query &= ~Q(**{new_key: item})
                    else:
                        line.update({new_key: item})

        if main_key:
            func = getattr(self, f"_{main_key}_convert", None)
            query = func(query, data) if func else query
        if not query:
            query = self._and_convert(query, data)
        return query

    def _to_Q_order(self, data: t.List[str], model: type(Model)) -> t.List[str]:
        order_ = list()
        for line in data:
            attribute_list = line.split("__")[:-1]
            operator = line.split("__")[-1]
            validate_attributes(attribute_list, model)
            operator, item, is_not = convert_operator(
                operator, "__".join(attribute_list)
            )
            order_.append(operator)
        return order_

    def _and_convert(self, query: Q, data: t.List[t.Dict]) -> Q:
        result = dict()
        for line in data:
            if line:
                result.update(line)

        return query & Q(**result) if result else query

    def _or_convert(self, query: Q, data: t.List[t.Dict]) -> Q:
        query |= (Q(**line) for line in data if line)
        return query

    def _not_convert(self, query: Q, data: t.List[t.Dict]) -> Q:
        return ~self._and_convert(query, data)


class StrongParser:
    """Преобразование строки в словарь для фильтрации

    """

    search_with_brackets = "|".join(
        [f"{key}$" for key in DEFAULT_OPERATORS if key.count(".") == 0]
    )

    search_without_brackets = "|".join(
        [key for key in DEFAULT_OPERATORS if key.count(".") == 2]
    )

    search_order = "|".join([key for key in DEFAULT_OPERATORS if key.count(".") == 1])

    def __call__(
        self, input_string: str, model: type(Model), is_filter=True
    ) -> t.List[t.Union[t.Dict, str]]:
        self.model = model
        self.is_filter = is_filter
        qb = BracketParser(input_string, -1, -1, [[]], [])
        validate_brackets(input_string)
        self.search_query(qb)
        return qb.list_stack[0]

    def search_query(self, qb: BracketParser) -> BracketParser:
        qb = BracketParser(
            qb.input_string,
            qb.input_string.find("("),
            qb.input_string.find(")"),
            qb.list_stack,
            qb.drop_key_stack,
        )

        if qb.num_opn != -1 and qb.num_opn < qb.num_cls:
            func = self.inside_brackets
        elif (qb.num_cls != -1 and qb.num_opn == -1) or qb.num_opn > qb.num_cls:
            func = self.outside_brackets
        else:
            func = self.without_brackets

        qb = func(qb)
        return qb

    def inside_brackets(self, qb: BracketParser) -> BracketParser:
        current_list, key_exists = self._handle_sub(
            qb.input_string[: qb.num_opn], qb.list_stack[-1]
        )

        if key_exists:
            qb.list_stack.append([])
            current_list.append({key_exists: qb.list_stack[-1]})
        else:
            qb.drop_key_stack.append(True)

        qb = BracketParser(
            qb.input_string[qb.num_opn + 1 :],
            qb.num_opn,
            qb.num_cls,
            qb.list_stack,
            qb.drop_key_stack,
        )
        return self.search_query(qb)

    def outside_brackets(self, qb: BracketParser) -> BracketParser:
        self._handle_sub(qb.input_string[: qb.num_cls], qb.list_stack[-1])
        qb.drop_key_stack.pop() if True in qb.drop_key_stack else qb.list_stack.pop()

        qb = BracketParser(
            qb.input_string[qb.num_cls + 1 :],
            qb.num_opn,
            qb.num_cls,
            qb.list_stack,
            qb.drop_key_stack,
        )
        return self.search_query(qb)

    def without_brackets(self, qb: BracketParser) -> BracketParser:
        self._handle_sub(qb.input_string, qb.list_stack[-1])
        return qb

    def _handle_sub(
        self, sub_string: str, current_list: t.List
    ) -> t.Tuple[t.List, str]:
        sub_string, possible_key = self._check_last(sub_string.split(","))
        sub_string = [x for x in [self._find_token(y) for y in sub_string] if x]
        possible_key = self._find_token(possible_key) if possible_key else possible_key
        [current_list.append(x) for x in sub_string] if sub_string else None
        return current_list, possible_key

    def _check_last(self, sub_string_list: t.List[str]) -> t.Tuple[t.List, str]:
        result = re.search(self.search_with_brackets, sub_string_list[-1])
        return (
            (sub_string_list[:-1], sub_string_list[-1])
            if result
            else (sub_string_list, "")
        )

    def _find_token(self, sub_string: str) -> t.Union[t.Dict, str]:
        if self.is_filter:
            result = re.search(self.search_without_brackets, sub_string)
        else:
            result = re.search(self.search_order, sub_string)
        if result:
            return self._handle_operator(sub_string, result.group())
        else:
            return sub_string

    def _handle_operator(
        self, attribute_list: str, operator: str
    ) -> t.Union[t.Dict, str]:
        attribute_list, search_data = attribute_list.split(operator)
        attribute_list = attribute_list.split(".")
        if search_data:
            return {
                "{}__{}".format(
                    "__".join(attribute_list), operator.replace(".", "")
                ): search_data
            }
        else:
            return "{}__{}".format("__".join(attribute_list), operator.replace(".", ""))


class StrongRelations:
    def __init__(self, max_level: int, level: str, serializer):
        self.relations = self._get_relations(max_level, level, serializer)

    def __call__(self):
        return self._convert(self.relations)

    def _get_relations(self, max_level: int, level: str, serializer) -> t.Dict:
        relations = dict()
        if not level and max_level > 0:
            relations = self._create_by_max_level(
                max_level, serializer.Meta.model, serializer
            )
        return relations

    def _create_by_max_level(
        self, max_level: int, model: type(Model), serializer
    ) -> t.Dict:
        relations = dict()
        if not hasattr(serializer, "fields"):
            serializer = (
                serializer.proxied
                if hasattr(serializer, "proxied")
                else serializer.root
            )
        model_field_list = [
            (field, serializer.fields[field.name])
            for field in model._meta.get_fields()
            if field.name in serializer.fields.keys() and field.is_relation
        ]
        if model_field_list:
            for field, serializer in model_field_list:
                prefetch_related = (
                    True if field.many_to_many or field.one_to_many else False
                )
                new_max_level = max_level if prefetch_related else max_level - 1
                children = None
                if max_level - 1 > 0:
                    children = self._create_by_max_level(
                        max_level - 1, field.related_model, serializer
                    )
                relations[field.name] = {
                    "prefetch_related": prefetch_related,
                    "max_level": new_max_level,
                    "children": children,
                }
        return relations if relations else None

    def _convert(
        self, relations: t.Dict, enter=True
    ) -> t.Tuple[t.List[str], t.List[str]]:
        select_related = list()
        prefetch_related = list()
        for key, item in relations.items():
            new_enter = True if not item["prefetch_related"] else False
            if item["max_level"] >= 0 and item["children"] and enter:
                child_select_related, child_prefetch_related = self._convert(
                    item["children"], enter=new_enter
                )
                if child_select_related and not item["prefetch_related"]:
                    select_related.extend(
                        [f"{key}__{name}" for name in child_select_related]
                    )
                elif child_select_related and item["prefetch_related"]:
                    prefetch_related.extend(
                        [f"{key}__{name}" for name in child_select_related]
                    )
                elif child_prefetch_related:
                    prefetch_related.extend(
                        [f"{key}__{name}" for name in child_prefetch_related]
                    )
            else:
                if not item["prefetch_related"]:
                    select_related.extend([key])
                else:
                    prefetch_related.extend([key])

        return select_related, prefetch_related
