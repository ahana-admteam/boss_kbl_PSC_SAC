"""Tests for boss_admin/views/kbl_reports.py."""
import datetime
from unittest.mock import MagicMock, patch

import pytest

from boss_admin.views import kbl_reports


@pytest.fixture
def session_req(rf, db, config_data_dict):
    from boss_admin.models import Session
    from django.contrib.messages.storage.fallback import FallbackStorage

    Session.objects.create(ses_key="R1")

    def _make(method="get", path="/", data=None, ajax=False):
        m = method.lower()
        kw = {}
        if ajax:
            kw["HTTP_X_REQUESTED_WITH"] = "XMLHttpRequest"
        req = getattr(rf, m)(path, data or {}, **kw)
        req.session = {
            "ses_key": "R1",
            "config_data": dict(config_data_dict),
        }
        setattr(req, "_messages", FallbackStorage(req))
        return req

    return _make


class TestKblReports:
    def test_renders_reports_page(self, session_req):
        req = session_req()
        with patch.object(kbl_reports, "render", return_value="r") as rnd:
            res = kbl_reports.kbl_reports(req)
        assert res == "r"


class TestKblReport:
    def test_get_renders_dashboard(self, session_req):
        req = session_req()
        with patch.object(kbl_reports, "render", return_value="r"):
            res = kbl_reports.kbl_report(req, "A")
        assert res == "r"

    def test_post_psc_returns_psc_data(self, session_req):
        req = session_req(
            method="post",
            data={
                "from_date": "2020-01-01",
                "to_date": "2030-12-31",
                "review_type": "PSC",
            },
            ajax=True,
        )
        with patch("boss_admin.views.kbl_reports.PSCTable") as PSCT:
            qs = MagicMock()
            qs.order_by.return_value = [{"psc_rec_id": "P1"}]
            PSCT.objects.filter.return_value.values.return_value = qs
            res = kbl_reports.kbl_report(req, "A")
        assert res.status_code == 200

    def test_post_sac_returns_sac_data(self, session_req):
        req = session_req(
            method="post",
            data={
                "from_date": "2020-01-01",
                "to_date": "2030-12-31",
                "review_type": "SAC",
            },
            ajax=True,
        )
        with patch("boss_admin.views.kbl_reports.SACTable") as SACT:
            qs = MagicMock()
            qs.order_by.return_value = [{"sac_rec_id": "S1"}]
            SACT.objects.filter.return_value.values.return_value = qs
            res = kbl_reports.kbl_report(req, "A")
        assert res.status_code == 200

    def test_post_dashboard_b(self, session_req):
        req = session_req(method="post", data={}, ajax=True)
        with patch("boss_admin.views.kbl_reports.PSCTable") as PSCT, patch(
            "boss_admin.views.kbl_reports.SACTable"
        ) as SACT:
            for tbl in (PSCT, SACT):
                qs = MagicMock()
                qs.values.return_value = []
                tbl.objects.filter.return_value = qs
            res = kbl_reports.kbl_report(req, "B")
        assert res.status_code == 200


class TestDownloadExcelA:
    def test_psc_branch(self, rf):
        kbl_reports.report_dataA = [
            {
                "psc_rec_id": "P1",
                "branch_code": "B1",
                "region_name": "R",
                "cust_id": "C",
                "borrower_name": "BN",
                "facility_num": "F",
                "sanc_limit": 100,
                "npa_date": datetime.datetime(2024, 1, 1),
                "nap_tag": "T",
                "status": "S",
                "current_role": "X",
            }
        ]
        req = rf.get("/")
        resp = kbl_reports.download_excel_A(req)
        assert resp["Content-Type"].startswith("application/ms-excel")
        assert "PSC_report.xlsx" in resp["Content-Disposition"]

    def test_sac_branch(self, rf):
        kbl_reports.report_dataA = [
            {
                "sac_rec_id": "S1",
                "psc_rec_id__branch_code": "B",
                "psc_rec_id__region_name": "R",
                "psc_rec_id__cust_id": "C",
                "psc_rec_id__borrower_name": "BN",
                "psc_rec_id__facility_num": "F",
                "psc_rec_id__sanc_limit": 100,
                "psc_rec_id__npa_date": datetime.datetime(2024, 1, 1),
                "psc_rec_id__nap_tag": "T",
                "status": "S",
                "current_role": "X",
            }
        ]
        req = rf.get("/")
        resp = kbl_reports.download_excel_A(req)
        assert "SAC_report.xlsx" in resp["Content-Disposition"]


class TestDownloadExcelB:
    def test_writes_workbook(self, rf):
        kbl_reports.report_dataB = {
            "psc_data": {
                "BOM": [{"psc_rec_id": "P1"}],
                "BOC": [],
                "ROM": [],
                "ROC": [],
                "HOM": [],
                "HOC": [],
                "CON": [],
            },
            "sac_data": {
                "ROM": [{"sac_rec_id": "S1"}],
                "ROC": [],
                "HOM": [],
                "HOC": [],
                "CON": [],
            },
        }
        req = rf.get("/")
        resp = kbl_reports.download_excel_B(req)
        assert (
            "spreadsheetml.sheet" in resp["Content-Type"]
            or resp["Content-Type"].startswith("application/")
        )
        assert "report.xlsx" in resp["Content-Disposition"]
