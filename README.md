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

All requests default to a 10-second connect timeout and a 30-second read timeout.
Configure these with `getswish.SwishClient(timeout=(5.0, 60.0))`, use a single number for both,
or set `timeout=None` to disable timeouts. The read timeout limits waiting between received data,
not the total request duration. Timeouts raise Requests exceptions, not `SwishError`.
After a payment or payout timeout, check its status before retrying; the server may have accepted it.

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

## Error handling

All HTTP 4xx/5xx responses raise `getswish.SwishError`, including responses with empty bodies.
It inherits from `requests.HTTPError` (and `requests.RequestException`). Inspect `errors` for normalized error
messages, `raw_errors` for the unchanged parsed JSON or response text, `trace_id` when supplied, and
`response.status_code` to distinguish rejections, authentication failures, rate limits, and server errors.
Unexpected error fields are converted to strings; empty errors use an HTTP status message without changing `raw_errors`.
Connection failures, timeouts, and TLS errors retain their Requests exception types.

```python
import requests
import getswish

try:
    payment = swish_client.create_payment(100.00, callback_url)
except getswish.SwishError as error:
    print(error.response.status_code, error.errors, error.trace_id)
except requests.RequestException as error:
    print("Request failed:", error)
```

## Development setup

Install [uv](https://docs.astral.sh/uv/getting-started/installation/) (CI uses uv 0.13.1), clone the repository,
and sync the locked development environment. uv installs the required Python if necessary.

    git clone https://github.com/nibon/getswish-python.git && cd getswish-python

    uv sync --locked

### Testing

Run all tests.

    uv run --locked pytest

Run one focused test.

    uv run --locked pytest tests/test_client.py::test_requests_create_payment

Run coverage the same way as CI.

    uv run --locked pytest --cov=src

Run the source lint check.

    uv run --locked ruff check src

Run the source-only type check (Python 3.10 is the minimum supported version).

    uv run --locked ty check src

Build and check the package.

    uv build
    uv run --locked twine check dist/getswish-*.whl dist/getswish-*.tar.gz

To test another interpreter locally, run `uv run --locked --python 3.10 pytest` (or 3.11-3.15).
CI runs the full six-version matrix; uv does not provide a single-command matrix runner.

The lockfile is for development; library consumers use the dependency ranges in `pyproject.toml`.

### Release workflow

Update the changelog, then bump the version with `uv version --bump patch` (or `minor` or `major`).
uv normally updates `pyproject.toml` and `uv.lock` and syncs the environment; it does not commit or tag.
Review the diff and commit the version, lockfile, and changelog with ordinary Git commands. To keep unrelated
staged changes out of the release commit, specify paths with `git commit --only -- pyproject.toml uv.lock CHANGELOG.md`.
CI runs the full matrix, coverage, lint, types, build, distribution validation, and installed-resource checks.

    uv build
    uv run --locked twine check dist/getswish-*.whl dist/getswish-*.tar.gz

Review the changes and wait for CI. `uv publish` uploads existing artifacts; it does not build them.
Select only the artifacts for the current version, not all files under `dist/`. For example, for version 0.4.0:

    uv publish --index testpypi dist/getswish-0.4.0-py3-none-any.whl dist/getswish-0.4.0.tar.gz
    uv publish dist/getswish-0.4.0-py3-none-any.whl dist/getswish-0.4.0.tar.gz

Set `UV_PUBLISH_TOKEN` to the appropriate API token for each destination (TestPyPI and PyPI use different tokens).
The `testpypi` publish index is configured in `pyproject.toml`. Never reuse a TestPyPI token on PyPI.
