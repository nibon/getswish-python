# Swish - Python client

Client library to integrate with the swish commerce and payout api.

## Supported APIs

* https://developer.swish.nu/documentation/getting-started/swish-commerce-api
* https://developer.swish.nu/documentation/getting-started/swish-payout-api

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

The example code uses the test environment and certificates in this library.

```python
import getswish

swish_client = getswish.SwishClient()

callback_url = "https://example.com/callback/"

### Example - Commerce API

# Perform a payment request - E-commerce.
payment_e = swish_client.create_payment(
    100.00, callback_url, message="Product name."
)

# Perform a payment request - M-commerce.
payment_m = swish_client.create_payment(
    100.00, callback_url, "46701234567", message="Product name."
)

# Retrieve info about the payment
payment_retrieved = swish_client.retrieve_payment(payment_m.id)

# Cancel the payment
payment_cancelled = swish_client.cancel_payment(payment_m.id)

# Refund payment the whole amount to the previous payer which now is the payee.
payment_refund = swish_client.create_refund(
    payment_e.id, callback_url, payment_e.payer_alias, payment_e.amount
)

### Example - Payout API

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

## Example - Production Client

In production the environment must be set
to `swish.ProductionEnvironment` and all path must be modified to the production certificates that you have generated
through your bank and swish company portals. The example below is the default configuration for the test certificates
and environment. Replace all paths and files with your generated production instances.

```python
from pathlib import Path
import getswish

cert_base = Path(__file__).parent.parent.parent.resolve()
cert_base = cert_base / "mss_test_2.0" / "Getswish_Test_Certificates"

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

## Example - Production Client with payout

Using the payout API require an additional certificate from your bank and called a signing certificate.

```python
from pathlib import Path
import getswish

cert_base = Path(__file__).parent.parent.parent.resolve()
cert_base = cert_base / "mss_test_2.0" / "Getswish_Test_Certificates"

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
            public_serial="51FFA3C2336C8D5B4904D53CD9FAB21D",
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
    python3 -m pip install flit
    flit install --only-deps

### Testing installing package and pytest

Symlink getswish and run pytest. You might want to uninstall the getswish library depending on your workflow.

    flit install --symlink
    pytest

### Testing using nox

Isolated testing on configured python versions and running a coverage test.

    nox
