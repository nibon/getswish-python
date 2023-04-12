from dataclasses import dataclass
import pytest
import requests
from requests import HTTPError

import getswish


from .fixtures import *


@dataclass
class RequestsMockResponse:
    status_code: int = 200
    json_data: list[dict] | dict = ""
    headers: dict = dict

    def json(self):
        return self.json_data

    def raise_for_status(self):
        if self.status_code >= 400:
            raise HTTPError()


def test_url(client):
    version, path = "v1", "path"
    assert client._url(version, path) == f"{client.environment.base}{version}{path}"


def test_sign_payload(client):
    a = client._sign_payload({"foo": "bar"})
    assert type(a) == str
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
