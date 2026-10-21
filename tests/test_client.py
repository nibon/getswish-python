import base64
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

from cryptography import x509
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
import pytest
import requests
from requests import HTTPError

import getswish
from getswish.environments import TestCertificates


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


def test_default_clients_have_independent_configuration():
    first = getswish.SwishClient()
    second = getswish.SwishClient()
    assert first.environment is not second.environment
    assert first.certificates is not second.certificates
    for name in ("communication", "verify", "signing"):
        assert getattr(first.certificates, name) is not getattr(second.certificates, name)
        assert getattr(first.certificates, name) is not getattr(TestCertificates, name)

    first.environment.base = "https://changed.example/"
    first.certificates.communication.public = "changed.pem"
    first.certificates.verify.public = "changed-ca.pem"
    first.certificates.signing.private_key = "changed.key"

    assert second.environment.base == getswish.TestEnvironment.base
    assert second.certificates.communication.public == TestCertificates.communication.public
    assert second.certificates.verify.public == TestCertificates.verify.public
    assert second.certificates.signing.private_key == TestCertificates.signing.private_key
    assert getswish.SwishClient().certificates.communication.public == TestCertificates.communication.public


def test_explicit_client_configuration_preserves_identity():
    client = getswish.SwishClient(getswish.TestEnvironment, TestCertificates)
    assert client.environment is getswish.TestEnvironment
    assert client.certificates is TestCertificates


def test_client_init(client):
    assert client is not None


@pytest.mark.parametrize("options", [
    {"environment": getswish.TestEnvironment},
    {"certificates": getswish.Certificates(None, None)},
])
def test_client_init_requires_environment_and_certificates(options):
    with pytest.raises(ValueError, match="environment and certificates must be provided together"):
        getswish.SwishClient(**options)


def test_url(client):
    version, path = "v1", "path"
    assert client._url(version, path) == f"{client.environment.base}{version}{path}"


def test_recurring_url(client):
    path = "/recurring/merchant/v1/consents"
    assert client._recurring_url(path) == f"{client.environment.recurring_base}{path}"


def test_qr_url(client):
    path = "v1/prefilled"
    assert client._qr_url(path) == f"{client.environment.qr_base}{path}"


def test_sign_payload(client):
    a = client._sign_payload({"foo": "bar"})
    assert isinstance(a, str)
    assert len(a) == 684


def test_sign_payload_missing(client):
    client.certificates.signing = None
    with pytest.raises(ValueError, match="signing certificate private key is required"):
        client._sign_payload({"foo": "bar"})


def test_sign_payload_missing_private_key(client):
    client.certificates.signing.private_key = None
    with pytest.raises(ValueError, match="signing certificate private key is required"):
        client._sign_payload({"foo": "bar"})


def test_create_payout_missing_signing_certificate(client, callback_url):
    client.certificates.signing = None
    with pytest.raises(ValueError, match="signing certificate is required for payouts"):
        client.create_payout("reference", "46701234567", "197001019876", 10, callback_url)


@pytest.mark.parametrize("missing", ["communication", "verify"])
def test_requests_missing_certificate(client, missing):
    setattr(client.certificates, missing, None)
    with pytest.raises(ValueError, match="communication and verify certificates are required"):
        client._requests("get", "https://example.com")


@pytest.mark.parametrize("method", ["get", "post", "put", "patch", "delete"])
def test_requests_default_timeout(client, mocker, method):
    request = mocker.patch.object(requests, method, return_value=RequestsMockResponse())

    client._requests(method, "https://example.com")

    assert request.call_args.kwargs["timeout"] == (10.0, 30.0)


@pytest.mark.parametrize("timeout", [5.0, (2.0, 15.0), None])
def test_client_custom_timeout(callback_url, mocker, timeout):
    client = getswish.SwishClient(timeout=timeout)
    request = mocker.patch.object(requests, "put", return_value=RequestsMockResponse(headers={}))

    client.create_payment(20.0, callback_url)

    assert request.call_args.kwargs["timeout"] == timeout
    assert "timeout" not in request.call_args.kwargs["json"]


