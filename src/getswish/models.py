from __future__ import annotations

import dataclasses
from dataclasses import dataclass

from .utils import camel2snake, f_name_conv, snake2camel


@dataclass
class Payment:
    """https://developer.swish.nu/api/payment-request/v2#payment-request-object"""

    id: str | None = None
    callback_url: str | None = None
    payee_alias: str | None = None
    amount: int | float | None = None
    currency: str = "SEK"
    message: str | None = None
    payer_alias: str | None = None
    payer_ssn: str | None = None
    payment_reference: str | None = None
    age_limit: str | None = None
    payee_payment_reference: str | None = None
    status: str | None = None
    location: str | None = None
    payment_request_token: str | None = None
    date_created: str | None = None
    date_paid: str | None = None
    error_code: str | None = None
    error_message: str | None = None
    additional_information: str | None = None
    callback_identifier: str | None = None

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
class Refund:
    """https://developer.swish.nu/api/refunds/v2#refund-request-object"""

    id: str | None = None
    callback_url: str | None = None
    payee_alias: str | None = None
    amount: int | float | None = None
    currency: str = "SEK"
    message: str | None = None
    payer_alias: str | None = None
    payer_ssn: str | None = None
    payment_reference: str | None = None
    age_limit: str | None = None
    payee_payment_reference: str | None = None
    status: str | None = None
    location: str | None = None
    payment_request_token: str | None = None
    date_created: str | None = None
    date_paid: str | None = None
    error_code: str | None = None
    error_message: str | None = None
    additional_information: str | None = None
    callback_identifier: str | None = None
    original_payment_reference: str | None = None
    payer_payment_reference: str | None = None

    @staticmethod
    def from_service(refund_create_object: dict) -> Refund:
        """Map service response format to local Refund class."""

        return Refund(**{camel2snake(k): v for k, v in refund_create_object.items()})

    def to_service(self) -> dict:
        """Remove empty fields and id which is always sent in URL before sending instance to swish service."""

        def _exclude(k, v):
            return v is None or k == "id"

        return {f_name_conv(k, snake2camel): v for k, v in dataclasses.asdict(self).items() if not _exclude(k, v)}


@dataclass
class Payout:
    """https://developer.swish.nu/api/payouts/v1#payout-object"""

    payout_instruction_uuid: str | None = None
    payer_payment_reference: str | None = None
    payment_reference: str | None = None
    signing_certificate_serial_number: str | None = None
    payer_alias: str | None = None
    payee_alias: str | None = None
    payee_ssn: str | None = None
    amount: int | float | None = None
    currency: str = "SEK"
    payout_type: str = "PAYOUT"
    instruction_date: str | None = None
    message: str | None = None
    location: str | None = None
    callback_url: str | None = None
    status: str | None = None
    date_created: str | None = None
    date_paid: str | None = None
    error_code: str | None = None
    error_message: str | None = None
    additional_information: str | None = None
    callback_identifier: str | None = None

    @staticmethod
    def from_service(payout_create_object: dict) -> Payout:
        """Map service response format to local Payout class."""

        return Payout(**{f_name_conv(k, camel2snake, True): v for k, v in payout_create_object.items()})

    def to_service(self) -> dict:
        return {f_name_conv(k, snake2camel): v for k, v in dataclasses.asdict(self).items()}


