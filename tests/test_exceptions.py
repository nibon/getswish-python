import pytest
import requests

from getswish import SwishError


@pytest.mark.parametrize("base", [requests.HTTPError, requests.RequestException])
def test_swish_error_requests_compatibility(base):
    error = SwishError("failed")
    with pytest.raises(base) as caught:
        raise error
    assert caught.value is error


def test_swish_error_response_and_request():
    response = requests.Response()
    response.status_code = 422
    response.request = requests.Request("POST", "https://example.com").prepare()
    error = SwishError("failed", response=response)
    assert error.response is response
    assert error.response.status_code == 422
    assert error.request is response.request


@pytest.mark.parametrize(
    "payload, expected",
    [
        ({"errorCode": ["upstream"], "errorMessage": "failed"}, {"['upstream']": "failed"}),
        ({"errorCode": {"code": 1}, "errorMessage": ["failed"]}, {"{'code': 1}": "['failed']"}),
        ({"code": [1], "message": {"detail": "failed"}}, {"[1]": "{'detail': 'failed'}"}),
        ({"errorCode": None, "errorMessage": None}, {"None": "None"}),
        ([None, "failed", 42], {"error": "[None, 'failed', 42]"}),
        (42, {"error": "42"}),
        (True, {"error": "True"}),
    ],
)
def test_swish_error_unexpected_payload(payload, expected):
    error = SwishError(payload)
    assert error.errors == expected
    assert error.raw_errors is payload
    assert str(error)


@pytest.mark.parametrize("payload", [[], {}, None, False, 0, ""])
def test_swish_error_empty_payload_without_response(payload):
    error = SwishError(payload)
    assert error.errors == {"error": str(payload)}
    assert error.raw_errors is payload
    assert error.response is None


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