@pytest.mark.parametrize("timeout", [3.0, (1.0, 5.0), None])
def test_requests_explicit_timeout_override(client, mocker, timeout):
    request = mocker.patch.object(requests, "get", return_value=RequestsMockResponse())

    client._requests("get", "https://example.com", timeout=timeout)

    assert request.call_args.kwargs["timeout"] == timeout


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


def test_requests_swish_error_list_preserves_details(client, callback_url, mocker):
    errors = [
        {"errorCode": "first", "errorMessage": "invalid alias", "traceId": "trace-id", "field": "payeeAlias"},
        {"errorCode": "second", "errorMessage": "invalid amount", "field": "amount"},
    ]
    mocker.patch.object(requests, "put", return_value=RequestsMockResponse(422, errors))

    with pytest.raises(getswish.SwishError) as error:
        client.create_payment(20.0, callback_url)

    assert error.value.trace_id == "trace-id"
    assert error.value.errors == {"first": "invalid alias", "second": "invalid amount"}
    assert error.value.raw_errors == errors


def test_requests_swish_error_text(client, callback_url, mocker):
    response = RequestsMockResponse(422, text="bad gateway")
    response.json = lambda: (_ for _ in ()).throw(ValueError())
    mocker.patch.object(requests, "put", return_value=response)
    with pytest.raises(getswish.SwishError) as e_info:
        client.create_payment(20.0, callback_url)
    assert e_info.value.errors == {"error": "bad gateway"}


@pytest.mark.parametrize("status", [400, 401, 403, 404, 415, 422, 429, 500, 503, 599])
def test_requests_swish_error_non_json_text(client, callback_url, mocker, status):
    response = RequestsMockResponse(status, text="request rejected")
    response.json = lambda: (_ for _ in ()).throw(ValueError())
    mocker.patch.object(requests, "put", return_value=response)
    with pytest.raises(getswish.SwishError) as error:
        client.create_payment(20.0, callback_url)
    assert error.value.errors == {"error": "request rejected"}
    assert error.value.raw_errors == "request rejected"
    assert error.value.response is response


@pytest.mark.parametrize("status", [400, 401, 403, 404, 415, 422, 429, 500, 503, 599])
def test_requests_empty_error_body_raises_swish_error(client, mocker, status):
    response = RequestsMockResponse(status)
    response.json = lambda: (_ for _ in ()).throw(ValueError())
    mocker.patch.object(requests, "post", return_value=response)
    with pytest.raises(getswish.SwishError) as error:
        client.create_commerce_qr_code("commerce-token", "png")
    assert error.value.errors == {"error": f"HTTP {status}"}
    assert error.value.raw_errors == ""
    assert error.value.response is response


@pytest.mark.parametrize("json_data", [[], {}, None, False, 0, ""])
def test_requests_empty_json_error_raises_swish_error(client, callback_url, mocker, json_data):
    mocker.patch.object(requests, "put", return_value=RequestsMockResponse(422, json_data))
    with pytest.raises(getswish.SwishError) as error:
        client.create_payment(20.0, callback_url)
    assert error.value.errors == {"error": "HTTP 422"}
    assert error.value.raw_errors is json_data


def test_requests_unexpected_json_error_raises_swish_error(client, mocker):
    payload = {"errorCode": ["upstream"], "errorMessage": {"detail": "failed"}}
    response = requests.Response()
    response.status_code = 500
    response._content = json.dumps(payload).encode()
    mocker.patch.object(requests, "get", return_value=response)
    with pytest.raises(getswish.SwishError) as caught:
        client._requests("get", "https://example.com")
    assert caught.value.errors == {"['upstream']": "{'detail': 'failed'}"}
    assert caught.value.raw_errors == payload
    assert caught.value.response is response


