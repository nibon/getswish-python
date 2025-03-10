# Merchant Swish Simulator #

This directory (zip-file) contains a *User Guide* on how to use the
*Merchant Swish Simulator (MSS)* together with the test
*authentication* certificates that are needed in order to properly
communicate with the server. 
Please also look at our updated documentation,
https://developer.swish.nu/
https://developer.swish.nu/api/mss/v1

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
notBefore=Tue, 28 Nov 2023 08:12:00 GMT
notAfter=Thu, 28 Nov 2025 08:12:00 GMT
serial=4512B3EBDA6E3CE6BFB14ABA6274A02C

./Getswish_Test_Certificates$ openssl x509 -startdate -enddate -serial -noout -in Swish_Merchant_TestSigningCertificate_1234679304.pem 
notBefore=Tue, 28 Nov 2023 08:13:00 GMT
notAfter=Thu, 28 Nov 2025 08:13:00 GMT
serial=5E24D8820F5B62C7E5CAC75D20D6E754

./Getswish_Test_Certificates$ openssl x509 -startdate -enddate -serial -noout -in Swish_TechnicalSupplier_TestCertificate_9871065216.pem 
notBefore=Tue, 28 Nov 2023 08:14:00 GMT
notAfter=Thu, 28 Nov 2025 08:14:00 GMT
serial=4DD744CB6C6C9363D16432012F0B4439

./Getswish_Test_Certificates$ openssl x509 -startdate -enddate -serial -noout -in Swish_TLS_RootCA.pem 
notBefore=Fri, 10 2006 00:00:00 GMT
notAfter=Mon, 10 2031 00:00:00 GMT
serial=083BE056904246B1A1756AC95991C74A