from collections import namedtuple

BracketParser = namedtuple(
    "BracketParser",
    ["input_string", "num_opn", "num_cls", "list_stack", "drop_key_stack"],
)


OperatorInfo = namedtuple("OperatorInfo", ["name", "is_bracket", "is_point"])
