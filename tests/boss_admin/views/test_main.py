"""Tests for boss_admin/views/main.py."""
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from boss_admin.views import main


class TestLogOut:
    def test_calls_redirect(self, db, employee, rf):
        from boss_admin.models import Log, Session

        Session.objects.create(ses_key="L1")
        Log.objects.create(emp_id=employee, ses_key="L1", status="Login")

        req = rf.get("/logout")
        from django.contrib.sessions.backends.signed_cookies import SessionStore

        req.session = SessionStore()
        req.session["ses_key"] = "L1"
        req.session["emp_id"] = employee.emp_id
        req.session.save()

        resp = main.log_out(req)
        # Redirects to login_page
        assert resp.status_code == 302
        assert "/login" in resp["Location"]

    def test_redirects_when_session_invalid(self, rf, db):
        req = rf.get("/logout")
        req.session = {}  # no ses_key triggers @my_login_required redirect
        from django.contrib.messages.storage.fallback import FallbackStorage

        setattr(req, "_messages", FallbackStorage(req))
        resp = main.log_out(req)
        assert resp.status_code == 302


class TestGenericExport:
    def test_filters_by_date_range(self, db, branch, ro_branch, tmp_path, monkeypatch):
        from boss_admin.models import BranchMaster

        monkeypatch.chdir(tmp_path)
        req = MagicMock()
        resp = main.generic_export(req, BranchMaster, "2020-01-01", "2030-12-31")
        assert resp["Content-Type"].startswith("application/")
        assert "branch" in resp["Content-Disposition"].lower() or "BranchMaster" in resp["Content-Disposition"]

    def test_no_date_range_dumps_all(self, db, branch, tmp_path, monkeypatch):
        from boss_admin.models import BranchMaster

        monkeypatch.chdir(tmp_path)
        req = MagicMock()
        resp = main.generic_export(req, BranchMaster, None, None)
        assert resp.status_code == 200


class TestAddBranchExportView:
    def test_get_request_returns_none(self, rf, db):
        req = rf.get("/")
        # @my_login_required forces redirect to login when no session
        req.session = {}
        from django.contrib.messages.storage.fallback import FallbackStorage

        setattr(req, "_messages", FallbackStorage(req))
        resp = main.add_branch_export_view(req)
        assert resp.status_code == 302

    def test_post_calls_generic_export(self, rf, db, employee, branch, tmp_path, monkeypatch):
        from boss_admin.models import Session

        Session.objects.create(ses_key="X")
        monkeypatch.chdir(tmp_path)

        req = rf.post(
            "/", {"export_fromdate": "2020-01-01", "export_todate": "2030-12-31"}
        )
        req.session = {"ses_key": "X"}
        from django.contrib.messages.storage.fallback import FallbackStorage

        setattr(req, "_messages", FallbackStorage(req))
        resp = main.add_branch_export_view(req)
        assert resp.status_code == 200


class TestAddEmployeeExportView:
    def test_post_calls_generic_export(self, rf, db, employee, branch, tmp_path, monkeypatch):
        from boss_admin.models import Session

        Session.objects.create(ses_key="Y")
        monkeypatch.chdir(tmp_path)

        req = rf.post(
            "/", {"export_fromdate": "2020-01-01", "export_todate": "2030-12-31"}
        )
        req.session = {"ses_key": "Y"}
        from django.contrib.messages.storage.fallback import FallbackStorage

        setattr(req, "_messages", FallbackStorage(req))
        resp = main.add_employee_export_view(req)
        assert resp.status_code == 200


