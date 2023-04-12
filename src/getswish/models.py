from __future__ import annotations

import dataclasses
from dataclasses import dataclass

from .utils import camel2snake, f_name_conv, snake2camel


@dataclass
class Payment:
    """https://developer.swish.nu/api/payment-request/v2#payment-request-object"""

    id: str = None
    callback_url: str = None
    payee_alias: str = None
    amount: int | float = None
    currency: str = "SEK"
    message: str = None
    payer_alias: str = None
    payer_ssn: str = None
    payment_reference: str = None
    age_limit: str = None
    payee_payment_reference: str = None
    status: str = None
    location: str = None
    payment_request_token: str = None
    date_created: str = None
    date_paid: str = None
    error_code: str = None
    error_message: str = None
    additional_information: str = None

    @staticmethod
    def from_service(payment_request_object: dict) -> Payment:
        """Map service response format to local Payment class."""

        return Payment(**{f_name_conv(k, camel2snake, True): v for k, v in payment_request_object.items()})

    def to_service(self) -> dict:
        """Remove empty fields and id which is always sent in URL before sending instance to swish service."""

        def _exclude(k, v):
            return v is None or k == "id"

        return {f_name_conv(k, snake2camel): v for k, v in dataclasses.asdict(self).items() if not _exclude(k, v)}


@dataclass
class Refund(Payment):
    """https://developer.swish.nu/api/refunds/v2#refund-request-object"""

    original_payment_reference: str = None
    payer_payment_reference: str = None

    @staticmethod
    def from_service(refund_create_object: dict) -> Refund:
        """Map service response format to local Refund class."""

        return Refund(**{camel2snake(k): v for k, v in refund_create_object.items()})


@dataclass
class Payout:
    """https://developer.swish.nu/api/payouts/v1#payout-object"""

    payout_instruction_uuid: str = None
    payer_payment_reference: str = None
    payment_reference: str = None
    signing_certificate_serial_number: str = None
    payer_alias: str = None
    payee_alias: str = None
    payee_ssn: str = None
    amount: int | float = None
    currency: str = "SEK"
    payout_type: str = "PAYOUT"
    instruction_date: str = None
    message: str = None
    location: str = None
    callback_url: str = None
    status: str = None
    date_created: str = None
    date_paid: str = None
    error_code: str = None
    error_message: str = None
    additional_information: str = None

    @staticmethod
    def from_service(payout_create_object: dict) -> Payout:
        """Map service response format to local Payout class."""

        return Payout(**{f_name_conv(k, camel2snake, True): v for k, v in payout_create_object.items()})

    def to_service(self) -> dict:
        return {f_name_conv(k, snake2camel): v for k, v in dataclasses.asdict(self).items()}
