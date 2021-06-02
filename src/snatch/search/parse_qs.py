import re
import typing as t

from snatch.exceptions import BracketsException
from snatch.tuples import QueryBracket
from snatch.validators import validate_brackets


class QSParser:
    def __call__(self, input_string: t.AnyStr) -> t.List:
        qb = QueryBracket(input_string, -1, -1, [[]], [])
        if not validate_brackets(input_string):
            raise BracketsException(qb.input_string)
        self.search_query(qb)
        return qb.list_stack[0]

    def search_query(self, qb: QueryBracket) -> QueryBracket:
        """Последовательный обход строки относительно скобок

        """
        qb = QueryBracket(
            qb.input_string,
            qb.input_string.find("("),
            qb.input_string.find(")"),
            qb.list_stack,
            qb.drop_key_stack,
        )

        if qb.num_cls == -1 and qb.num_opn == -1:
            func = self.without_brackets
        elif qb.num_opn != -1 and qb.num_opn < qb.num_cls:
            func = self.inside_brackets
        elif (qb.num_cls != -1 and qb.num_opn == -1) or qb.num_opn > qb.num_cls:
            func = self.outside_brackets
        else:
            raise BracketsException(qb.input_string)
        qb = func(qb)
        return qb

    def inside_brackets(self, qb: QueryBracket) -> QueryBracket:
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

        qb = QueryBracket(
            qb.input_string[qb.num_opn + 1:],
            qb.num_opn,
            qb.num_cls,
            qb.list_stack,
            qb.drop_key_stack,
        )
        return self.search_query(qb)

    def outside_brackets(self, qb: QueryBracket) -> QueryBracket:
        """Обработка ситуации: в скобке -> из скобки

        """
        self._handle_sub(qb.input_string[: qb.num_cls], qb.list_stack[-1])
        qb.drop_key_stack.pop() if True in qb.drop_key_stack else qb.list_stack.pop()

        qb = QueryBracket(
            qb.input_string[qb.num_cls + 1:],
            qb.num_opn,
            qb.num_cls,
            qb.list_stack,
            qb.drop_key_stack,
        )
        return self.search_query(qb)

    def without_brackets(self, qb: QueryBracket) -> QueryBracket:
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

    @staticmethod
    def _check_last(sub_string_list: t.List[str]) -> t.Tuple[t.List, str]:
        """Получение оператора перед скобками

        """
        search_string = r"\.in\.$|\.between\.$|or$|and$|not$"
        result = re.search(search_string, sub_string_list[-1])
        return (
            (sub_string_list[:-1], sub_string_list[-1])
            if result
            else (sub_string_list, "")
        )

    def _find_token(self, sub_string: str) -> t.Union[t.Dict, str]:
        """Получение оператора между точками, которые не подразумевают скобки

        """
        search_string = r"\.eq\.|\.gt\.|\.gte\.|\.lt\.|\.lte\.|\.neq\.|\.is\.|\.like\.|\.day\.|\.month\.|\.year\.|\.re\."
        result = re.search(search_string, sub_string)
        if result:
            return self._handle_operator(sub_string, result.group())
        else:
            return sub_string

    @staticmethod
    def _handle_operator(column_name_list: str, op: str) -> t.Dict:
        """Построение параметра для запроса

        """
        column_name_list, search_data = column_name_list.split(op)
        column_name_list = "__".join(column_name_list.split("."))
        return {"{}__{}".format(column_name_list, op[1:-1]): search_data}
