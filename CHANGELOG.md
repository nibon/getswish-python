# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.4.0] - 2026-10-20

### Added

- Added Python 3.14 and stable Python 3.15 to the required CI test matrix and package classifiers,
  retaining Python 3.10 support.
- Added a development lockfile and source-only ty checking.
- Included a `py.typed` marker for downstream type checking.
- Declared public package exports with `__all__` and made the version metadata helper private.
- Added configurable client HTTP timeouts, defaulting to 10 seconds to connect and 30 seconds to read.
  Set `timeout=None` to restore unlimited waiting; timeout exceptions retain their Requests types.
- Added experimental Recurring Payments API: `create_recurring_ecommerce_consent`, `create_recurring_mcommerce_consent`,
  `update_recurring_consent_callback_url`, `retrieve_recurring_consent`, `delete_recurring_consent`,
  `create_recurring_payment`, `retrieve_recurring_payment`, `check_recurring_tin_availability`,
  `check_recurring_alias_availability`.
- Added experimental QR Code API: `create_prefilled_qr_code`, `create_commerce_qr_code`.
- Added `RecurringConsent`, `RecurringPayment`, `RecurringAvailability` model classes.
- Added `SwishError.raw_errors` and `SwishError.trace_id` attributes; `SwishError` now accepts
  `list[dict] | dict | str` inputs.
- Added `recurring_base` and `qr_base` fields to `Environment`.
- Added `_recurring_url` and `_qr_url` URL helpers to `SwishClient`.
- Added `on_behalf_of` (partner header) support to recurring methods.
- Added CI workflow gates: Ruff lint, ty type checking, package build, Twine validation, and isolated
  installed-certificate checks for wheel and source distributions.
- Added Python 3.10-3.13 classifiers to `pyproject.toml`.

### Changed

- Migrated maintainer setup, checks, builds, version bumps, and publishing to native uv commands and the
  `uv_build` backend, replacing Make, Nox, Flit, and the custom version-bumping script.
- Moved the package version to `pyproject.toml`; `getswish.__version__` reads installed package metadata.
  Release bumps update project metadata and lockfile without automatically committing or tagging.
- Incomplete environment/certificates configuration and missing required request or payout certificates now raise
  `ValueError` instead of incidental `AttributeError` or `AssertionError`.
- All HTTP 4xx/5xx responses now raise `SwishError`, including empty bodies and statuses previously raised as
  `requests.HTTPError`. JSON and text error details are preserved; empty errors fall back to the HTTP status.
- `SwishError` now inherits from `requests.HTTPError` and exposes the original `response` and its `request`.
  Existing `HTTPError` and `RequestException` handlers now also catch `SwishError`; put specific `SwishError`
  handlers first. Network, timeout, and TLS exceptions remain unchanged.
- Existing `SwishError` handlers now also receive authentication, rate-limit, and server errors, not just
  payment rejections. Inspect `response.status_code` to distinguish them.
- Moved CI coverage, lint, and package checks to Python 3.15 and aligned Ruff's target with the Python 3.10 minimum.
- Marked Recurring and QR APIs experimental in 0.4.0; contract validation and stabilization are deferred to 0.5.0.
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
- Updated type hints to use `str | None` union syntax throughout.
- Updated README development and release instructions to use uv and documented all commands.

Error-handling example (using an existing client and callback URL):

```python
import requests
import getswish

try:
    payment = swish_client.create_payment(100.00, callback_url)
except getswish.SwishError as error:
    print(error.response.status_code, error.errors, error.trace_id)
except requests.RequestException as error:
    print("Request failed:", error)
```

### Fixed

- Fixed custom payment payee aliases, UTC payout instruction timestamps, and shared mutable default client configuration.
- Preserved empty JSON/text values in `SwishError.raw_errors` and safely normalized unexpected error fields to strings.
- Replaced expired MSS 2.0 test credentials with MSS 3.0 credentials and included them in installed packages.
- Corrected the README Commerce QR example to use a fresh pending M-commerce payment token and repaired its code blocks.
- Corrected the README refund example to use the completed payment's reference and payer alias.
- Clarified that the custom certificate configuration examples use test credentials, not production credentials.

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