@pytest.mark.parametrize("status", [400, 401, 403, 404, 415, 422, 429, 500, 503, 599])
def test_requests_json_error_raises_swish_error(client, mocker, status):
    error = {"errorCode": "server-error", "errorMessage": "failed"}
    response = RequestsMockResponse(status, error)
    mocker.patch.object(requests, "post", return_value=response)
    with pytest.raises(getswish.SwishError) as caught:
        client.create_commerce_qr_code("commerce-token", "png")
    assert caught.value.errors == {"server-error": "failed"}
    assert caught.value.raw_errors == error
    assert caught.value.response is response


@pytest.mark.parametrize("status", [200, 201, 204, 302])
def test_requests_success_response_unchanged(client, mocker, status):
    response = RequestsMockResponse(status)
    parse_json = mocker.patch.object(response, "json")
    mocker.patch.object(requests, "get", return_value=response)
    assert client._requests("get", "https://example.com") is response
    parse_json.assert_not_called()


@pytest.mark.parametrize("exception", [requests.ConnectionError, requests.Timeout, requests.exceptions.SSLError])
def test_requests_transport_error_unchanged(client, mocker, exception):
    failure = exception("request failed")
    mocker.patch.object(requests, "get", side_effect=failure)
    with pytest.raises(exception) as caught:
        client._requests("get", "https://example.com")
    assert caught.value is failure


def test_requests_create_payment(client, callback_url, t_payment_response, t_payment_created_headers, mocker):
    patched_response = RequestsMockResponse(201, t_payment_response, t_payment_created_headers)
    mocker.patch.object(requests, "put", return_value=patched_response)
    response = client.create_payment(20.0, callback_url)
    assert response.location == "https://payment/path/"
    assert response.payment_request_token == "payment_token"


@pytest.mark.parametrize("payee_alias", [None, "1234567890"])
def test_create_payment_payee_alias(client, callback_url, mocker, payee_alias):
    patched_put = mocker.patch.object(requests, "put", return_value=RequestsMockResponse(201, headers={}))
    options = {} if payee_alias is None else {"payee_alias": payee_alias}

    payment = client.create_payment(20.0, callback_url, **options)

    expected = payee_alias or client.merchant_swish_number
    assert payment.payee_alias == expected
    assert patched_put.call_args.kwargs["json"]["payeeAlias"] == expected


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


def test_requests_create_payout_signature_matches_posted_payload(client, mocker, callback_url):
    patched_post = mocker.patch.object(requests, "post", return_value=RequestsMockResponse(201, headers={}))
    client.create_payout("order-123", "46731234567", "198810236383", 20.0, callback_url)

    posted = patched_post.call_args.kwargs["json"]
    payload = posted["payload"]
    assert patched_post.call_args.kwargs["url"] == client._url("v1", "/payouts")
    assert posted["callbackUrl"] == callback_url
    assert payload["callbackUrl"] is None
    assert payload["payeeSSN"] == "198810236383"
    assert payload["payerPaymentReference"] == "order-123"
    instruction_date = payload["instructionDate"]
    assert instruction_date.endswith("Z")
    assert len(instruction_date) == len("2026-10-21T12:34:56Z")
    parsed_date = datetime.fromisoformat(instruction_date.replace("Z", "+00:00"))
    assert parsed_date.tzinfo == timezone.utc
    assert parsed_date.microsecond == 0

    certificate = x509.load_pem_x509_certificate(Path(client.certificates.signing.public).read_bytes())
    assert payload["signingCertificateSerialNumber"] == format(certificate.serial_number, "X")
    public_key = certificate.public_key()
    signature = base64.b64decode(posted["signature"], validate=True)
    # The client signs the SHA-512 digest as data, so RSA/SHA-512 hashes that digest again.
    digest = hashlib.sha512(json.dumps(payload).encode("utf-8")).digest()
    public_key.verify(signature, digest, padding.PKCS1v15(), hashes.SHA512())

    tampered = {**payload, "amount": 21.0}
    tampered_digest = hashlib.sha512(json.dumps(tampered).encode("utf-8")).digest()
    with pytest.raises(InvalidSignature):
        public_key.verify(signature, tampered_digest, padding.PKCS1v15(), hashes.SHA512())


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
    called_url = patched_post.call_args.kwargs["url"]
    assert called_url.startswith(client.environment.recurring_base + "/recurring/merchant/v1/consents/")
    assert len(called_url.split("/")[-1]) == 32  # auto-generated UUID hex
    assert patched_post.call_args.kwargs["json"]["payer"] == {"alias": "46701234567"}
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
    called_url = patched_post.call_args.kwargs["url"]
    assert "/recurring/merchant/v1/consents/" in called_url
    assert called_url.endswith("/token")
    assert patched_post.call_args.kwargs["json"]["payee"] == {"alias": client.merchant_swish_number}
    assert patched_post.call_args.kwargs["headers"] is None


