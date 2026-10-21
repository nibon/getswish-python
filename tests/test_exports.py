import getswish


def test_public_exports():
    expected = {
        "Certificate", "Certificates", "Environment", "Payment", "Payout", "ProductionEnvironment",
        "RecurringAvailability", "RecurringConsent", "RecurringPayment", "Refund", "SwishClient",
        "SwishError", "TestEnvironment", "__version__",
    }
    assert set(getswish.__all__) == expected
    namespace = {}
    exec("from getswish import *", namespace)
    assert namespace.keys() - {"__builtins__"} == expected
    for name in expected:
        assert namespace[name] is getattr(getswish, name)


def test_metadata_helper_is_private():
    assert not hasattr(getswish, "version")
