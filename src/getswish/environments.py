from dataclasses import dataclass, field


@dataclass
class Certificate:
    public: str = None
    private_key: str = None
    public_serial: str = None


@dataclass
class Certificates:
    communication: Certificate | None = field(repr=False)  # cert, private key
    verify: Certificate | None = field(repr=False)  # cert
    signing: Certificate | None = field(repr=False)  # cert, private key, serial


@dataclass
class Environment:
    name: str
    base: str


TestEnvironment = Environment(name="test", base="https://mss.cpc.getswish.net/swish-cpcapi/api/")
ProductionEnvironment = Environment(name="production", base="https://cpc.getswish.net/swish-cpcapi/")