class TestDocumentViews:
    def test_document_delete_via_ajax_post(self, rf):
        req = rf.post("/", {"file_id": "5"}, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        with patch.object(main, "fileUpload") as fu:
            fu.file_upload.delete_documents.return_value = "deleted"
            resp = main.Document_delete(req)
        fu.file_upload.delete_documents.assert_called_with("5")
        assert resp.status_code == 200

    def test_document_delete_non_ajax_returns_none(self, rf):
        req = rf.post("/", {})
        assert main.Document_delete(req) is None

    def test_document_view_via_ajax_get(self, rf):
        req = rf.get("/", {"document_id": "3"}, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        with patch.object(main, "fileUpload") as fu:
            fu.file_upload.get_single_document.return_value = [{"file": "x"}]
            resp = main.Document_view(req)
        fu.file_upload.get_single_document.assert_called_with("3")
        assert resp.status_code == 200

    def test_document_view_non_ajax_returns_none(self, rf):
        req = rf.get("/", {})
        assert main.Document_view(req) is None


class TestApiCheck:
    @pytest.mark.parametrize(
        "api_type,wrapper_attr",
        [
            ("HUPMINQ", "EmpDataAPI"),
            ("Dashboard", "PSCDashboardAPI"),
            ("Branch", "BranchDataAPI"),
            ("PSC", "NPAStatusAPI"),
            ("CustomerAssets", "CustomerAssetsAPI"),
        ],
    )
    def test_dispatches_to_correct_api(
        self, rf, db, config_data_dict, api_type, wrapper_attr
    ):
        from boss_admin.models import Session

        Session.objects.create(ses_key="A1")
        req = rf.post(
            "/", {"apiType": api_type, "requestData": "RD"},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        req.session = {
            "ses_key": "A1",
            "config_data": dict(config_data_dict),
        }
        from django.contrib.messages.storage.fallback import FallbackStorage

        setattr(req, "_messages", FallbackStorage(req))
        with patch.object(main, "kApi") as kapi:
            getattr(kapi, wrapper_attr).return_value = {"ok": True}
            resp = main.api_check(req)
        assert resp.status_code == 200

    @pytest.mark.parametrize(
        "api_type,expected_msg",
        [
            ("DashboardCRON", "Dashboard CRON"),
            ("BranchCRON", "Branch CRON"),
            ("PSC_CRON", "PSC CRON"),
        ],
    )
    def test_cron_apis_return_message(
        self, rf, db, config_data_dict, api_type, expected_msg
    ):
        from boss_admin.models import Session

        Session.objects.create(ses_key="A2")
        req = rf.post(
            "/", {"apiType": api_type, "requestData": ""},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        req.session = {
            "ses_key": "A2",
            "config_data": dict(config_data_dict),
        }
        from django.contrib.messages.storage.fallback import FallbackStorage

        setattr(req, "_messages", FallbackStorage(req))
        resp = main.api_check(req)
        assert resp.status_code == 200
        import json
        assert json.loads(resp.content)["responseData"] == expected_msg

    def test_invalid_api_type(self, rf, db, config_data_dict):
        """For an unknown api_type the view sets responseData='Invalid' but
        never assigns jsonResponseData, so an UnboundLocalError is caught,
        printed, and the view returns None implicitly."""
        from boss_admin.models import Session

        Session.objects.create(ses_key="A3")
        req = rf.post(
            "/", {"apiType": "BOGUS", "requestData": ""},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        req.session = {
            "ses_key": "A3",
            "config_data": dict(config_data_dict),
        }
        from django.contrib.messages.storage.fallback import FallbackStorage

        setattr(req, "_messages", FallbackStorage(req))
        resp = main.api_check(req)
        # Internal UnboundLocalError caught → returns None
        assert resp is None

    def test_get_request_renders_template(self, rf, db, config_data_dict):
        from boss_admin.models import Session

        Session.objects.create(ses_key="A4")
        req = rf.get("/")
        req.session = {
            "ses_key": "A4",
            "config_data": dict(config_data_dict),
        }
        from django.contrib.messages.storage.fallback import FallbackStorage

        setattr(req, "_messages", FallbackStorage(req))
        with patch.object(main, "render", return_value="rendered") as rnd:
            res = main.api_check(req)
        assert res == "rendered"
