"""Tests for boss_v1/settings/__init__.py — environment switching."""
import importlib
import sys


class TestSettingsInit:
    def test_local_env_loads_dev(self, monkeypatch):
        """When BOSS_ENV != 'prod', dev settings should be loaded."""
        # Reload the package to evaluate __init__.py with the patched flag
        if "boss_v1.settings" in sys.modules:
            del sys.modules["boss_v1.settings"]
        if "boss_v1.settings.dev" in sys.modules:
            # leave dev alone — we just need __init__ to evaluate
            pass
        mod = importlib.import_module("boss_v1.settings")
        assert mod.BOSS_ENV == "local"
        # dev.py defines DATABASES & ALLOWED_HOSTS
        assert hasattr(mod, "DATABASES")
        assert "default" in mod.DATABASES
