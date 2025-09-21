# Changelog

## Unreleased

### Changed
- test(migrate): modularized Issue API tests into `tracker/tests/test_issue_api_comprehensive.py` and added a migration snapshot and shim (Phase 1). Verified 21 tests passing for the Issue API suite.

### Notes
- Full `python manage.py test` currently triggers a discovery ImportError due to the `tracker/tests` package vs `tracker/tests.py` collision; this is intentional during phased migration. See `test-suite-phased-migration-plan.md` Phase 1 notes for mitigation options.
