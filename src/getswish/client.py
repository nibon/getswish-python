import base64
import hashlib
import json
import logging
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timezone

import requests
import rsa
from requests import Response

from .environments import Certificates, Environment, TestEnvironment, TestCertificates
from .exceptions import SwishError
from .models import Payment, Payout, RecurringAvailability, RecurringConsent, RecurringPayment, Refund
from .utils import generate_transaction_id

logger = logging.getLogger("getswish")
logger.addHandler(logging.NullHandler())


@dataclass
class SwishClient:
    environment: Environment | None = None
    certificates: Certificates | None = None
    merchant_swish_number: str = "1234679304"

    def __post_init__(self):
        if self.environment is None and self.certificates is None:
            self.environment = deepcopy(TestEnvironment)
            self.certificates = deepcopy(TestCertificates)
        if self.environment is None or self.certificates is None:
            raise ValueError("environment and certificates must be provided together")
        logger.debug("getswish.env: %s", self.environment.name)

    @property
    def _environment(self) -> Environment:
        if self.environment is None:
            raise ValueError("environment is required")
        return self.environment

    @property
    def _certificates(self) -> Certificates:
        if self.certificates is None:
            raise ValueError("certificates are required")
        return self.certificates

    def _url(self, version: str, path: str) -> str:
        return f"{self._environment.base}{version}{path}"

    def _recurring_url(self, path: str) -> str:
        base = self._environment.recurring_base or self._environment.base
        return f"{base}{path}"

    def _qr_url(self, path: str) -> str:
        base = self._environment.qr_base or self._environment.base
        return f"{base}{path}"

    def _partner_headers(self, on_behalf_of: str | None = None, headers: dict | None = None) -> dict | None:
        request_headers = dict(headers or {})
        if on_behalf_of is not None:
            request_headers["onBehalfOf"] = on_behalf_of
        return request_headers or None

    def _requests(self, method: str, url: str, /, **kwargs) -> Response:
        """Add client certificates and raise SwishError for HTTP error responses."""

        certificates = self._certificates
        if certificates.communication is None or certificates.verify is None:
            raise ValueError("communication and verify certificates are required")
        kwargs.update(
            cert=(
                certificates.communication.public,
                certificates.communication.private_key,
            ),
            verify=certificates.verify.public,
        )
        response = getattr(requests, method)(url=url, **kwargs)
        if 400 <= response.status_code < 600:
            try:
                errors = response.json()
            except ValueError:
                errors = response.text
            raise SwishError(errors, response=response)
        return response

    def _sign_payload(self, payload: dict) -> str:
        """
        https://developer.swish.nu/documentation/guides/make-a-payout
        https://developer.swish.nu/documentation/getting-started/swish-payout-api
        """

        signing = self._certificates.signing
        if signing is None or signing.private_key is None:
            raise ValueError("signing certificate private key is required for payouts")
        payload_json_encoded = json.dumps(payload).encode("utf-8")
        payload_hash = hashlib.sha512(payload_json_encoded).digest()
        with open(signing.private_key, mode="rb") as private_file:
            key_data = private_file.read()
        private_key = rsa.PrivateKey.load_pkcs1(key_data)
        signature = rsa.sign(payload_hash, private_key, "SHA-512")
        signature_b64 = base64.b64encode(signature)
        return signature_b64.decode("utf-8")

    def create_payment(
        self,
        amount: int | float,
        callback_url: str,
        payer_alias: str | None = None,
        /,
        **kwargs,
    ) -> Payment:
        """https://developer.swish.nu/api/payment-request/v2#create-payment-request"""

        payment = Payment(
            payee_alias=kwargs.pop("payee_alias", self.merchant_swish_number),
            payer_alias=payer_alias,
            amount=amount,
            callback_url=callback_url,
            **kwargs,
        )
        payment.id = payment.id or generate_transaction_id()
        response = self._requests(
            "put",
            self._url("v2", f"/paymentrequests/{payment.id}"),
            json=payment.to_service(),
        )
        payment.location = response.headers.get("Location")
        payment.payment_request_token = response.headers.get("PaymentRequestToken")
        return payment

    def retrieve_payment(self, transaction_id: str) -> Payment:
        """https://developer.swish.nu/api/payment-request/v2#retrieve-payment-request"""

        return Payment.from_service(self._requests("get", self._url("v1", f"/paymentrequests/{transaction_id}")).json())

    def cancel_payment(self, transaction_id: str) -> Payment:
        """https://developer.swish.nu/api/payment-request/v2#cancel-payment-request"""

        return Payment.from_service(
            self._requests(
                "patch",
                self._url("v1", f"/paymentrequests/{transaction_id}"),
                json=[{"op": "replace", "path": "/status", "value": "cancelled"}],
                headers={"Content-Type": "application/json-patch+json"},
            ).json()
        )

    def create_refund(
        self,
        original_payment_reference: str,
        callback_url: str,
        payee_alias: str,
        amount: int | float,
        /,
        **kwargs,
    ) -> Refund:
        """https://developer.swish.nu/api/refunds/v2#create-refund"""

        refund = Refund(
            original_payment_reference=original_payment_reference,
            callback_url=callback_url,
            payee_alias=payee_alias,
            amount=amount,
            payer_alias=kwargs.pop("payer_alias", self.merchant_swish_number),
            **kwargs,
        )
        refund.id = refund.id or generate_transaction_id()
        response = self._requests("put", self._url("v2", f"/refunds/{refund.id}"), json=refund.to_service())
        refund.location = response.headers.get("Location")
        return refund

    def retrieve_refund(self, transaction_id: str) -> Refund:
        """https://developer.swish.nu/api/refunds/v1#retrieve-refund"""

        return Refund.from_service(self._requests("get", self._url("v1", f"/refunds/{transaction_id}")).json())

    def create_payout(
        self,
        payer_payment_reference: str,
        payee_alias: str,
        payee_ssn: str,
        amount: int | float,
        callback_url: str,
        /,
        **kwargs,
    ) -> Payout:
        """https://developer.swish.nu/api/payouts/v1#create-payout"""

        signing = self._certificates.signing
        if signing is None:
            raise ValueError("signing certificate is required for payouts")
        payout = Payout(
            payer_payment_reference=payer_payment_reference,
            payee_alias=payee_alias,
            payee_ssn=payee_ssn,
            amount=amount,
            payer_alias=kwargs.pop("payer_alias", self.merchant_swish_number),
            instruction_date=datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
            signing_certificate_serial_number=signing.public_serial,
            **kwargs,
        )
        payout.payout_instruction_uuid = payout.payout_instruction_uuid or generate_transaction_id()
        payload = payout.to_service()
        url = self._url("v1", "/payouts")
        payload = {
            "payload": payload,
            "callbackUrl": callback_url,
            "signature": self._sign_payload(payload),
        }
        response = self._requests("post", url, json=payload)
        logger.debug("getswish.create_payout.response.text: %s", response.text)
        payout.location = response.headers.get("Location")
        return payout

    def retrieve_payout(self, transaction_id: str) -> Payout:
        """https://developer.swish.nu/api/payouts/v1#retrieve-payout"""

        response = self._requests("get", self._url("v1", f"/payouts/{transaction_id}"))
        logger.debug("getswish.retrieve_payout.response.text: %s", response.text)
        return Payout.from_service(response.json())

    def create_recurring_ecommerce_consent(
        self,
        callback_url: str,
        payer_alias: str | None = None,
        /,
        on_behalf_of: str | None = None,
        **kwargs,
    ) -> RecurringConsent:
        """https://developer.swish.nu/documentation/getting-started/swish-recurring-payments-api"""

        consent = RecurringConsent(
            callback_url=callback_url,
            payee_alias=kwargs.pop("payee_alias", self.merchant_swish_number),
            payer_alias=payer_alias,
            **kwargs,
        )
        consent.consent_id = consent.consent_id or generate_transaction_id()
        response = self._requests(
            "post",
            self._recurring_url(f"/recurring/merchant/v1/consents/{consent.consent_id}"),
            json=consent.to_service(),
            headers=self._partner_headers(on_behalf_of),
        )
        consent.location = response.headers.get("Location")
        return consent

    def create_recurring_mcommerce_consent(
        self,
        callback_url: str,
        /,
        on_behalf_of: str | None = None,
        **kwargs,
    ) -> RecurringConsent:
        """https://developer.swish.nu/documentation/getting-started/swish-recurring-payments-api"""

        consent = RecurringConsent(
            callback_url=callback_url,
            payee_alias=kwargs.pop("payee_alias", self.merchant_swish_number),
            **kwargs,
        )
        consent.consent_id = consent.consent_id or generate_transaction_id()
        response = self._requests(
            "post",
            self._recurring_url(f"/recurring/merchant/v1/consents/{consent.consent_id}/token"),
            json=consent.to_service(),
            headers=self._partner_headers(on_behalf_of),
        )
        consent.location = response.headers.get("Location")
        consent.payment_request_token = response.headers.get("PaymentRequestToken")
        return consent

    def update_recurring_consent_callback_url(
        self,
        consent_id: str,
        callback_url: str,
        /,
        on_behalf_of: str | None = None,
    ) -> RecurringConsent:
        """https://developer.swish.nu/documentation/getting-started/swish-recurring-payments-api"""

        response = self._requests(
            "put",
            self._recurring_url(f"/recurring/merchant/v1/consent/{consent_id}/callback"),
            json={"callbackUrl": callback_url},
            headers=self._partner_headers(on_behalf_of),
        )
        try:
            return RecurringConsent.from_service(response.json())
        except ValueError:
            return RecurringConsent(consent_id=consent_id, callback_url=callback_url)

    def retrieve_recurring_consent(
        self,
        consent_id: str,
        /,
        on_behalf_of: str | None = None,
    ) -> RecurringConsent:
        """https://developer.swish.nu/documentation/getting-started/swish-recurring-payments-api"""

        response = self._requests(
            "get",
            self._recurring_url(f"/recurring/merchant/v1/consents/{consent_id}"),
            headers=self._partner_headers(on_behalf_of),
        )
        return RecurringConsent.from_service(response.json())

    def delete_recurring_consent(
        self,
        consent_id: str,
        /,
        on_behalf_of: str | None = None,
    ) -> Response:
        """https://developer.swish.nu/documentation/getting-started/swish-recurring-payments-api"""

        return self._requests(
            "delete",
            self._recurring_url(f"/recurring/merchant/v1/consents/{consent_id}"),
            headers=self._partner_headers(on_behalf_of),
        )

    def create_recurring_payment(
        self,
        consent_id: str,
        amount: int | float,
        callback_url: str,
        /,
        on_behalf_of: str | None = None,
        **kwargs,
    ) -> RecurringPayment:
        """https://developer.swish.nu/documentation/getting-started/swish-recurring-payments-api"""

        payment = RecurringPayment(
            consent_id=consent_id,
            amount=amount,
            callback_url=callback_url,
            payee_alias=kwargs.pop("payee_alias", self.merchant_swish_number),
            **kwargs,
        )
        payment.payment_id = payment.payment_id or generate_transaction_id()
        response = self._requests(
            "post",
            self._recurring_url(f"/recurring/merchant/v1/payments/single/{payment.payment_id}"),
            json=payment.to_service(),
            headers=self._partner_headers(on_behalf_of),
        )
        payment.location = response.headers.get("Location")
        return payment

    def retrieve_recurring_payment(
        self,
        payment_id: str,
        /,
        on_behalf_of: str | None = None,
    ) -> RecurringPayment:
        """https://developer.swish.nu/documentation/getting-started/swish-recurring-payments-api"""

        response = self._requests(
            "get",
            self._recurring_url(f"/recurring/merchant/v1/payments/single/{payment_id}/status"),
            headers=self._partner_headers(on_behalf_of),
        )
        return RecurringPayment.from_service(response.json())

    def check_recurring_tin_availability(
        self,
        tin: str,
        /,
        on_behalf_of: str | None = None,
    ) -> RecurringAvailability:
        """https://developer.swish.nu/documentation/getting-started/swish-recurring-payments-api"""

        response = self._requests(
            "post",
            self._recurring_url("/recurring/merchant/v1/recurring/tin"),
            json={"tin": tin},
            headers=self._partner_headers(on_behalf_of),
        )
        return RecurringAvailability.from_service(response.json())

    def check_recurring_alias_availability(
        self,
        alias: str,
        /,
        on_behalf_of: str | None = None,
    ) -> RecurringAvailability:
        """https://developer.swish.nu/documentation/getting-started/swish-recurring-payments-api"""

        response = self._requests(
            "post",
            self._recurring_url("/recurring/merchant/v1/recurring/alias"),
            json={"alias": alias},
            headers=self._partner_headers(on_behalf_of),
        )
        return RecurringAvailability.from_service(response.json())

    def create_prefilled_qr_code(
        self,
        qr_format: str,
        /,
        **kwargs,
    ) -> bytes | str:
        """https://developer.swish.nu/documentation/getting-started/swish-qr-code"""

        if qr_format not in {"jpg", "png", "svg"}:
            raise ValueError(f"qr_format must be one of 'jpg', 'png', 'svg'; got {qr_format!r}")

        def _qr_field(key: str) -> dict:
            value = kwargs.pop(key, None)
            editable = kwargs.pop(f"{key}_editable", False)
            return {key: {"value": value, "editable": editable}} if value is not None else {}

        payload: dict = {"format": qr_format}
        payload.update(_qr_field("payee"))
        payload.update(_qr_field("amount"))
        payload.update(_qr_field("message"))
        payload.update({k: v for k, v in kwargs.items() if v is not None})
        response = self._requests(
            "post",
            self._qr_url("v1/prefilled"),
            json=payload,
            headers={"Accept": "image/svg+xml" if qr_format == "svg" else f"image/{qr_format}"},
        )
        if qr_format == "svg":
            return response.content.decode("utf-8")
        return response.content

    def create_commerce_qr_code(
        self,
        token: str,
        qr_format: str,
        /,
        **kwargs,
    ) -> bytes | str:
        """https://developer.swish.nu/documentation/getting-started/swish-qr-code"""

        if qr_format not in {"jpg", "png", "svg"}:
            raise ValueError(f"qr_format must be one of 'jpg', 'png', 'svg'; got {qr_format!r}")
        payload = {"token": token, "format": qr_format, **{k: v for k, v in kwargs.items() if v is not None}}
        response = self._requests(
            "post",
            self._qr_url("v1/commerce"),
            json=payload,
            headers={"Accept": "image/svg+xml" if qr_format == "svg" else f"image/{qr_format}"},
        )
        if qr_format == "svg":
            return response.content.decode("utf-8")
        return response.content
