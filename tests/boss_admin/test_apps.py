"""Tests for boss_admin/apps.py."""


class TestBossAdminConfig:
    def test_name(self):
        from boss_admin.apps import JcradminappConfig

        assert JcradminappConfig.name == "boss_admin"
