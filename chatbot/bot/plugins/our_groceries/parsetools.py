import re
from typing import Tuple, Optional, Union


FRACTION_TRANSLATION = {
    "½": ".5",
    "⅓": ".3333333333333333",
    "⅔": ".6666666666666666",
    "⅕": ".2",
    "⅖": ".4",
    "⅗": ".6",
    "⅘": ".8",
    "¼": ".25",
    "¾": ".75",
    "⅚": ".8333333333333334",
    "⅙": ".16666666666666666",
    "⅐": ".14285714285714285",
    "⅑": ".1111111111111111",
    "⅒": ".1",
    "⅛": ".125",
    "⅜": ".375",
    "⅝": ".625",
    "⅞": ".875",
}

RE_UNICODE_FRACTIONS = "|".join(FRACTION_TRANSLATION)
MATCH_NUMBER_WITH_UNICODE_FRACTIONS = re.compile(rf"(\d*)\s*({RE_UNICODE_FRACTIONS})")

MATCH_EXCESSIVE_WHITESPACE = re.compile(r"\s+")

NON_DISCRETE_UNITS = ("g", "kg", "ml", "l", "TL", "EL",)
RE_NON_DISCRETE_UNITS = "|".join(NON_DISCRETE_UNITS)
MATCH_UNIT_BLACKLIST = re.compile(rf"\b({RE_NON_DISCRETE_UNITS})\b", re.IGNORECASE)


def re_compile_match_split_amount_and_unit(use_us_float_format: bool) -> re.Pattern:
    """Compiles a regex that matches float numbers and the remaining string."""

    if use_us_float_format:
        nsep = ","
        fsep = r"\."
    else:
        nsep = r"\."
        fsep = ","

    return re.compile(rf"""
        \s*
        (
            (?:                    # Left part of comma (can be ommitted)
                \d+
                (?:{nsep}\d\d\d)*  # Number separation for large numbers, e.g 1,000,000
            )?
            (?:                # Right part of comma
                (?:{fsep}\d+)
                |
                (?:\s*{RE_UNICODE_FRACTIONS})
            )?
        )
        \s*
        (.*)  # Remaining part
        \s*
    """, re.VERBOSE)


MATCH_SPLIT_AMOUNT_AND_UNIT_DE = re_compile_match_split_amount_and_unit(False)
MATCH_SPLIT_AMOUNT_AND_UNIT_US = re_compile_match_split_amount_and_unit(True)


def unicode_fraction_to_float(text: str) -> float:
    """Converts a number that might include unicode fractions to a float."""
    def callback(m: re.Match[str]) -> str:
        return m.group(1) + FRACTION_TRANSLATION[m.group(2)]

    return float(re.sub(MATCH_NUMBER_WITH_UNICODE_FRACTIONS, callback, text))


def non_us_to_us_number(text: str) -> str:
    """Translates numbers from non-US formats to US format, i.e. replaces commas with dots and vice-versa."""
    return text.translate({
        ord("."): ",",
        ord(","): ".",
    })


def reduce_excessive_whitespace(text: str) -> str:
    """Reduces multiple consecutive whitespace characters to a single space character."""
    return re.sub(MATCH_EXCESSIVE_WHITESPACE, " ", text)


def split_amount_and_unit(unit_amount_str: str, use_us_float_format: bool) -> Tuple[str, str]:
    """Splits the amount and unit part of a combined string and returns a tuple (amount, unit).

    The given string should be of the format "<number> <unit>".
    If use_us_float_format is true, "." is used as float separator and "," as separator within the number, e.g. 1,000,000.05.
    If false, it's inversed, e.g. 1.000.000,05.

    Signs are not supported. Only positive numbers are expected.
    Fractional unicode characters are supported and will be matched as part of the number.

    Valid number formats are for example:
        - 1
        - 1.5
        - .5
        - 1 ½
        - ½
        - 1,000.5
        - 1,000 ½
    Invalid number formats are for example:
        - 1.
        - 1.5 ½
        - 1  .5
        - 1.  5
        - 1,00,00

    Example:
        "3 small" -> ("3", "small")
        "300g" -> ("300", "g")
        "1.000,5 g" -> ("1.000,5", "g") for non-US format, else ("1.000", ",5 g")
        "1,000.5 g" -> ("1,000.5", "g") for US format, else ("1,000", ".5 g")
        "1,000 ½ g" -> ("1,000 ½", "g") for US format, else ("", "")
        "1.000 ½ g" -> ("1.000 ½", "g")
        "4 ½" -> ("4 ½", "")
        "tomato" -> ("", "tomato")
        "" -> ("", "")
    """
    default = ("", "")

    if not unit_amount_str:
        return default

    if use_us_float_format:
        m = MATCH_SPLIT_AMOUNT_AND_UNIT_US.match(unit_amount_str)
    else:
        m = MATCH_SPLIT_AMOUNT_AND_UNIT_DE.match(unit_amount_str)

    if not m:
        return default

    amount = m.group(1)
    unit = m.group(2)

    return ("" if amount is None else amount.strip(), "" if unit is None else unit.strip())


def try_get_discrete_amount(amount: Union[str, float, int], unit: str) -> Optional[int]:
    """Returns the discrete amount for a given amount and unit combination or None if not applicable."""
    # Ensure dealing with an integer amount
    int_amount: int

    if isinstance(amount, int):
        int_amount = amount

    elif isinstance(amount, float):
        if amount.is_integer():
            int_amount = int(amount)
        else:
            return None

    elif isinstance(amount, str):
        try:
            int_amount = int(amount)
        except ValueError:
            return None

    if unit:
        # Ensure there are no unicode fractions that were treated as part of the unit
        if any((i in unit for i in FRACTION_TRANSLATION)):
            return None

        # Ensure the unit is not a weight or volume unit
        if MATCH_UNIT_BLACKLIST.match(unit):
            return None

    return int_amount


def normalize_str_to_float(number: str, from_us_float_format: bool) -> float:
    """Removes number separators, interprets unicode fractions and returns a corresponding float.

    The number is assumed to be valid according to the given format, otherwise the result will be undefined behavior.
    """
    if not from_us_float_format:
        number = non_us_to_us_number(number)

    number = number.replace(",", "")  # Remove number separators
    return unicode_fraction_to_float(number)


def parse_amount_and_unit(amount_and_unit: str, source_uses_us_float_format: bool) -> Tuple[float, str]:
    """Helper function that combines multiple processing steps for parsing combined amount+unit strings.

    Calls split_amount_and_unit() and normalize_str_to_float() internally.
    """
    amount, unit = split_amount_and_unit(amount_and_unit, source_uses_us_float_format)

    if amount:
        amount_float = normalize_str_to_float(amount, source_uses_us_float_format)
    else:
        amount_float = 0.0

    return amount_float, unit
