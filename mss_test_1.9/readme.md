# Merchant Swish Simulator #

This directory (zip-file) contains a *User Guide* on how to use the
*Merchant Swish Simulator (MSS)* together with the test
*authentication* certificates that are needed in order to properly
communicate with the server.

For payout requests a specific *Swish_Merchant_TestSigningCertificate*
is provided that **must** be used to sign the payout request payload
(create the signature property value). No other signing certificate
will be accepted by MSS but result in error message returned to
caller.

# List of provided files #

.
├── Getswish_Test_Certificates
│   ├── old_certs
│   │   ├── readme.md
│   │   ├── Swish_Merchant_TestCertificate_1234679304.key
│   │   ├── Swish_Merchant_TestCertificate_1234679304.p12
│   │   └── Swish_Merchant_TestCertificate_1234679304.pem
│   ├── Swish_Merchant_TestCertificate_1234679304.key
│   ├── Swish_Merchant_TestCertificate_1234679304.p12
│   ├── Swish_Merchant_TestCertificate_1234679304.pem
│   ├── Swish_Merchant_TestSigningCertificate_1234679304.key
│   ├── Swish_Merchant_TestSigningCertificate_1234679304.p12
│   ├── Swish_Merchant_TestSigningCertificate_1234679304.pem
│   ├── Swish_TechnicalSupplier_TestCertificate_9871065216.key
│   ├── Swish_TechnicalSupplier_TestCertificate_9871065216.p12
│   ├── Swish_TechnicalSupplier_TestCertificate_9871065216.pem
│   └── Swish_TLS_RootCA.pem
├── MSS_UserGuide_v1.9.pdf
└── readme.md

2 directories, 16 files


# Certificate expire dates #

`
./Getswish_Test_Certificates$ openssl x509 -startdate -enddate -serial -noout -in Swish_Merchant_TestCertificate_1234679304.pem 
notBefore=May 13 07:43:13 2020 GMT
notAfter=May 13 07:43:13 2022 GMT
serial=0BF3A59588F654C767835FC95A53610F

./Getswish_Test_Certificates$ openssl x509 -startdate -enddate -serial -noout -in Swish_Merchant_TestSigningCertificate_1234679304.pem 
notBefore=Sep 23 12:00:20 2019 GMT
notAfter=Sep 23 12:00:20 2021 GMT
serial=7D70445EC8EF4D1E3A713427E973D097

./Getswish_Test_Certificates$ openssl x509 -startdate -enddate -serial -noout -in Swish_TechnicalSupplier_TestCertificate_9871065216.pem 
notBefore=Oct 19 13:28:42 2018 GMT
notAfter=Oct 19 13:28:42 2020 GMT
serial=21E0B224ADC487718F485230A2F5C76D

./Getswish_Test_Certificates$ openssl x509 -startdate -enddate -serial -noout -in Swish_TLS_RootCA.pem 
notBefore=Nov 10 00:00:00 2006 GMT
notAfter=Nov 10 00:00:00 2031 GMT
serial=083BE056904246B1A1756AC95991C74A

`
