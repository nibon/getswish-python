# Merchant Swish Simulator #

This directory (zip-file) contains a *User Guide* on how to use the
*Merchant Swish Simulator (MSS)* together with the test
*authentication* certificates that are needed in order to properly
communicate with the server. 
Please also look at our updated documentation,
https://developer.swish.nu/
https://developer.swish.nu/api/mss/v1
[Swish_Merchant_TestSigningCertificate_1234679304.p12](Getswish_Test_Certificates%2FSwish_Merchant_TestSigningCertificate_1234679304.p12)
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
notBefore=Wed, 20 Jul 2022 14:49:34 GMT
notAfter=Sat, 20 Jul 2024 14:49:34 GMT
serial=4EF5C55AA5E475A3611087A4897F3F13

./Getswish_Test_Certificates$ openssl x509 -startdate -enddate -serial -noout -in Swish_Merchant_TestSigningCertificate_1234679304.pem 
notBefore=Wed, 20 Jul 2022 14:40:25 GMT
notAfter=Sat, 20 Jul 2024 14:40:25 GMT
serial=51FFA3C2336C8D5B4904D53CD9FAB21D

./Getswish_Test_Certificates$ openssl x509 -startdate -enddate -serial -noout -in Swish_TechnicalSupplier_TestCertificate_9871065216.pem 
notBefore=Tue, 09 Aug 2022 09:31:29 GMT
notAfter=Fri, 09 Aug 2024 09:31:29 GMT
serial=43180BE273556FF6970249395357B583

./Getswish_Test_Certificates$ openssl x509 -startdate -enddate -serial -noout -in Swish_TLS_RootCA.pem 
notBefore=Fri, 10 2006 00:00:00 GMT
notAfter=Mon, 10 2031 00:00:00 GMT
serial=083BE056904246B1A1756AC95991C74A

`