def test_requests_update_recurring_consent_callback(client, callback_url, t_recurring_consent_response, mocker):
    patched_put = mocker.patch.object(
        requests, "put", return_value=RequestsMockResponse(200, t_recurring_consent_response)
    )
    response = client.update_recurring_consent_callback_url("consent-id", callback_url, on_behalf_of="partner")
    assert response.consent_id == "consent-id"
    expected_url = client._recurring_url("/recurring/merchant/v1/consent/consent-id/callback")
    assert patched_put.call_args.kwargs["url"] == expected_url
    assert patched_put.call_args.kwargs["json"] == {"callbackUrl": callback_url}
    assert patched_put.call_args.kwargs["headers"] == {"onBehalfOf": "partner"}


def test_requests_update_recurring_consent_callback_without_response_body(client, callback_url, mocker):
    response = RequestsMockResponse(204)
    response.json = lambda: (_ for _ in ()).throw(ValueError())
    patched_put = mocker.patch.object(requests, "put", return_value=response)

    consent = client.update_recurring_consent_callback_url("consent-id", callback_url)

    assert consent.consent_id == "consent-id"
    assert consent.callback_url == callback_url
    assert patched_put.call_args.kwargs["json"] == {"callbackUrl": callback_url}


def test_requests_retrieve_recurring_consent(client, t_recurring_consent_response, mocker):
    patched_get = mocker.patch.object(
        requests, "get", return_value=RequestsMockResponse(200, t_recurring_consent_response)
    )
    response = client.retrieve_recurring_consent("consent-id")
    assert response.consent_id == "consent-id"
    assert patched_get.call_args.kwargs["url"] == client._recurring_url("/recurring/merchant/v1/consents/consent-id")


def test_requests_delete_recurring_consent(client, mocker):
    patched_delete = mocker.patch.object(requests, "delete", return_value=RequestsMockResponse(204))
    response = client.delete_recurring_consent("consent-id", on_behalf_of="partner")
    assert response.status_code == 204
    assert patched_delete.call_args.kwargs["url"] == client._recurring_url("/recurring/merchant/v1/consents/consent-id")
    assert patched_delete.call_args.kwargs["headers"] == {"onBehalfOf": "partner"}


def test_requests_create_recurring_payment(client, callback_url, t_recurring_payment_response, mocker):
    patched_post = mocker.patch.object(
        requests,
        "post",
        return_value=RequestsMockResponse(201, t_recurring_payment_response, {"Location": "https://payment/path/"}),
    )
    response = client.create_recurring_payment(
        "consent-id", 20.0, callback_url, on_behalf_of="partner", message="Recurring payment"
    )
    assert response.location == "https://payment/path/"
    called_url = patched_post.call_args.kwargs["url"]
    assert "/recurring/merchant/v1/payments/single/" in called_url
    assert patched_post.call_args.kwargs["json"]["consentId"] == "consent-id"
    assert patched_post.call_args.kwargs["json"]["amount"] == {"value": 20.0, "currency": "SEK"}
    assert patched_post.call_args.kwargs["headers"] == {"onBehalfOf": "partner"}


def test_requests_retrieve_recurring_payment(client, t_recurring_payment_response, mocker):
    patched_get = mocker.patch.object(
        requests, "get", return_value=RequestsMockResponse(200, t_recurring_payment_response)
    )
    response = client.retrieve_recurring_payment("payment-id")
    assert response.payment_id == "payment-id"
    expected_url = client._recurring_url("/recurring/merchant/v1/payments/single/payment-id/status")
    assert patched_get.call_args.kwargs["url"] == expected_url


