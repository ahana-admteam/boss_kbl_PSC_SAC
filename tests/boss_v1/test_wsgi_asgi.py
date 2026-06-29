"""Tests for boss_v1 WSGI / ASGI entrypoints."""


class TestWSGI:
    def test_application_exists(self):
        from boss_v1 import wsgi

        assert hasattr(wsgi, "application")


class TestASGI:
    def test_application_exists(self):
        from boss_v1 import asgi

        assert hasattr(asgi, "application")
