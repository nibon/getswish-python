"""Getswish python client library"""

from importlib.metadata import version as _version

from .client import SwishClient
from .environments import Certificate, Certificates, Environment, ProductionEnvironment, TestEnvironment
from .exceptions import SwishError
from .models import Payment, Payout, RecurringAvailability, RecurringConsent, RecurringPayment, Refund

__all__ = [
    "Certificate",
    "Certificates",
    "Environment",
    "Payment",
    "Payout",
    "ProductionEnvironment",
    "RecurringAvailability",
    "RecurringConsent",
    "RecurringPayment",
    "Refund",
    "SwishClient",
    "SwishError",
    "TestEnvironment",
    "__version__",
]

__version__ = _version("getswish")
