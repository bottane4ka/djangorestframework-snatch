from collections import namedtuple

QueryBracket = namedtuple(
    "QueryBracket",
    ["input_string", "num_opn", "num_cls", "list_stack", "drop_key_stack"],
)
