from dataclasses import dataclass
import pytest
import requests
from requests import HTTPError

import getswish


from .fixtures import *  # noqa F403


@dataclass
class RequestsMockResponse:
    status_code: int = 200
    json_data: list[dict] | dict = ""
    headers: dict = dict
    text: str = ""
    content: bytes = b""

    def json(self):
        return self.json_data

    def raise_for_status(self):
        if self.status_code >= 400:
            raise HTTPError()


def test_client_init_default(client_default):
    assert client_default is not None


def test_client_init(client):
    assert client is not None


def test_url(client):
    version, path = "v1", "path"
    assert client._url(version, path) == f"{client.environment.base}{version}{path}"


def test_recurring_url(client):
    version, path = "v1", "/consents"
    assert client._recurring_url(version, path) == f"{client.environment.recurring_base}{version}{path}"


def test_qr_url(client):
    version, path = "v1", "/prefilled"
    assert client._qr_url(version, path) == f"{client.environment.qr_base}{version}{path}"


def test_sign_payload(client):
    a = client._sign_payload({"foo": "bar"})
    assert isinstance(a, str)
    assert len(a) == 684


def test_sign_payload_missing(client):
    client.certificates.signing = None
    with pytest.raises(AssertionError):
        client._sign_payload({"foo": "bar"})


def test_requests_http_error(client, callback_url, mocker):
    mocker.patch.object(requests, "put", return_value=RequestsMockResponse(400))
    with pytest.raises(HTTPError):
        client.create_payment(20.0, callback_url)


def test_requests_swish_error(client, callback_url, t_service_error, mocker):
    mocker.patch.object(requests, "put", return_value=RequestsMockResponse(422, t_service_error))
    with pytest.raises(getswish.SwishError):
        client.create_payment(20.0, callback_url)


def test_requests_swish_error_object(client, callback_url, mocker):
    error = {"errorCode": "foo", "errorMessage": "bar", "traceId": "trace-id"}
    mocker.patch.object(requests, "put", return_value=RequestsMockResponse(422, error))
    with pytest.raises(getswish.SwishError) as e_info:
        client.create_payment(20.0, callback_url)
    assert e_info.value.errors == {"foo": "bar"}
    assert e_info.value.trace_id == "trace-id"


def test_requests_swish_error_text(client, callback_url, mocker):
    response = RequestsMockResponse(422, text="bad gateway")
    response.json = lambda: (_ for _ in ()).throw(ValueError())
    mocker.patch.object(requests, "put", return_value=response)
    with pytest.raises(getswish.SwishError) as e_info:
        client.create_payment(20.0, callback_url)
    assert e_info.value.errors == {"error": "bad gateway"}


def test_requests_create_payment(client, callback_url, t_payment_response, t_payment_created_headers, mocker):
    patched_response = RequestsMockResponse(201, t_payment_response, t_payment_created_headers)
    mocker.patch.object(requests, "put", return_value=patched_response)
    response = client.create_payment(20.0, callback_url)
    assert response.location == "https://payment/path/"
    assert response.payment_request_token == "payment_token"


def test_requests_retrieve_payment(client, callback_url, t_payment_response, mocker):
    mocker.patch.object(requests, "get", return_value=RequestsMockResponse(200, t_payment_response))
    response = client.retrieve_payment(t_payment_response["id"])
    assert response.id == t_payment_response["id"]


def test_requests_cancel_payment(client, callback_url, t_payment_response, mocker):
    mocker.patch.object(requests, "patch", return_value=RequestsMockResponse(200, t_payment_response))
    response = client.cancel_payment(t_payment_response["id"])
    assert response.id == t_payment_response["id"]


def test_requests_create_refund(client, mocker, callback_url, t_refund, t_refund_response, t_refund_created_headers):
    patched_response = RequestsMockResponse(201, t_refund_response, t_refund_created_headers)
    mocker.patch.object(requests, "put", return_value=patched_response)
    response = client.create_refund(
        t_refund.original_payment_reference, callback_url, t_refund.payee_alias, t_refund.amount
    )
    assert response.location == "https://refund/path/"


