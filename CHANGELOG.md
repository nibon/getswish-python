# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed

- Corrected the README Commerce QR example to use a fresh pending M-commerce payment token and repaired its code blocks.
- Corrected the README refund example to use the completed payment's reference and payer alias.
- Clarified that the custom certificate configuration examples use test credentials, not production credentials.

## [0.4.0] - 2026-05-31

### Added

- Added Recurring Payments API: `create_recurring_ecommerce_consent`, `create_recurring_mcommerce_consent`,
  `update_recurring_consent_callback_url`, `retrieve_recurring_consent`, `delete_recurring_consent`,
  `create_recurring_payment`, `retrieve_recurring_payment`, `check_recurring_tin_availability`,
  `check_recurring_alias_availability`.
- Added QR Code API: `create_prefilled_qr_code`, `create_commerce_qr_code`.
- Added `RecurringConsent`, `RecurringPayment`, `RecurringAvailability` model classes.
- Added `SwishError.raw_errors` and `SwishError.trace_id` attributes; `SwishError` now accepts
  `list[dict] | dict | str` inputs.
- Added `recurring_base` and `qr_base` fields to `Environment`.
- Added `_recurring_url` and `_qr_url` URL helpers to `SwishClient`.
- Added `on_behalf_of` (partner header) support to recurring methods.
- Added Python 3.14 to nox and CI matrix.
- Added CI workflow gates: ruff lint, package build, and twine check.
- Added Python 3.10–3.14 classifiers to `pyproject.toml`.

### Changed

- Recurring endpoints corrected to match Swish documentation: id-bearing PUT/POST paths,
  `PUT .../callback` for callback updates, `POST` with request body for availability checks,
  `/payments/single/{paymentId}/status` for payment retrieval.
- QR prefilled payload now uses nested `{"value": ..., "editable": bool}` objects for
  `payee`, `amount`, and `message` fields per Swish QR API spec.
- `RecurringConsent` model updated: `consent_id` replaces `id`; `sub_status`, `activated_at`,
  `payer_tin` fields added; nested payer/payee objects handled in `to_service`/`from_service`.
- `RecurringPayment` model updated: `payment_id` replaces `id`; `sub_status`, `status_at` fields
  added; nested payer/payee and amount objects handled in `to_service`/`from_service`.
- `RecurringAvailability` simplified to `recurring_is_offered` field matching service response.
- `_requests` now raises `SwishError` on 400 and 415 status codes (in addition to 422) when the
  response body contains error details.
- Updated type hints to use `str | None` union syntax throughout.
- Updated README development setup to use `pip install -e .[tests]` and documented all commands.

## [0.3.0] - 2025-03-10

### Added

- Added the now documented field callbackIdentifier to Payment and Refund objects.
- Added python 3.13 to the nox file and GitHub actions.

### Changed

- Updated all certificate references from `mss_test_1.9` to `mss_test_2.0` in `README.md` and `TestEnvironment`.
- Changed `utcnow` to `now` with timezone information in the `create_payout` method.
- Updated ruff settings in `pyproject.toml`.
- Updated documentation and added example.

## [0.2.4] - 2023-06-09

### Added

- Added the undocumented Payout field callbackIdentifier that is
  included when retrieving payout updates and only in production environment.

## [0.2.3] - 2023-06-02

### Added

- Added logging.
- Added nox as optional dependency.

### Changed

- Updated documentation.
- Updated tests for coverage.

## [0.2.2] - 2023-04-13

### Changed

- Updated production environment default url.
- Updated default test environment parameters.
- Corrected project source url in pyproject.toml.

## [0.2.0] - 2023-04-12

###  Added

- Added nox.

### Changed

- Updated documentation, build and testing.

## [0.1.3] - 2023-02-14

### Changed

- Updated build, CHANGELOG.md and README.md.

## [0.1.2] - 2022-10-17

- Added test cases.

## [0.1.1] - 2022-09-14

### Added

- Initial version
