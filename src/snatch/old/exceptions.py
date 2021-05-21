class DataException(Exception):
    """
    Ошибка, связянная с БД
    """
    pass


class UserActionException(Exception):
    """
    Ошибка, связанная с действиями пользователя
    """
    pass


class ZabbixException(Exception):
    """
    Ошибка, связанная с взаимодействием с Zabbix
    """
    pass


class IpaException(Exception):
    """
    Ошибка, связанная с взаимодействием с IPA
    """
    pass


class RepoException(Exception):
    """
    Ошибка, связанная с созданием канала
    """
    pass


class FilterParseException(Exception):
    pass