def test_requests_retrieve_refund(client, callback_url, t_refund_response, mocker):
    mocker.patch.object(requests, "get", return_value=RequestsMockResponse(200, t_refund_response))
    response = client.retrieve_refund(t_refund_response["id"])
    assert response.id == t_refund_response["id"]


def test_requests_create_payout(client, mocker, callback_url, t_payout, t_payout_response, t_payout_created_headers):
    patched_response = RequestsMockResponse(201, t_payout_response, t_payout_created_headers)
    mocker.patch.object(requests, "post", return_value=patched_response)
    response = client.create_payout(
        t_payout.payer_payment_reference,
        t_payout.payee_alias,
        t_payout.payee_ssn,
        t_payout.amount,
        callback_url,
    )
    assert response.location == "https://payout/path/"


def test_requests_retrieve_payout(client, callback_url, t_payout_response, mocker):
    mocker.patch.object(requests, "get", return_value=RequestsMockResponse(200, t_payout_response))
    response = client.retrieve_payout(t_payout_response["payoutInstructionUUID"])
    assert response.payout_instruction_uuid == t_payout_response["payoutInstructionUUID"]


def test_requests_create_recurring_ecommerce_consent(
    client, callback_url, t_recurring_consent_response, mocker
):
    patched_post = mocker.patch.object(
        requests,
        "post",
        return_value=RequestsMockResponse(201, t_recurring_consent_response, {"Location": "https://consent/path/"}),
    )
    response = client.create_recurring_ecommerce_consent(
        callback_url,
        "46701234567",
        on_behalf_of="partner",
        payee_payment_reference="order-123",
    )
    assert response.location == "https://consent/path/"
    assert patched_post.call_args.kwargs["url"] == client._recurring_url("v1", "/consents")
    assert patched_post.call_args.kwargs["json"]["payerAlias"] == "46701234567"
    assert patched_post.call_args.kwargs["headers"] == {"onBehalfOf": "partner"}


def test_requests_create_recurring_mcommerce_consent(client, callback_url, t_recurring_consent_response, mocker):
    patched_post = mocker.patch.object(
        requests,
        "post",
        return_value=RequestsMockResponse(
            201,
            t_recurring_consent_response,
            {"Location": "https://consent/path/", "PaymentRequestToken": "recurring-token"},
        ),
    )
    response = client.create_recurring_mcommerce_consent(callback_url)
    assert response.location == "https://consent/path/"
    assert response.payment_request_token == "recurring-token"
    assert patched_post.call_args.kwargs["url"] == client._recurring_url("v1", "/consents/token")


def test_requests_update_recurring_consent_callback(client, callback_url, t_recurring_consent_response, mocker):
    patched_patch = mocker.patch.object(requests, "patch", return_value=RequestsMockResponse(200, t_recurring_consent_response))
    response = client.update_recurring_consent_callback_url("consent-id", callback_url, on_behalf_of="partner")
    assert response.id == "consent-id"
    assert patched_patch.call_args.kwargs["url"] == client._recurring_url("v1", "/consents/consent-id")
    assert patched_patch.call_args.kwargs["json"] == [
        {"op": "replace", "path": "/callbackUrl", "value": callback_url}
    ]
    assert patched_patch.call_args.kwargs["headers"] == {
        "Content-Type": "application/json-patch+json",
        "onBehalfOf": "partner",
    }


def test_requests_retrieve_recurring_consent(client, t_recurring_consent_response, mocker):
    patched_get = mocker.patch.object(requests, "get", return_value=RequestsMockResponse(200, t_recurring_consent_response))
    response = client.retrieve_recurring_consent("consent-id")
    assert response.id == "consent-id"
    assert patched_get.call_args.kwargs["url"] == client._recurring_url("v1", "/consents/consent-id")


