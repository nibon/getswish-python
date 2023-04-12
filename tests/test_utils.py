import pytest

from getswish.utils import (
    camel2snake,
    f_name_conv,
    generate_transaction_id,
    snake2camel,
)


@pytest.mark.parametrize(
    "s, expected",
    [
        ("payeeSSN", "payee_s_s_n"),
        ("fooBar", "foo_bar"),
        ("foo", "foo"),
        ("fooBarFoobar", "foo_bar_foobar"),
        ("f", "f"),
        ("fB", "f_b"),
        ("", ""),
    ],
)
def test_camel2snake(s, expected):
    assert camel2snake(s) == expected


@pytest.mark.parametrize(
    "s, expected",
    [
        ("payeeSSN", "payee_ssn"),
        ("fooBar", "foo_bar"),
        ("foo", "foo"),
        ("fooBarFoobar", "foo_bar_foobar"),
        ("f", "f"),
        ("fB", "f_b"),
        ("", ""),
    ],
)
def test_camel2snake_extra_naming_helpers(s, expected):
    assert f_name_conv(s, camel2snake, True) == expected


@pytest.mark.parametrize(
    "s, expected",
    [
        ("payee_ssn", "payeeSsn"),
        ("foo_bar", "fooBar"),
        ("foo", "foo"),
        ("foo_bar_foobar", "fooBarFoobar"),
        ("f", "f"),
        ("f_b", "fB"),
        ("", ""),
    ],
)
def test_snake2camel(s, expected):
    assert snake2camel(s) == expected


@pytest.mark.parametrize(
    "s, expected",
    [
        ("payee_ssn", "payeeSSN"),  # <-- The difference
        ("foo_bar", "fooBar"),
        ("foo", "foo"),
        ("foo_bar_foobar", "fooBarFoobar"),
        ("f", "f"),
        ("f_b", "fB"),
        ("", ""),
    ],
)
def test_snake2camel_extra_naming_helpers(s, expected):
    assert f_name_conv(s, snake2camel) == expected


def test_transaction_uuid():
    transaction_id = generate_transaction_id()
    assert transaction_id.isupper()
    assert len(transaction_id) == 32
