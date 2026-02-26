"""Tests for zephyr_mcp.zephyr.constants module."""

from zephyr_mcp.zephyr.constants import (
    DEFAULT_TEST_CASE_FIELDS,
    TEST_CASE_PRIORITIES,
    TEST_CASE_STATUSES,
    TEST_EXECUTION_STATUSES,
)


class TestConstants:
    def test_default_test_case_fields(self):
        assert isinstance(DEFAULT_TEST_CASE_FIELDS, list)
        assert "key" in DEFAULT_TEST_CASE_FIELDS
        assert "name" in DEFAULT_TEST_CASE_FIELDS
        assert "status" in DEFAULT_TEST_CASE_FIELDS

    def test_execution_statuses(self):
        assert isinstance(TEST_EXECUTION_STATUSES, list)
        assert "Pass" in TEST_EXECUTION_STATUSES
        assert "Fail" in TEST_EXECUTION_STATUSES
        assert "Blocked" in TEST_EXECUTION_STATUSES
        assert "Not Executed" in TEST_EXECUTION_STATUSES
        assert "In Progress" in TEST_EXECUTION_STATUSES

    def test_case_priorities(self):
        assert isinstance(TEST_CASE_PRIORITIES, list)
        assert "High" in TEST_CASE_PRIORITIES
        assert "Normal" in TEST_CASE_PRIORITIES
        assert "Low" in TEST_CASE_PRIORITIES

    def test_case_statuses(self):
        assert isinstance(TEST_CASE_STATUSES, list)
        assert "Approved" in TEST_CASE_STATUSES
        assert "Draft" in TEST_CASE_STATUSES
        assert "Deprecated" in TEST_CASE_STATUSES
