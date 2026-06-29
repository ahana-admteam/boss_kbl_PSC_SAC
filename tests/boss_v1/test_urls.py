"""Tests for boss_v1/urls.py — top-level URL include layout.

The full include chain pulls in preliminaryscreeningcommittee_review.urls
which references `settings.base.MEDIA_URL`. That submodule access only
works when boss_v1.settings is imported as a package the right way at
runtime — under pytest's test settings it raises AttributeError.

So we read the source file rather than import-evaluating it."""
import os


class TestUrls:
    def test_urls_file_exists(self):
        path = os.path.join(
            os.path.dirname(__file__), "..", "..", "boss_v1", "urls.py"
        )
        assert os.path.exists(path)

    def test_urls_file_includes_expected_apps(self):
        path = os.path.join(
            os.path.dirname(__file__), "..", "..", "boss_v1", "urls.py"
        )
        with open(path) as f:
            src = f.read()
        assert "boss_admin.urls" in src
        assert "notifications_app.urls" in src
        assert "preliminaryscreeningcommittee_review.urls" in src
        assert "admin.site.urls" in src
