from pathlib import Path

import pytest

import getswish


@pytest.fixture
def t_service_error():
    return [{"errorCode": "foo", "errorMessage": "bar"}]


@pytest.fixture
def callback_url() -> str:
    return "https://example.com/callback"


@pytest.fixture
def client_default() -> getswish.SwishClient:
    return getswish.SwishClient()


@pytest.fixture
def client() -> getswish.SwishClient:
    cert_base = Path(__file__).parent.parent.resolve() / "mss_test_1.9" / "Getswish_Test_Certificates"
    return getswish.SwishClient(
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


@pytest.fixture
def t_payment():
    from getswish import Payment

    return Payment(
        id="7B4DBF32F6C04943B67DB374A9031151",
        callback_url="https://example.com/callback",
        payee_alias="1234679304",
        amount=20,
        currency="SEK",
        location="https://mss.cpc.getswish.net/swish-cpcapi/api/v1/paymentrequests/7B4DBF32F6C04943B67DB374A9031151",
        payment_request_token="2b25565bd2fb4535bb636208a50ea3c6",
    )


@pytest.fixture
def t_payment_created_headers():
    return {"Location": "https://payment/path/", "PaymentRequestToken": "payment_token"}


@pytest.fixture
def t_payment_response():
    return {
        "id": "7B4DBF32F6C04943B67DB374A9031151",
        "payeePaymentReference": None,
        "paymentReference": "B4E19D1107AF477494E2B464CFE26530",
        "callbackUrl": "https://example.com/callback",
        "payerAlias": "46464646464",
        "payeeAlias": "1234679304",
        "amount": 20.0,
        "currency": "SEK",
        "message": "",
        "status": "CREATED",
        "dateCreated": "2022-09-14T10:38:06.780Z",
        "datePaid": None,
        "errorCode": None,
        "errorMessage": None,
    }


@pytest.fixture
def t_refund():
    from getswish import Refund

    return Refund(
        id="C26944D5FFC645C3B9BABBA5F96F45CC",
        callback_url="https://example.com/callback",
        payee_alias="46731234567",
        amount=20.0,
        currency="SEK",
        payer_alias="1234679304",
        payment_reference="3013E58CE1474EDC94D273B41101FCD9",
        status="DEBITED",
        date_created="2022-09-14T10:38:16.341Z",
        original_payment_reference="53C2253D45A04B33A8330063B2FE5D2F",
        payer_payment_reference="",
    )


@pytest.fixture
def t_refund_response():
    return {
        "id": "C26944D5FFC645C3B9BABBA5F96F45CC",
        "paymentReference": "3013E58CE1474EDC94D273B41101FCD9",
        "payerPaymentReference": "",
        "originalPaymentReference": "53C2253D45A04B33A8330063B2FE5D2F",
        "callbackUrl": "https://example.com/callback",
        "payerAlias": "1234679304",
        "payeeAlias": "46739123456",
        "amount": 20.0,
        "currency": "SEK",
        "message": None,
        "status": "DEBITED",
        "dateCreated": "2022-09-14T10:38:16.341Z",
        "datePaid": None,
        "errorMessage": None,
        "additionalInformation": None,
        "errorCode": None,
    }


@pytest.fixture
def t_refund_created_headers():
    return {"Location": "https://refund/path/"}


@pytest.fixture
def t_payout():
    from getswish import Payout

    return Payout(
        payout_instruction_uuid="A9CC06E74D894FA4AD26059A1F3AAA78",
        payer_payment_reference="myRef2893",
        payment_reference="DC94DC82C2FB4D0794511B0F8E435F51",
        payer_alias="1234679304",
        payee_alias="46731234567",
        payee_ssn="198810236383",
        amount=20.0,
        currency="SEK",
        payout_type="PAYOUT",
        callback_url="https://example.com/callback/",
        status="PAID",
        date_created="2022-09-14T10:38:26.763Z",
        date_paid="2022-09-14T10:38:30.764Z",
    )


@pytest.fixture
def t_payout_response():
    return {
        "paymentReference": "DC94DC82C2FB4D0794511B0F8E435F51",
        "payoutInstructionUUID": "A9CC06E74D894FA4AD26059A1F3AAA78",
        "payerPaymentReference": "myRef2893",
        "callbackUrl": "https://example.com/callback/",
        "payerAlias": "1234679304",
        "payeeAlias": "46731234567",
        "payeeSSN": "198810236383",
        "amount": 20.0,
        "currency": "SEK",
        "message": None,
        "payoutType": "PAYOUT",
        "status": "PAID",
        "dateCreated": "2022-09-14T10:38:26.763Z",
        "datePaid": "2022-09-14T10:38:30.764Z",
        "errorMessage": None,
        "additionalInformation": None,
        "errorCode": None,
    }


@pytest.fixture
def t_payout_created_headers():
    return {"Location": "https://payout/path/"}
