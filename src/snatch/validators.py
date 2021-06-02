def validate_brackets(input_str: str) -> bool:
    """Валидация правильной последовательности скобок

    Args:
        input_str: входящая строка

    Returns:
        is_valid: признак валидности строки
    """
    if not (input_str and isinstance(input_str, str)):
        return False

    if not ("(" in input_str or ")" in input_str):
        return True

    open_brackets, close_brackets = 0, 0
    for char in input_str:
        if char == "(":
            open_brackets += 1
        elif char == ")":
            close_brackets += 1
        if open_brackets < close_brackets:
            return False
    return True
