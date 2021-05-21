from re import search


class QSParser(object):

    __slots__ = ['result']

    def __init__(self, input_str):
        self.result = []  # list (с уровнями вложенности), в котором накапливаются результаты
        self._inparenth(input_str, [self.result], []) if self._validate(input_str) else None

    def __getitem__(self, item):
        return self.result[item]

    @staticmethod
    def _validate(input_str):
        """
        валидация: тип str, не пустая, количества открытых и закрытых скобок равны
        :param input_str: входная строка
        :return: True или False
        """
        if not input_str or not isinstance(input_str, str):
            return False
        parenths = []
        for x in input_str:
            parenths.append(x) if x == '(' else None
            if x == ')':
                if len(parenths) == 0:
                    return False
                parenths.pop()
        return True if len(parenths) == 0 else False

    def _inparenth(self, input_str, list_stack, drop_key_stack):
        """
        последовательный обход строки относительно открываемых/закрываемых скобок
        :param input_str: текущий остаток строки
        :param list_stack: стек в который складывются list текущего уровня относительно скобок
        :param drop_key_stack: list булевых значений входов в скобки без ключа (при выходе из скобок - pop())
        :return: None
        """
        opn, cls = input_str.find('('), input_str.find(')')  # определяем индексы ближайших скобок
        if opn < cls and opn != -1:  # ситуация: перед скобкой -> в скобку s[:opn]
            current_list, got_key = self._handle_sub(input_str[:opn], list_stack[-1])
            if got_key:  # если есть, то он отделяется от остальной строки
                list_stack.append([])  # добавляем новый list в стек
                current_list.append({got_key: list_stack[-1]})  # добавляем внутрь текущего list пару {ключ: новый list}
            else:  # входим в скобки без предшествующего ключа
                drop_key_stack.append(True)
            return self._inparenth(input_str[opn + 1:], list_stack, drop_key_stack)
        elif opn > cls or (cls != -1 and opn == -1):  # ситуация: в скобке -> из скобки s[:cls]
            self._handle_sub(input_str[:cls], list_stack[-1])
            drop_key_stack.pop() if True in drop_key_stack else list_stack.pop()
            return self._inparenth(input_str[cls + 1:], list_stack, drop_key_stack)
        else:  # ситуация: после всех скобок в конце строки
            self._handle_sub(input_str, list_stack[-1])  # обрабатываем последнюю подстроку
            return

    def _handle_sub(self, substr, current_list):
        """
        обработка подстроки между скобками (как открывающимися, так и закрывающимися)
        :param substr: подстрока
        :param current_list: list текущего уровня относительно скобок из list_stack
        :return: (обновлённый current_list и ключ str, если есть (либо пустая строка))
        """
        substr, possible_key = self._check_last(substr.split(','))
        substr = [x for x in [self._find_token(y) for y in substr] if x]
        possible_key = self._find_token(possible_key) if possible_key else possible_key
        [current_list.append(x) for x in substr] if substr else None  # добавляем остаток строки в массив
        return current_list, possible_key

    @staticmethod
    def _check_last(separated_substr):
        """
        получение элемента перед скобками - если он является оператором из словаря операторов номер 2
        :param separated_substr: строка, разбитая по запятым
        :return: строка без последнего элемента, если он оператор, либо целиком, если оператора нет
        """
        last_el = separated_substr[-1]
        res = search('\.eq\.$|\.gt\.$|\.gte\.$|\.lt\.$|\.lte\.$|\.neq\.$|\.in\.$|\.is\.$|\.like\.$|or$|and$|not$',
                     last_el)
        return (separated_substr[:-1], last_el) if res is not None else (separated_substr, '')

    def _find_token(self, sub_el):
        """
        поиск оператора из словаря операторов номер 1 в элементе подстроки (разделённой по запятым)
        :param sub_el: часть подстроки
        :return: если есть оператор, то dict из функции handle_operator(), иначе - строка в неизменном виде
        """
        res = search('\.eq\.|\.gt\.|\.gte\.|\.lt\.|\.lte\.|\.neq\.|\.in\.|\.is\.|\.not\.|\.like\.',
                     sub_el)  # словарь номер 1
        return self._handle_operator(sub_el, res.group()) if res is not None else sub_el

    @staticmethod
    def _handle_operator(sub_el, op):
        """
        обработка строки с оператором из словаря 1 и словаря 2
        :param sub_el: часть подстроки
        :param op: обнаруженный оператор
        :return: dict или строка, обработанная относительно оператора
        """
        sub_el = sub_el.split(op)
        sub_el[0] = '__'.join(sub_el[0].split('.'))
        return {'{}__{}'.format(sub_el[0], op[1:-1]): sub_el[1]} if sub_el[1] else '{}__{}'.format(sub_el[0], op[1:-1])
