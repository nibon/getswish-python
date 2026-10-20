from getswish import Payment, Payout, RecurringAvailability, RecurringConsent, RecurringPayment, Refund
from getswish.utils import camel2snake, f_name_conv

from .fixtures import *  # noqa: F403


def test_payment_from_service(t_payment_response):
    payment = Payment.from_service(t_payment_response)
    for k, v in t_payment_response.items():
        assert getattr(payment, f_name_conv(k, camel2snake, True)) == v


def test_payment_to_service(t_payment):
    service_json_data = t_payment.to_service()
    for k, v in service_json_data.items():
        assert getattr(t_payment, f_name_conv(k, camel2snake, True)) == v


def test_refund_from_service(t_refund_response):
    refund = Refund.from_service(t_refund_response)
    for k, v in t_refund_response.items():
        assert getattr(refund, f_name_conv(k, camel2snake, True)) == v


def test_refund_to_service(t_refund):
    service_json_data = t_refund.to_service()
    for k, v in service_json_data.items():
        assert getattr(t_refund, f_name_conv(k, camel2snake, True)) == v


def test_payout_from_service(t_payout_response):
    payout = Payout.from_service(t_payout_response)
    for k, v in t_payout_response.items():
        assert getattr(payout, f_name_conv(k, camel2snake, True)) == v


def test_payout_to_service(t_payout):
    service_json_data = t_payout.to_service()
    for k, v in service_json_data.items():
        assert getattr(t_payout, f_name_conv(k, camel2snake, True)) == v


def test_recurring_consent_from_service(t_recurring_consent_response):
    consent = RecurringConsent.from_service(t_recurring_consent_response)
    assert consent.consent_id == "consent-id"
    assert consent.payer_alias == "46701234567"
    assert consent.payee_alias == "1234679304"
    assert consent.status == "ACTIVE"
    assert consent.sub_status is None
    assert consent.activated_at == "2024-10-28T11:52:08.903863Z"


def test_recurring_consent_to_service(t_recurring_consent):
    service_json_data = t_recurring_consent.to_service()
    assert "consent_id" not in service_json_data
    assert "consentId" not in service_json_data
    assert service_json_data["payer"] == {"alias": "46701234567"}
    assert service_json_data["payee"] == {"alias": "1234679304"}
    assert service_json_data["callbackUrl"] == "https://example.com/recurring/callback"
    assert service_json_data["payeePaymentReference"] == "order-123"


def test_recurring_consent_to_service_with_payer_tin(t_recurring_consent):
    t_recurring_consent.payer_alias = None
    t_recurring_consent.payer_tin = "198810236383"

    service_json_data = t_recurring_consent.to_service()

    assert service_json_data["tin"] == "198810236383"
    assert "payer" not in service_json_data
    assert "payerTin" not in service_json_data


def test_recurring_payment_from_service(t_recurring_payment_response):
    payment = RecurringPayment.from_service(t_recurring_payment_response)
    assert payment.payment_id == "payment-id"
    assert payment.status == "PAID"
    assert payment.status_at == "2024-10-28T11:52:08.903863Z"


def test_recurring_payment_from_service_with_nested_details(t_recurring_payment_response):
    response = {
        **t_recurring_payment_response,
        "payer": {"alias": "46701234567"},
        "payee": {"alias": "1234679304"},
        "amount": {"value": 20.0, "currency": "SEK"},
    }

    payment = RecurringPayment.from_service(response)

    assert payment.payment_id == "payment-id"
    assert payment.payer_alias == "46701234567"
    assert payment.payee_alias == "1234679304"
    assert payment.amount == 20.0
    assert payment.currency == "SEK"


def test_recurring_payment_to_service(t_recurring_payment):
    service_json_data = t_recurring_payment.to_service()
    assert "payment_id" not in service_json_data
    assert "paymentId" not in service_json_data
    assert service_json_data["payee"] == {"alias": "1234679304"}
    assert service_json_data["amount"] == {"value": 20.0, "currency": "SEK"}
    assert service_json_data["consentId"] == "consent-id"


def test_recurring_payment_to_service_with_payer(t_recurring_payment):
    t_recurring_payment.payer_alias = "46701234567"

    service_json_data = t_recurring_payment.to_service()

    assert service_json_data["payer"] == {"alias": "46701234567"}
    assert service_json_data["payee"] == {"alias": "1234679304"}
    assert service_json_data["amount"] == {"value": 20.0, "currency": "SEK"}
    assert "payerAlias" not in service_json_data


def test_recurring_availability_from_service(t_recurring_availability_response):
    availability = RecurringAvailability.from_service(t_recurring_availability_response)
    assert availability.recurring_is_offered is True
