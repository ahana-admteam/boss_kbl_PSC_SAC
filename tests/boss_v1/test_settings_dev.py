"""Tests for boss_v1/settings/dev.py."""


class TestDevSettings:
    def test_debug_true(self):
        from boss_v1.settings import dev

        assert dev.DEBUG is True

    def test_ad_login_false(self):
        from boss_v1.settings import dev

        assert dev.AD_LOGIN is False

    def test_allowed_hosts_includes_tenants(self):
        from boss_v1.settings import dev

        for h in (
            "kotak.localhost",
            "localhost",
            "fincare.localhost",
            "hdfc.localhost",
            "jana.localhost",
            "rbl.localhost",
            "demo.localhost",
            "ujjivan.localhost",
            "svc.localhost",
        ):
            assert h in dev.ALLOWED_HOSTS

    def test_databases_has_sqlite_default(self):
        from boss_v1.settings import dev

        assert (
            dev.DATABASES["default"]["ENGINE"]
            == "django.db.backends.sqlite3"
        )

    def test_all_tenants_have_db_entry(self):
        from boss_v1.settings import dev

        for tenant in (
            "default",
            "kotak",
            "jana",
            "fincare",
            "hdfc",
            "rbl",
            "demo",
            "ujjivan",
            "svc",
        ):
            assert tenant in dev.DATABASES
