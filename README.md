# Swish - Python client

Client library to integrate with the swish commerce and payout api.

## Supported APIs

* https://developer.swish.nu/documentation/getting-started/swish-commerce-api
* https://developer.swish.nu/documentation/getting-started/swish-payout-api
* https://developer.swish.nu/documentation/getting-started/swish-recurring-payments-api (experimental)
* https://developer.swish.nu/documentation/getting-started/swish-qr-code (experimental)

Recurring and QR support is experimental in 0.4.0. Contract validation and stabilization are deferred to 0.5.0;
these interfaces may change. Commerce and Payout are not experimental.

## Installation

    pip install getswish

## Prerequisites

Swish api integration require communication certificates and keys to integrate with the commerce api and additional
signing certificates and keys for signing payout in the payout api. The client setup require that all the certificates
are available through file paths which are given on client setup. The communication certificates are create through your
bank portal after the appropriate agreements are signed and signing certificates are set up after additional payout
agreements are signed, trough https://portal.swish.nu/.

The signing certificate, private key and serial is only required when using the payout API.

## Example - Test Client

The example uses the public MSS 3.0 test credentials bundled with the installed library, valid until September 11, 2027.
Do not use these credentials in production. Source: the [MSS 3.0 bundle](https://assets.ctfassets.net/4dca8u8ebqnn/4CgQJUfc6ncjKHooAkqvDx/d27012ce097a5b0f6b151a8ccdfe285d/MSS_test_3.0.zip)
from [Swish test environments](https://developer.swish.nu/documentation/environments).

```python
import getswish

swish_client = getswish.SwishClient()

callback_url = "https://example.com/callback/"
```

### Example - Commerce API

```python
# Perform a payment request - M-commerce.
payment_m = swish_client.create_payment(
    100.00, callback_url, message="Product name."
)

# Perform a payment request - E-commerce.
payment_e = swish_client.create_payment(
    100.00, callback_url, "46701234567", message="Product name."
)

# Retrieve info about the payment
payment_retrieved = swish_client.retrieve_payment(payment_e.id)

# Cancel the payment
payment_cancelled = swish_client.cancel_payment(payment_e.id)

# After the callback confirms payment_m is PAID, retrieve its payment reference and payer.
paid_payment = swish_client.retrieve_payment(payment_m.id)

# Refund the whole amount to the previous payer, who is now the refund payee.
payment_refund = swish_client.create_refund(
    paid_payment.payment_reference, callback_url, paid_payment.payer_alias, paid_payment.amount
)

# Retrieve info about the refund
payment_refund_retrieved = swish_client.retrieve_refund(payment_refund.id)
```

### Example - Recurring Payments API (experimental)

Recurring payments allow a merchant to charge a customer on a consent basis. The customer signs
a consent once (via e-commerce or m-commerce flow), and the merchant can then initiate payments
against that consent without further customer interaction.

```python
# Check if the payer's bank supports recurring payments for their alias.
availability = swish_client.check_recurring_alias_availability("46701234567")
if not availability.recurring_is_offered:
    raise Exception("Recurring payments not available for this payer.")

# Create a recurring consent - E-commerce flow (payer alias known).
consent = swish_client.create_recurring_ecommerce_consent(
    callback_url, "46701234567", payee_payment_reference="subscription-001"
)

# Create a recurring consent - M-commerce flow (payer alias unknown; token shown to user).
consent_m = swish_client.create_recurring_mcommerce_consent(
    callback_url, payee_payment_reference="subscription-001"
)
# consent_m.payment_request_token -- show this to the payer in the Swish app.

# Retrieve consent info (e.g. after callback confirms ACTIVE status).
consent_active = swish_client.retrieve_recurring_consent(consent.consent_id)

# Charge the customer against the active consent.
payment = swish_client.create_recurring_payment(
    consent.consent_id, 100.00, callback_url, message="Monthly subscription."
)

# Check payment status.
payment_status = swish_client.retrieve_recurring_payment(payment.payment_id)

# Update the callback URL on an existing consent.
swish_client.update_recurring_consent_callback_url(consent.consent_id, "https://example.com/new-callback/")

# Delete (cancel) the consent.
swish_client.delete_recurring_consent(consent.consent_id)
```

### Example - QR Code API (experimental)

```python
# Generate a prefilled QR code (payee + amount pre-set, editable by payer).
qr_png = swish_client.create_prefilled_qr_code(
    "png",
    payee="1234679304",
    amount=100.00,
    amount_editable=True,
    message="Order #1234",
    size=300,
)
# qr_png is bytes -- write to a file or serve as an image response.

# Generate an SVG QR code.
qr_svg = swish_client.create_prefilled_qr_code("svg", payee="1234679304")
# qr_svg is a str containing the SVG markup.

# Create a fresh M-commerce request without a payer alias; use its token while pending.
qr_payment = swish_client.create_payment(100.00, callback_url, message="QR purchase.")

# Generate a QR code from this Commerce payment token, not a recurring consent token.
qr_commerce = swish_client.create_commerce_qr_code(
    qr_payment.payment_request_token, "png", size=300
)
```

### Example - Payout API

```python
# Generate a merchant specific reference.
# This reference could be order id or similar.
# Use generate_transaction_id for convenience.

from getswish.utils import generate_transaction_id

reference_id = generate_transaction_id()

# Perform a payment request
payout = swish_client.create_payout(
    reference_id, "46701234567", "197001019876", 10.00, callback_url, message="Test payout message."
)

# Retrieve info about the payout
payout_retrieved = swish_client.retrieve_payout(payout.payout_instruction_uuid)
```

## Example - Custom Test Client

This example explicitly uses `getswish.TestEnvironment` and the bundled test certificates. For production, use
`getswish.ProductionEnvironment`, your issued communication certificate and key, the appropriate TLS trust certificate,
and your merchant Swish number. Do not use the bundled test credentials in production.

```python
from pathlib import Path
import getswish

cert_base = Path(getswish.__file__).resolve().parent / "certificates" / "mss_test_3.0"

swish_client = getswish.SwishClient(
    environment=getswish.TestEnvironment,
    certificates=getswish.Certificates(
        communication=getswish.Certificate(
            public=f"{cert_base}/Swish_Merchant_TestCertificate_1234679304.pem",
            private_key=f"{cert_base}/Swish_Merchant_TestCertificate_1234679304.key",
        ),
        verify=getswish.Certificate(public=f"{cert_base}/Swish_TLS_RootCA.pem"),
    ),
    merchant_swish_number="1234679304",
)
```

## Example - Custom Test Client with Payout

This is also a test configuration. Payout additionally requires a signing certificate, private key, and serial number.
For production, use `getswish.ProductionEnvironment` and your issued communication and signing credentials instead of
these bundled test files.

```python
from pathlib import Path
import getswish

cert_base = Path(getswish.__file__).resolve().parent / "certificates" / "mss_test_3.0"

swish_client = getswish.SwishClient(
    environment=getswish.TestEnvironment,
    certificates=getswish.Certificates(
        communication=getswish.Certificate(
            public=f"{cert_base}/Swish_Merchant_TestCertificate_1234679304.pem",
            private_key=f"{cert_base}/Swish_Merchant_TestCertificate_1234679304.key",
        ),
        verify=getswish.Certificate(public=f"{cert_base}/Swish_TLS_RootCA.pem"),
        signing=getswish.Certificate(
            public=f"{cert_base}/Swish_Merchant_TestSigningCertificate_1234679304.pem",
            private_key=f"{cert_base}/Swish_Merchant_TestSigningCertificate_1234679304.key",
            public_serial="4F24C03A0295A0B53596240EA8C0F430",
        ),
    ),
    merchant_swish_number="1234679304",
)

callback_url = "https://example.com/callback/"
```

### Generating public_serial for signing certificate

The signing certificate `public_serial` is extracted from the certificate using this command on linux.

    openssl x509 -in Swish_Merchant_TestSigningCertificate_1234679304.pem -serial -noout

## Development setup

Clone the repository and set up a local virtual environment.

    git clone https://github.com/nibon/getswish-python.git && cd getswish-python

    python3 -m venv .venv
    source .venv/bin/activate
    python3 -m pip install -U pip
    python3 -m pip install -e .[tests]

### Testing

Run all tests.

    pytest

Run one focused test.

    pytest tests/test_client.py::test_requests_create_payment

Run coverage the same way as CI.

    pytest --cov=src

Run the source lint check.

    ruff check src

Build and check the package.

    python3 -m pip install build twine
    python3 -m build
    twine check dist/*

### Testing using nox

Isolated testing on configured python versions and running a coverage test.

    nox