def test_requests_check_recurring_tin_availability(client, t_recurring_availability_response, mocker):
    patched_post = mocker.patch.object(
        requests, "post", return_value=RequestsMockResponse(200, t_recurring_availability_response)
    )
    response = client.check_recurring_tin_availability("1234679304")
    assert response.recurring_is_offered is True
    assert patched_post.call_args.kwargs["url"] == client._recurring_url("/recurring/merchant/v1/recurring/tin")
    assert patched_post.call_args.kwargs["json"] == {"tin": "1234679304"}


def test_requests_check_recurring_alias_availability(client, t_recurring_availability_response, mocker):
    patched_post = mocker.patch.object(
        requests, "post", return_value=RequestsMockResponse(200, t_recurring_availability_response)
    )
    response = client.check_recurring_alias_availability("46701234567")
    assert response.recurring_is_offered is True
    assert patched_post.call_args.kwargs["url"] == client._recurring_url("/recurring/merchant/v1/recurring/alias")
    assert patched_post.call_args.kwargs["json"] == {"alias": "46701234567"}


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
    assert patched_post.call_args.kwargs["url"] == client._qr_url("v1/prefilled")
    assert patched_post.call_args.kwargs["json"] == {
        "format": "png",
        "payee": {"value": "1234679304", "editable": False},
        "amount": {"value": 20.0, "editable": False},
        "message": {"value": "QR payment", "editable": False},
        "size": 300,
        "border": 1,
        "transparent": True,
    }
    assert patched_post.call_args.kwargs["headers"] == {"Accept": "image/png"}


def test_requests_create_prefilled_qr_code_editable(client, mocker):
    patched_post = mocker.patch.object(
        requests,
        "post",
        return_value=RequestsMockResponse(200, headers={"Content-Type": "image/png"}, content=b"png-content"),
    )
    client.create_prefilled_qr_code("png", payee="1234679304", payee_editable=True, amount=20.0, amount_editable=True)
    assert patched_post.call_args.kwargs["json"]["payee"] == {"value": "1234679304", "editable": True}
    assert patched_post.call_args.kwargs["json"]["amount"] == {"value": 20.0, "editable": True}


def test_requests_create_prefilled_qr_invalid_format(client):
    with pytest.raises(ValueError, match="qr_format"):
        client.create_prefilled_qr_code("gif")


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


def test_requests_create_commerce_qr_code(client, mocker):
    patched_post = mocker.patch.object(
        requests,
        "post",
        return_value=RequestsMockResponse(200, headers={"Content-Type": "image/png"}, content=b"commerce-png"),
    )
    response = client.create_commerce_qr_code("commerce-token", "png", size=300)
    assert response == b"commerce-png"
    assert patched_post.call_args.kwargs["url"] == client._qr_url("v1/commerce")
    assert patched_post.call_args.kwargs["json"] == {"token": "commerce-token", "format": "png", "size": 300}
    assert patched_post.call_args.kwargs["headers"] == {"Accept": "image/png"}


def test_requests_create_commerce_qr_invalid_format(client):
    with pytest.raises(ValueError, match="qr_format"):
        client.create_commerce_qr_code("token", "bmp")


def test_requests_create_commerce_svg_qr_code(client, mocker):
    patched_post = mocker.patch.object(
        requests,
        "post",
        return_value=RequestsMockResponse(200, headers={"Content-Type": "image/svg+xml"}, content=b"<svg />"),
    )
    assert client.create_commerce_qr_code("commerce-token", "svg") == "<svg />"
    assert patched_post.call_args.kwargs["headers"] == {"Accept": "image/svg+xml"}


def test_requests_create_commerce_svg_qr_code_unexpected_content_type(client, mocker):
    mocker.patch.object(
        requests,
        "post",
        return_value=RequestsMockResponse(200, headers={"Content-Type": "text/html"}, content=b"<html>unexpected</html>"),
    )
    assert client.create_commerce_qr_code("commerce-token", "svg") == "<html>unexpected</html>"
