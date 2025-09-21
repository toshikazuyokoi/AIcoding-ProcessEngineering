"""Shim to include legacy monolithic tests in discovery.

Temporarily imports everything from tests_legacy so Django discovers them
after removing the original tests.py module that shadowed the tests package.

Migration Note: This is an intermediate compatibility layer.
"""

from tracker.tests_legacy import *  # noqa: F401,F403
