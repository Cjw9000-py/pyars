# Release Notes

## v1.0 - 2025-02-15
- Reworked argument system into dedicated `pyars.argument` subpackage with separate classes for positional, option, flag, and command descriptors.
- Updated container orchestration to support the new API, including default conversion, collection handling, and stricter command validation.
- Refreshed documentation, examples, and tests to reflect the new usage pattern defined in `new-spec.py`.
- Added `new-spec.py` as the canonical usage reference for the v1.0 interface and ensured the test suite passes against the redesigned API.
