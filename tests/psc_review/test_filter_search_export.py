"""Tests for FilterData, SearchData, ExportData classes in psc_views.py."""
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from preliminaryscreeningcommittee_review.views.psc_views import (
    ExportData,
    FilterData,
    SearchData,
)


def _customer(**kw):
    defaults = {
        "status": "Submitted",
        "branch_code_id": 1,
        "psc_rec_id": "PSC1",
        "branch_code": "BR001",
        "region_name": "South",
        "cust_id": "C1",
        "total_exposure": "1000",
        "borrower_name": "BN",
        "current_role": "BO Maker",
        "sac_rec_id": "SAC1",
        "sac_details": {
            "status": "Submitted",
            "total_exposure": "1,000",
            "current_role": "RO Maker",
        },
    }
    defaults.update(kw)
    return SimpleNamespace(**defaults)


class TestFilterPscData:
    def test_all_all_returns_unchanged(self):
        data = [_customer(), _customer(status="Approved")]
        assert FilterData.filter_psc_data(data, "all", "all") == data

    def test_zone_all_filters_by_status(self):
        data = [
            _customer(status="Submitted"),
            _customer(status="Approved"),
        ]
        result = FilterData.filter_psc_data(data, "all", "Approved")
        assert len(result) == 1
        assert result[0].status == "Approved"

    def test_status_all_filters_by_zone(self):
        data = [_customer(branch_code_id=1), _customer(branch_code_id=2)]
        result = FilterData.filter_psc_data(data, "2", "all")
        assert len(result) == 1
        assert result[0].branch_code_id == 2

    def test_both_filters_combined(self):
        data = [
            _customer(branch_code_id=1, status="Submitted"),
            _customer(branch_code_id=1, status="Approved"),
            _customer(branch_code_id=2, status="Approved"),
        ]
        result = FilterData.filter_psc_data(data, "1", "Approved")
        assert len(result) == 1


class TestFilterSacData:
    def test_all_all_unchanged(self):
        data = [_customer(), _customer()]
        assert FilterData.filter_sac_data(data, "all", "all") == data

    def test_zone_all_filters_status(self):
        data = [
            _customer(sac_details={"status": "Submitted"}),
            _customer(sac_details={"status": "Approved"}),
        ]
        result = FilterData.filter_sac_data(data, "all", "Approved")
        assert len(result) == 1

    def test_status_all_filters_zone(self):
        data = [_customer(branch_code_id=1), _customer(branch_code_id=2)]
        result = FilterData.filter_sac_data(data, "1", "all")
        assert len(result) == 1

    def test_both_filters_combined(self):
        data = [
            _customer(
                branch_code_id=1, sac_details={"status": "Submitted"}
            ),
            _customer(
                branch_code_id=1, sac_details={"status": "Approved"}
            ),
        ]
        result = FilterData.filter_sac_data(data, "1", "Approved")
        assert len(result) == 1


class TestSearchPscData:
    def test_no_search_returns_unchanged(self):
        data = [_customer()]
        assert SearchData.search_psc_data(data, "") == data

    def test_matches_psc_rec_id(self):
        data = [_customer(psc_rec_id="PSC999"), _customer(psc_rec_id="PSC1")]
        result = SearchData.search_psc_data(data, "PSC999")
        assert len(result) == 1

    def test_matches_borrower_name(self):
        data = [_customer(borrower_name="Alice"), _customer(borrower_name="Bob")]
        result = SearchData.search_psc_data(data, "Alice")
        assert len(result) == 1

    def test_matches_total_exposure_with_commas(self):
        data = [_customer(total_exposure="100000")]
        result = SearchData.search_psc_data(data, "1,00,000")
        assert len(result) == 1


class TestSearchSacData:
    def test_no_search_returns_unchanged(self):
        data = [_customer()]
        assert SearchData.search_sac_data(data, "") == data

    def test_matches_sac_rec_id(self):
        data = [_customer(sac_rec_id="X1"), _customer(sac_rec_id="X2")]
        result = SearchData.search_sac_data(data, "X1")
        assert len(result) == 1


class TestSearchMomData:
    def test_no_search_returns_unchanged(self):
        qs = MagicMock()
        assert SearchData.search_mom_data(qs, "") is qs

    def test_search_true_filters_active(self):
        qs = MagicMock()
        result = SearchData.search_mom_data(qs, "True")
        qs.filter.assert_called_once()
        assert result == qs.filter.return_value

    def test_search_false_filters_inactive(self):
        qs = MagicMock()
        result = SearchData.search_mom_data(qs, "False")
        qs.filter.assert_called_once()
        assert result == qs.filter.return_value

    def test_search_generic_text(self):
        qs = MagicMock()
        result = SearchData.search_mom_data(qs, "meeting")
        qs.filter.assert_called_once()
        assert result == qs.filter.return_value


class TestExportPscData:
    def test_all_all_unchanged(self):
        data = [{"status": "Submitted", "branch_code": 1}]
        assert ExportData.export_psc_data(data, "all", "all") == data

    def test_zone_all_filter_status(self):
        data = [
            {"status": "Submitted"},
            {"status": "Approved"},
        ]
        result = ExportData.export_psc_data(data, "all", "Approved")
        assert len(result) == 1

    def test_status_all_filter_zone(self):
        data = [{"branch_code": 1}, {"branch_code": 2}]
        result = ExportData.export_psc_data(data, "2", "all")
        assert len(result) == 1

    def test_both_filters(self):
        data = [
            {"status": "Submitted", "branch_code": 1},
            {"status": "Approved", "branch_code": 2},
            {"status": "Approved", "branch_code": 1},
        ]
        result = ExportData.export_psc_data(data, "1", "Approved")
        assert len(result) == 1


class TestExportSacData:
    def test_all_all_unchanged(self):
        qs = MagicMock()
        assert ExportData.export_sac_data(qs, "all", "all") is qs

    def test_filter_by_zone(self):
        qs = MagicMock()
        result = ExportData.export_sac_data(qs, "2", "all")
        qs.filter.assert_called_with(branch_code=2)

    def test_filter_by_status(self):
        qs = MagicMock()
        result = ExportData.export_sac_data(qs, "all", "Submitted")
        qs.filter.assert_called_with(sac_details__status="Submitted")

    def test_filter_combined(self):
        qs = MagicMock()
        ExportData.export_sac_data(qs, "1", "Submitted")
        qs.filter.assert_called_with(
            sac_details__status="Submitted", branch_code=1
        )
