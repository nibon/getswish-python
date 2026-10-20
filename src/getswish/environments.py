from dataclasses import dataclass, field
from pathlib import Path

cert_base = Path(__file__).resolve().parent / "certificates" / "mss_test_3.0"


@dataclass
class Certificate:
    public: str | None = None
    private_key: str | None = None
    public_serial: str | None = None


@dataclass
class Certificates:
    communication: Certificate | None = field(repr=False)  # cert, private key
    verify: Certificate | None = field(repr=False)  # cert
    signing: Certificate | None = field(repr=False, default=None)  # cert, private key, serial


@dataclass
class Environment:
    name: str
    base: str
    recurring_base: str | None = None
    qr_base: str | None = None


TestEnvironment = Environment(
    name="test",
    base="https://mss.cpc.getswish.net/swish-cpcapi/api/",
    recurring_base="https://mss.cpc.getswish.net",
    qr_base="https://mpc.getswish.net/qrg-swish/api/",
)
ProductionEnvironment = Environment(
    name="production",
    base="https://cpc.getswish.net/swish-cpcapi/api/",
    recurring_base="https://cpc.getswish.net",
    qr_base="https://mpc.getswish.net/qrg-swish/api/",
)

TestCertificates = Certificates(
    Certificate(
        public=f"{cert_base}/Swish_Merchant_TestCertificate_1234679304.pem",
        private_key=f"{cert_base}/Swish_Merchant_TestCertificate_1234679304.key",
    ),
    Certificate(public=f"{cert_base}/Swish_TLS_RootCA.pem"),
    Certificate(
        public=f"{cert_base}/Swish_Merchant_TestSigningCertificate_1234679304.pem",
        private_key=f"{cert_base}/Swish_Merchant_TestSigningCertificate_1234679304.key",
        public_serial="4F24C03A0295A0B53596240EA8C0F430",
    ),
)