@dataclass
class RecurringConsent:
    """Recurring payment consent object."""

    consent_id: str | None = None
    callback_url: str | None = None
    payee_alias: str | None = None
    payer_alias: str | None = None
    payer_tin: str | None = None
    payee_payment_reference: str | None = None
    status: str | None = None
    sub_status: str | None = None
    payment_request_token: str | None = None
    location: str | None = None
    activated_at: str | None = None
    date_created: str | None = None
    date_cancelled: str | None = None
    error_code: str | None = None
    error_message: str | None = None
    additional_information: str | None = None
    callback_identifier: str | None = None

    @staticmethod
    def from_service(consent_object: dict) -> RecurringConsent:
        """Map service response format to local RecurringConsent class."""

        flat: dict = {}
        for k, v in consent_object.items():
            if k == "payer" and isinstance(v, dict):
                flat["payer_alias"] = v.get("alias")
            elif k == "payee" and isinstance(v, dict):
                flat["payee_alias"] = v.get("alias")
            else:
                flat[f_name_conv(k, camel2snake, True)] = v
        fields = {f.name for f in dataclasses.fields(RecurringConsent)}
        return RecurringConsent(**{k: v for k, v in flat.items() if k in fields})

    def to_service(self) -> dict:
        """Remove empty fields and consent_id before sending instance to swish service."""

        skip = {"consent_id", "payment_request_token", "location"}
        result: dict = {}
        for k, v in dataclasses.asdict(self).items():
            if v is None or k in skip:
                continue
            if k == "payer_alias":
                result["payer"] = {"alias": v}
            elif k == "payee_alias":
                result["payee"] = {"alias": v}
            elif k == "payer_tin":
                result["tin"] = v
            else:
                result[f_name_conv(k, snake2camel)] = v
        return result


@dataclass
class RecurringPayment:
    """Recurring payment object."""

    payment_id: str | None = None
    consent_id: str | None = None
    callback_url: str | None = None
    payee_alias: str | None = None
    payer_alias: str | None = None
    amount: int | float | None = None
    currency: str = "SEK"
    message: str | None = None
    payee_payment_reference: str | None = None
    payer_payment_reference: str | None = None
    payment_reference: str | None = None
    status: str | None = None
    sub_status: str | None = None
    status_at: str | None = None
    location: str | None = None
    date_created: str | None = None
    date_paid: str | None = None
    error_code: str | None = None
    error_message: str | None = None
    additional_information: str | None = None
    callback_identifier: str | None = None

    @staticmethod
    def from_service(payment_object: dict) -> RecurringPayment:
        """Map service response format to local RecurringPayment class."""

        flat: dict = {}
        for k, v in payment_object.items():
            if k == "payer" and isinstance(v, dict):
                flat["payer_alias"] = v.get("alias")
            elif k == "payee" and isinstance(v, dict):
                flat["payee_alias"] = v.get("alias")
            elif k == "amount" and isinstance(v, dict):
                flat["amount"] = v.get("value")
                flat["currency"] = v.get("currency", "SEK")
            else:
                flat[f_name_conv(k, camel2snake, True)] = v
        fields = {f.name for f in dataclasses.fields(RecurringPayment)}
        return RecurringPayment(**{k: v for k, v in flat.items() if k in fields})

    def to_service(self) -> dict:
        """Remove empty fields and payment_id before sending instance to swish service."""

        skip = {"payment_id", "location"}
        result: dict = {}
        for k, v in dataclasses.asdict(self).items():
            if v is None or k in skip:
                continue
            if k == "payer_alias":
                result["payer"] = {"alias": v}
            elif k == "payee_alias":
                result["payee"] = {"alias": v}
            elif k == "amount":
                result["amount"] = {"value": v, "currency": result.pop("currency", self.currency)}
            elif k == "currency":
                # handled inside amount block above; skip standalone
                pass
            else:
                result[f_name_conv(k, snake2camel)] = v
        return result


@dataclass
class RecurringAvailability:
    """Recurring payment availability response."""

    recurring_is_offered: bool | None = None

    @staticmethod
    def from_service(availability_object: dict) -> RecurringAvailability:
        """Map service response format to local RecurringAvailability class."""

        fields = {f.name for f in dataclasses.fields(RecurringAvailability)}
        flat = {f_name_conv(k, camel2snake, True): v for k, v in availability_object.items()}
        return RecurringAvailability(**{k: v for k, v in flat.items() if k in fields})
