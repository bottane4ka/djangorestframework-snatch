import re


def eq_convert(value):
    if value == "null":
        return "isnull", True, False
    return "exact", value, False


def neq_convert(value):
    if value == "null":
        return "isnull", False, False
    return "exact", value, True


def gt_convert(value):
    return "gt", value, False


def gte_convert(value):
    return "gte", value, False


def lt_convert(value):
    return "lt", value, False


def lte_convert(value):
    return "lte", value, False


def like_convert(value):
    lookups = [
        (r"^[^\*]*$", "exact", value),
        (r"^\*.*\*$", "contains", value[1:-1]),
        (r"^\*.*$", "endswith", value[1:]),
        (r"^.*\*$", "startswith", value[:-1]),
    ]
    for pattern, operator, new_value in lookups:
        if re.search(pattern, value):
            return operator, new_value, False
    return "contains", value, False


def is_convert(value):
    ntf = {"true": ["", True], "false": ["", False], "null": ["isnull", True]}
    if value in ntf.keys():
        operator, value = ntf[value]
    return "is", value, False


def year_convert(value):
    return "year", value, False


def month_convert(value):
    return "month", value, False


def day_convert(value):
    return "day", value, False


def ov_convert(value):
    return "overlap", value, False


def between_convert(value):
    return "range", value, False


def in_convert(value):
    return "in", value, False


def and_convert(value):
    return "", value, False


def or_convert(value):
    return "", value, False


def not_convert(value):
    return "", value, True


def desc_convert(value):
    return f"-{value}", None, False


def asc_convert(value):
    return value, None, False
