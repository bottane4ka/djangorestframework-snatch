import re
import typing as t
from django.db.models import Q, Model
from snatch.search.validators import (
    validate_brackets,
    validate_attributes,
    validate_operators,
)
from snatch.tuples import BracketParser
from snatch.search.validators import OPERATORS


class StrongCreator:
    """Создание сложного запроса с помощью объекта Q

    """

    def __call__(self, parse_data: t.List[t.Dict], model: Model) -> Q:
        return self._to_Q(parse_data, model)

    def _to_Q(
        self, data: t.Union[t.List[t.Dict[str, t.Any]]], model: Model, main_key="and"
    ) -> Q:
        query = Q()
        for line in data:
            key_list = line.keys()
            for key in key_list:
                if key in ["and", "not"]:
                    query &= self._to_Q(line[key], model, main_key=key)
                elif key in ["or"]:
                    query |= self._to_Q(line[key], model, main_key=key)
                else:
                    item = line.pop(key)
                    attribute_list = key.split("__")[:-1]
                    operator = key.split("__")[-1]
                    validate_attributes(attribute_list, model)
                    operator, item, is_not = validate_operators(operator, item)
                    new_key = "{}{}".format(
                        "__".join(attribute_list), f"__{operator}" if operator else ""
                    )
                    line[new_key] = item if not is_not else ~Q(**item)

        if main_key:
            func = getattr(self, f"_{main_key}_convert", None)
            query = func(query, data) if func else query
        return query

    def _and_convert(self, query: Q, data: t.List[t.Dict]) -> Q:
        result = dict()
        for line in data:
            result.update(line)
        return query & Q(**result)

    def _or_convert(self, query: Q, data: t.List[t.Dict]) -> Q:
        query |= (Q(**line) for line in data)
        return query

    def _not_convert(self, query: Q, data: t.List[t.Dict]) -> Q:
        return ~self._and_convert(query, data)


class StrongParser:
    """Преобразование строки в словарь для фильтрации

    """

    search_with_brackets = "|".join(
        [
            f"\.{key}\.$" if value.is_point else f"{key}$"
            for key, value in OPERATORS.items()
            if value.is_bracket
        ]
    )

    search_without_brackets = "|".join(
        [f"\.{key}\." for key, value in OPERATORS.items() if value.is_point]
    )

    def __call__(self, input_string: str) -> t.List[t.Dict]:
        qb = BracketParser(input_string, -1, -1, [[]], [])
        validate_brackets(input_string)
        self.search_query(qb)
        return qb.list_stack[0]

    def search_query(self, qb: BracketParser) -> BracketParser:
        """Последовательный обход строки относительно скобок

        """
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
        """Обработка ситуации: перед скобкой -> в скобку

        """
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
        """Обработка ситуации: в скобке -> из скобки

        """
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
        """Обработка ситуации: без скобок

        """
        self._handle_sub(qb.input_string, qb.list_stack[-1])
        return qb

    def _handle_sub(
        self, sub_string: str, current_list: t.List
    ) -> t.Tuple[t.List, str]:
        """Обработка подстроки между скобками

        """
        sub_string, possible_key = self._check_last(sub_string.split(","))
        sub_string = [x for x in [self._find_token(y) for y in sub_string] if x]
        possible_key = self._find_token(possible_key) if possible_key else possible_key
        [current_list.append(x) for x in sub_string] if sub_string else None
        return current_list, possible_key

    def _check_last(self, sub_string_list: t.List[str]) -> t.Tuple[t.List, str]:
        """Получение оператора перед скобками

        """
        result = re.search(self.search_with_brackets, sub_string_list[-1])
        return (
            (sub_string_list[:-1], sub_string_list[-1])
            if result
            else (sub_string_list, "")
        )

    def _find_token(self, sub_string: str) -> t.Union[t.Dict, str]:
        """Получение оператора между точками, которые не подразумевают скобки

        """
        result = re.search(self.search_without_brackets, sub_string)
        if result:
            return self._handle_operator(sub_string, result.group())
        else:
            return sub_string

    def _handle_operator(self, column_name_list: str, op: str) -> t.Union[t.Dict, str]:
        """Построение параметра для запроса

        """
        column_name_list, search_data = column_name_list.split(op)
        column_name_list = "__".join(column_name_list.split("."))
        if search_data:
            return {"{}__{}".format(column_name_list, op[1:-1]): search_data}
        else:
            return "{}__{}".format(column_name_list, op[1:-1])


if __name__ == "__main__":
    a = StrongParser()
    string = "and(p.eq.123,or(p.in.(1,2,3),abw.between.(578,587),a.p.eq.9))"
    result = a(string)
