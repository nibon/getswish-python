from dataclasses import dataclass, field
from pathlib import Path

cert_base = Path(__file__).parent.parent.parent.resolve() / "mss_test_2.0" / "Getswish_Test_Certificates"


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
    recurring_base="https://mss.cpc.getswish.net/recurring/merchant/",
    qr_base="https://mpc.getswish.net/qrg-swish/api/",
)
ProductionEnvironment = Environment(
    name="production",
    base="https://cpc.getswish.net/swish-cpcapi/api/",
    recurring_base="https://cpc.getswish.net/recurring/merchant/",
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
        public_serial="5E24D8820F5B62C7E5CAC75D20D6E754",
    ),
)
