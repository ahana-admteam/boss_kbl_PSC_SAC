"""Tests for preliminaryscreeningcommittee_review/views/account_views.py."""
from unittest.mock import patch

import pytest

from preliminaryscreeningcommittee_review.views import account_views


class TestAccountLog:
    def test_psc_renders(self, psc_session_req, psc_record):
        req = psc_session_req()
        with patch.object(account_views, "render", return_value="r") as rnd:
            res = account_views.account_log(req, "PSC", psc_record.psc_rec_id)
        assert res == "r"

    def test_sac_renders(self, psc_session_req, sac_record):
        req = psc_session_req()
        with patch.object(account_views, "render", return_value="r") as rnd:
            res = account_views.account_log(req, "SAC", sac_record.sac_rec_id)
        assert res == "r"

    def test_unknown_review_redirects(self, psc_session_req):
        req = psc_session_req()
        res = account_views.account_log(req, "PSC", "MISSING")
        assert res.status_code == 302


class TestAccountDashboard:
    def test_get_renders_dashboard(self, psc_session_req):
        req = psc_session_req()
        with patch.object(account_views, "render", return_value="r") as rnd:
            res = account_views.account_dashboard(req)
        assert res == "r"

    def test_post_delegates_to_account_log(
        self, psc_session_req, psc_record
    ):
        req = psc_session_req(
            method="post",
            data={"review_type": "PSC", "review_id": psc_record.psc_rec_id},
        )
        with patch.object(account_views, "render", return_value="r") as rnd:
            res = account_views.account_dashboard(req)
        assert res == "r"

    def test_exception_redirects(self, psc_session_req):
        req = psc_session_req()
        # Force render to fail by side-effecting config_data lookup
        with patch.object(
            account_views, "render", side_effect=Exception("boom")
        ):
            res = account_views.account_dashboard(req)
        assert res.status_code == 302
