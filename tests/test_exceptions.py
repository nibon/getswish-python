import pytest

from getswish import SwishError


def test_swish_error():
    with pytest.raises(SwishError):
        raise SwishError(errors=[{"errorCode": "foo", "errorMessage": "bar"}])


def test_swish_error_value():
    try:
        raise SwishError(errors=[{"errorCode": "foo", "errorMessage": "bar"}])
    except SwishError as e_info:
        assert str(e_info) == "foo: bar"
        assert e_info.errors == {"foo": "bar"}


def test_swish_error_value_multiple():
    try:
        raise SwishError(
            errors=[
                {"errorCode": "foo", "errorMessage": "bar"},
                {"errorCode": "hey", "errorMessage": "macarena"},
            ]
        )
    except SwishError as e_info:
        assert str(e_info) == "foo: bar, hey: macarena"
        assert e_info.errors == {"foo": "bar", "hey": "macarena"}
