"""Tests for boss_admin/templatetags/filters.py."""
import pytest

from boss_admin.templatetags.filters import my_filter


class TestMyFilter:
    def test_splits_on_underscore(self):
        assert my_filter("a_b_c") == ["a", "b", "c"]

    def test_no_underscore_returns_single_element(self):
        assert my_filter("abc") == ["abc"]

    def test_empty_string(self):
        assert my_filter("") == [""]

    def test_handles_integer_input(self):
        assert my_filter(123) == ["123"]

    def test_handles_none(self):
        assert my_filter(None) == ["None"]

    def test_trailing_underscore(self):
        assert my_filter("a_") == ["a", ""]
