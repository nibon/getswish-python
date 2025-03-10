# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
