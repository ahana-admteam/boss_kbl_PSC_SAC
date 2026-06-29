"""Tests for the PSC app apps.py and urls.py."""


class TestAppsConfig:
    def test_app_name(self):
        from preliminaryscreeningcommittee_review.apps import (
            PreliminaryscreeningcommitteeReviewConfig,
        )

        assert (
            PreliminaryscreeningcommitteeReviewConfig.name
            == "preliminaryscreeningcommittee_review"
        )


class TestUrls:
    def test_urls_file_declares_expected_routes(self):
        """The full module import resolves `settings.base.MEDIA_URL` which
        fails under the test settings package (no `base` submodule attr).
        So we read the URL conf source instead."""
        import os

        path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "..",
            "preliminaryscreeningcommittee_review",
            "urls.py",
        )
        with open(path) as f:
            src = f.read()
        for name in (
            "dashboard",
            "psc_review",
            "sac_review",
            "psc_update",
            "sac_update",
            "mom_dashboard",
            "mom_generate",
            "mom_lapses",
            "mom_review",
            "account_dashboard",
        ):
            assert f"name='{name}'" in src or f'name="{name}"' in src
