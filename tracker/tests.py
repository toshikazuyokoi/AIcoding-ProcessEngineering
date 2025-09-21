"""Minimal shim used during migration to preserve Django test discovery.

This file re-exports tests from the transitional package ``tracker.tests_pkg``
or falls back to the legacy consolidated module ``tracker.tests_legacy``.

Remove this file when migration is complete.
"""

try:
    from tracker.tests_pkg.test_issue_api_comprehensive import *  # noqa: F401,F403
except Exception:
    from tracker.tests_legacy import *  # noqa: F401,F403

