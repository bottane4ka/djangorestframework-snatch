import pytest
from snatch.search.validators import validate_brackets


class TestQSParser:
    @pytest.fixture
    def valid_strings(self):
        return ["()", "()()()" "(())()(()())"]

    @pytest.fixture
    def not_valid_strings(self):
        return ["", ")(", "())", ")(())"]

    def test_validate__check_valid_string__success(self, valid_strings):
        result = [validate_brackets(valid_string) for valid_string in valid_strings]

        assert all(result) is True

    def test_validate__check_not_valid_string__success(self, not_valid_strings):
        result = [
            validate_brackets(valid_string) for valid_string in not_valid_strings
        ]

        assert all(result) is False
