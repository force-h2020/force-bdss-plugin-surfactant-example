import re

from force_bdss.api import Identifier


#: Regex rules for force_bdss class Identifier
_regex = Identifier().parent.regex


def process_variable_name(variable_name):
    """Process variable name to make sure it will be accepted by
    force-bdss objects as an Identifier trait"""

    #: Regex rules of Identifier trait
    allowed = re.compile(_regex)

    # Remove any decimals or whitespace at beginning of string
    variable_name = re.sub(r"^\d", '', variable_name)
    variable_name = re.sub(r"^\s", '', variable_name)
    # Substitute any whitespace or hyphens with underscore
    variable_name = re.sub(r"\s|-", '_', variable_name)
    # Remove any non-word characters
    variable_name = re.sub(r"\W", '', variable_name)
    # Remove any double underscores
    variable_name = re.sub(r"__", '_', variable_name)

    # Check that variable name is allowed by BDSS
    assert re.match(allowed, variable_name) is not None, (
        f"Invalid variable name: {variable_name}"
    )

    return variable_name
