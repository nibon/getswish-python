from datetime import datetime, timezone
from pathlib import Path
import ssl

from cryptography import x509
from cryptography.hazmat.primitives.serialization import load_pem_private_key
import pytest
import rsa

import getswish


def test_default_certificates_are_package_resources():
    certificates = getswish.SwishClient().certificates
    directory = Path(getswish.__file__).resolve().parent / "certificates" / "mss_test_3.0"
    paths = [
        certificates.communication.public,
        certificates.communication.private_key,
        certificates.verify.public,
        certificates.signing.public,
        certificates.signing.private_key,
    ]
    for path in paths:
        assert Path(path).parent == directory
        assert Path(path).is_file()


@pytest.mark.parametrize("name", ["communication", "verify", "signing"])
def test_default_certificates_are_valid(name):
    certificate = getattr(getswish.SwishClient().certificates, name)
    parsed = x509.load_pem_x509_certificate(Path(certificate.public).read_bytes())
    assert parsed.not_valid_before_utc <= datetime.now(timezone.utc) < parsed.not_valid_after_utc


@pytest.mark.parametrize("name", ["communication", "signing"])
def test_default_certificate_keys_match(name):
    certificate = getattr(getswish.SwishClient().certificates, name)
    parsed = x509.load_pem_x509_certificate(Path(certificate.public).read_bytes())
    key = load_pem_private_key(Path(certificate.private_key).read_bytes(), password=None)
    assert key.public_key().public_numbers() == parsed.public_key().public_numbers()


def test_default_signing_serial_and_key():
    certificate = getswish.SwishClient().certificates.signing
    parsed = x509.load_pem_x509_certificate(Path(certificate.public).read_bytes())
    assert certificate.public_serial == format(parsed.serial_number, "X")
    key = rsa.PrivateKey.load_pkcs1(Path(certificate.private_key).read_bytes())
    assert key.n == parsed.public_key().public_numbers().n


def test_default_certificates_load_in_tls_context():
    certificates = getswish.SwishClient().certificates
    context = ssl.create_default_context(cafile=certificates.verify.public)
    context.load_cert_chain(certificates.communication.public, certificates.communication.private_key)
