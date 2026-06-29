"""Tests for psc_views.py helper functions (the testable utilities)."""
from unittest.mock import MagicMock, patch

import pytest

from preliminaryscreeningcommittee_review.views import psc_views


class TestConvertToYYYYMMDD:
    def test_valid_date_string(self):
        assert psc_views.convertToYYYYMMDD("15-06-2024") == "2024-06-15"

    @pytest.mark.parametrize(
        "v", ["NO_DATA", "NULL", "null", "NA", "None", None]
    )
    def test_null_sentinels_return_default(self, v):
        assert psc_views.convertToYYYYMMDD(v) == "01-01-1990"

    def test_invalid_format_raises(self):
        with pytest.raises(ValueError):
            psc_views.convertToYYYYMMDD("not-a-date")


class TestDateSlash2Hyphen:
    def test_slash_format(self):
        assert psc_views.date_slash_2_hyphen("15/06/2024") == "15-06-2024"

    def test_hyphen_format(self):
        assert psc_views.date_slash_2_hyphen("15-06-2024") == "15-06-2024"

    @pytest.mark.parametrize(
        "v", ["NO_DATA", "NULL", "null", "NA", "None", None, ""]
    )
    def test_null_sentinels_return_default(self, v):
        assert psc_views.date_slash_2_hyphen(v) == "01-01-1990"

    def test_invalid_format_returns_none(self):
        # No format matches → returns None implicitly
        assert psc_views.date_slash_2_hyphen("not-a-date") is None


class TestApiDatatypeCheck:
    def test_valid_value_returned(self):
        assert psc_views.api_datatype_check("real-data") == "real-data"

    @pytest.mark.parametrize(
        "v", ["NO_DATA", "NULL", "null", "NA", "None", None]
    )
    def test_null_sentinels(self, v):
        assert psc_views.api_datatype_check(v) == "01-01-1990"


class TestApiDataTypeNumCheck:
    def test_valid_returned(self):
        assert psc_views.api_dataType_num_check(123) == 123

    @pytest.mark.parametrize(
        "v", ["NO_DATA", "NULL", "null", "NA", "None", None]
    )
    def test_null_sentinels_return_zero(self, v):
        assert psc_views.api_dataType_num_check(v) == 0


class TestGetApiData:
    def test_runs_without_exception_when_flag_true(self, psc_session_req):
        sess = {"config_data": {"module": {"PSC001": {"is_api_data": True}}}}
        req = psc_session_req(session_extra=sess)
        assert psc_views.get_apidata(req) is None

    def test_runs_without_exception_when_flag_false(self, psc_session_req):
        sess = {"config_data": {"module": {"PSC001": {"is_api_data": False}}}}
        req = psc_session_req(session_extra=sess)
        assert psc_views.get_apidata(req) is None


class TestModifyCustAsstData:
    def _build_api_response(self):
        return {
            "RequestUUID": "RID1",
            "HStatus": "OK",
            "Name_of_the_Properiter_1": "Borrower",
            "Address_1": "Addr",
            "Constitution_1": "Indv",
            "DateOfEstablishment_1": "01-01-2020",
            "Networth_of_the_Borrower_1": 1000,
            "Dealing_with_us_Since_1": "01-01-2018",
            "Nature_of_Business_1": "Trade",
            "Names_of_the_Co_Obligant_1": "Co-Obg",
            "Loan_Account_No_1": "LAN1",
            "Sanction_Ref_Number_1": "REF1",
            "Sanction_Date_1": "01-01-2024",
            "Nature_of_Account_1": "OD",
            "Count_of_Securities_1": "1",
            "SanctionLimitAmt_1": 500000,
            "DueDate_1": "01-01-2026",
            "DATE_OF_NPA_1": "01-06-2025",
            "BalanceAsOnNPADate_1": 200000,
            "Purpose_of_Advance_1": "P",
            "ASSET_CLASSIFICATION_1": "Sub",
            "AodDate_1": "01-01-2024",
            "Nature_of_Security_1": "Property",
            "Type_of_Security_1": "Mortgage",
            "Date_of_Valuation_Sanction_1": "01/01/2024",
            "Present_Valuation_1": 600000,
            "Date_of_Valuation_1": "01/01/2025",
            "InsuranceVaidUpToDate_1": "01-01-2027",
            "InsuranceValue_1": 400000,
            "CERSAI_Number_1": "CER1",
        }

    def test_builds_expected_payload(self, psc_session_req):
        req = psc_session_req()
        result = psc_views.modify_cust_asst_data(req, self._build_api_response())
        assert result["RequestUUID"] == "RID1"
        assert result["basic_details"]["borrower_name"] == "Borrower"
        assert len(result["credit_facility"]) == 1
        assert len(result["securities_values"]) == 1
        assert result["credit_facility"][0]["lan"] == "LAN1"

    def test_no_loan_accounts_returns_empty_lists(self, psc_session_req):
        req = psc_session_req()
        result = psc_views.modify_cust_asst_data(
            req, {"RequestUUID": "x", "HStatus": "ok"}
        )
        assert result["credit_facility"] == []
        assert result["securities_values"] == []

    def test_exception_returns_none(self, psc_session_req):
        req = psc_session_req()
        # Force exception by passing non-dict
        assert psc_views.modify_cust_asst_data(req, None) is None


class TestModuleConstants:
    def test_psc_all_data_includes_key_columns(self):
        for col in (
            "id",
            "psc_rec_id",
            "borrower_name",
            "status",
            "npa_date",
        ):
            assert col in psc_views.psc_all_data

    def test_sac_all_data_includes_key_columns(self):
        for col in ("id", "sac_rec_id", "status", "psc_date"):
            assert col in psc_views.sac_all_data

    def test_credit_sanction_columns(self):
        for col in ("id", "lan", "sanctioned_limit"):
            assert col in psc_views.creditsanction_all_data

    def test_securities_columns(self):
        for col in ("id", "lan", "cersai_num"):
            assert col in psc_views.securities_all_data

    def test_mom_columns(self):
        for col in ("id", "meeting_id", "review_type"):
            assert col in psc_views.mom_all_data


class TestAppName:
    def test_app_name_constant(self):
        assert psc_views.app_name == "preliminaryscreeningcommittee_review"