def test_requests_delete_recurring_consent(client, mocker):
    patched_delete = mocker.patch.object(requests, "delete", return_value=RequestsMockResponse(204))
    response = client.delete_recurring_consent("consent-id", on_behalf_of="partner")
    assert response.status_code == 204
    assert patched_delete.call_args.kwargs["url"] == client._recurring_url("v1", "/consents/consent-id")
    assert patched_delete.call_args.kwargs["headers"] == {"onBehalfOf": "partner"}


def test_requests_create_recurring_payment(client, callback_url, t_recurring_payment_response, mocker):
    patched_post = mocker.patch.object(
        requests,
        "post",
        return_value=RequestsMockResponse(201, t_recurring_payment_response, {"Location": "https://payment/path/"}),
    )
    response = client.create_recurring_payment("consent-id", 20.0, callback_url, message="Recurring payment")
    assert response.location == "https://payment/path/"
    assert patched_post.call_args.kwargs["url"] == client._recurring_url("v1", "/payments")
    assert patched_post.call_args.kwargs["json"]["consentId"] == "consent-id"


def test_requests_retrieve_recurring_payment(client, t_recurring_payment_response, mocker):
    patched_get = mocker.patch.object(requests, "get", return_value=RequestsMockResponse(200, t_recurring_payment_response))
    response = client.retrieve_recurring_payment("payment-id")
    assert response.id == "payment-id"
    assert patched_get.call_args.kwargs["url"] == client._recurring_url("v1", "/payments/payment-id")


def test_requests_check_recurring_tin_availability(client, t_recurring_availability_response, mocker):
    patched_get = mocker.patch.object(
        requests, "get", return_value=RequestsMockResponse(200, t_recurring_availability_response)
    )
    response = client.check_recurring_tin_availability("1234679304")
    assert response.available is True
    assert patched_get.call_args.kwargs["url"] == client._recurring_url("v1", "/availability/tin/1234679304")


def test_requests_check_recurring_alias_availability(client, t_recurring_availability_response, mocker):
    patched_get = mocker.patch.object(
        requests, "get", return_value=RequestsMockResponse(200, t_recurring_availability_response)
    )
    response = client.check_recurring_alias_availability("46701234567")
    assert response.available is True
    assert patched_get.call_args.kwargs["url"] == client._recurring_url("v1", "/availability/alias/46701234567")


def test_requests_create_prefilled_qr_code(client, mocker):
    patched_post = mocker.patch.object(
        requests,
        "post",
        return_value=RequestsMockResponse(200, headers={"Content-Type": "image/png"}, content=b"png-content"),
    )
    response = client.create_prefilled_qr_code(
        "png",
        payee="1234679304",
        amount=20.0,
        message="QR payment",
        size=300,
        border=1,
        transparent=True,
    )
    assert response == b"png-content"
    assert patched_post.call_args.kwargs["url"] == client._qr_url("v1", "/prefilled")
    assert patched_post.call_args.kwargs["json"] == {
        "format": "png",
        "payee": "1234679304",
        "amount": 20.0,
        "message": "QR payment",
        "size": 300,
        "border": 1,
        "transparent": True,
    }
    assert patched_post.call_args.kwargs["headers"] == {"Accept": "image/png"}


def test_requests_create_prefilled_svg_qr_code(client, mocker):
    mocker.patch.object(
        requests,
        "post",
        return_value=RequestsMockResponse(200, headers={"Content-Type": "image/svg+xml"}, content=b"<svg />"),
    )
    response = client.create_prefilled_qr_code("svg")
    assert response == "<svg />"


def test_requests_create_prefilled_qr_code_swish_error(client, mocker):
    response = RequestsMockResponse(422, text="qr error")
    response.json = lambda: (_ for _ in ()).throw(ValueError())
    mocker.patch.object(requests, "post", return_value=response)
    with pytest.raises(getswish.SwishError) as e_info:
        client.create_prefilled_qr_code("png")
    assert e_info.value.errors == {"error": "qr error"}
