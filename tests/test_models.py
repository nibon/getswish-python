from getswish import Payment, Payout, Refund
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
