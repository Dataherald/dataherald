import re


def remove_whitespace(input_string: str) -> str:
    return re.sub(r"\s+", " ", input_string).strip()


def contains_line_breaks(input_string: str) -> bool:
    return "\n" in input_string
