from __future__ import annotations

import uuid


def snake2camel(snake_str: str) -> str:
    first, *others = snake_str.split("_")
    return "".join([first.lower(), *map(str.title, others)])


def camel2snake(camel_str: str) -> str:
    return "".join(["_" + c.lower() if c.isupper() else c for c in camel_str]).lstrip("_")


def generate_transaction_id():
    """Format required by length and capitalization by swish API."""
    return str(uuid.uuid4().hex).upper()


# Some field names from service doesn't map to conventional names between snake and camelCase.
# Small helpers just to do the conversation automagically.
_name_map = {
    "payout_instruction_uuid": "payoutInstructionUUID",
    "payee_ssn": "payeeSSN",
    "payer_ssn": "payerSSN",
}
_name_map_rev = {v: k for k, v in _name_map.items()}


def f_name_conv(field_name: str, conversion_function: callable, rev: bool = False) -> str:
    """Converts the field_name using the table firstly if found, else the given conversion function given."""
    return (_name_map_rev if rev else _name_map).get(field_name, conversion_function(field_name))
