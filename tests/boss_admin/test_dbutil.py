"""Tests for boss_admin/dbutil.py."""
import json
from unittest.mock import MagicMock, patch

import pytest

from boss_admin import dbutil


class TestTitleFunctions:
    @pytest.mark.parametrize(
        "func,expected",
        [
            (dbutil.inward_title, "Inward"),
            (dbutil.outward_title, "Outward"),
            (dbutil.key_title, "Key Movement"),
            (dbutil.branch_title, "Branch Document"),
            (dbutil.issuance_title, "Security Issuance"),
            (dbutil.security_title, "Security Form"),
            (dbutil.suspense_title, "Suspense Cash"),
            (dbutil.audit_title, "Audit"),
            (dbutil.security_equipment_title, "Security Equipment"),
            (dbutil.petty_cash_title, "Teller Cash"),
            (dbutil.complaints_title, "Complaint Book"),
            (dbutil.manual_title, "Manual Receipt"),
            (dbutil.fixed_asset_title, "Fixed Asset"),
            (dbutil.gold_loan_title, "Gold Loan"),
            (dbutil.locker_access_title, "Locker Access"),
            (dbutil.it_asset_title, "IT Assets"),
            (dbutil.asset_management_title, "Assets Management"),
        ],
    )
    def test_returns_expected_string(self, func, expected):
        assert func() == expected


class TestGetIpAddress:
    def test_returns_resolved_ip(self, mock_socket):
        assert dbutil.get_ip_address() == "127.0.0.1"


class TestAdLoginTest:
    def test_returns_data_on_successful_bind(self, mock_ldap):
        result = dbutil.ad_login_test("user1", "pwd")
        assert isinstance(result, dict)
        assert "entries" in result

    def test_returns_false_when_bind_fails(self, mock_ldap):
        mock_ldap.bind.return_value = False
        assert dbutil.ad_login_test("user1", "pwd") is False

    def test_returns_exception_on_error(self, monkeypatch):
        def _raise(*a, **kw):
            raise RuntimeError("ldap down")

        monkeypatch.setattr(dbutil, "Server", _raise)
        result = dbutil.ad_login_test("user1", "pwd")
        assert isinstance(result, RuntimeError)


class TestGenerateSessionSesKey:
    def test_generates_token_of_at_least_20_chars(self, db):
        """Token is made of 20 picks from a choice list that includes the full
        domain_id string, so the final string is at least 20 chars (and can be
        longer if domain_id is picked one or more times)."""
        token = dbutil.generate_session_ses_key("abc")
        assert isinstance(token, str)
        assert len(token) >= 20

    def test_persists_session_row(self, db):
        from boss_admin.models import Session

        token = dbutil.generate_session_ses_key("abc")
        assert Session.objects.filter(ses_key=token).exists()

    def test_returns_false_on_db_error(self, monkeypatch):
        class _BadSession:
            def __init__(self, **kw):
                pass

            def save(self):
                raise RuntimeError("db down")

        monkeypatch.setattr(dbutil, "Session", _BadSession)
        assert dbutil.generate_session_ses_key("abc") is False


class TestConCurrentLogin:
    def test_returns_false_when_no_session(self, db):
        assert dbutil.con_current_login("NONE") is False

    def test_marks_existing_session_logged_out(
        self, db, employee, branch
    ):
        from boss_admin.models import Log, Session

        Session.objects.create(ses_key="K1")
        Log.objects.create(emp_id=employee, ses_key="K1", status="Login")

        result = dbutil.con_current_login(employee.emp_id)
        assert result is True

        # Log row was updated to Logout
        assert Log.objects.filter(
            emp_id=employee, status="Logout"
        ).exists()
        # Session deleted
        assert not Session.objects.filter(ses_key="K1").exists()

    def test_returns_true_when_log_exists_but_no_session(
        self, db, employee
    ):
        from boss_admin.models import Log

        Log.objects.create(emp_id=employee, ses_key="K2", status="Login")
        assert dbutil.con_current_login(employee.emp_id) is True


class TestEmpValidation:
    def test_success_returns_success_json(
        self, db, register_role, employee, branch, rf
    ):
        # New unique emp+domain should pass; reuse existing branch_code
        req = rf.post("/")
        result = dbutil.emp_validation(
            "new_domain",
            "NEW_EMP",
            branch.branch_code,
            "good@example.com",
            "9876543210",
            0,
            req,
        )
        data = json.loads(result.content)
        assert data["err_logs"] == "success"
        assert data["em_id"] == "yes"
        assert data["branch_id"] == "yes"
        assert data["dm_id"] == "yes"

    def test_existing_domain_id_flagged(
        self, db, register_role, employee, branch, rf
    ):
        req = rf.post("/")
        result = dbutil.emp_validation(
            employee.domain_id,
            "NEW_EMP",
            branch.branch_code,
            "ok@ok.com",
            "9999999999",
            0,
            req,
        )
        data = json.loads(result.content)
        assert isinstance(data["err_logs"], list)
        assert any("domain id" in m for m in data["err_logs"])

    def test_invalid_email_flagged(self, db, register_role, employee, branch, rf):
        """Pass a non-string email so re.search raises TypeError —
        that's the only path that sets email='no' in the source."""
        req = rf.post("/")
        result = dbutil.emp_validation(
            "newdom",
            "NEW1",
            branch.branch_code,
            None,
            "9876543210",
            0,
            req,
        )
        data = json.loads(result.content)
        assert any("Invalid email" in m for m in data["err_logs"])

    def test_missing_branch_flagged(self, db, register_role, employee, branch, rf):
        req = rf.post("/")
        result = dbutil.emp_validation(
            "newdom",
            "NEW2",
            "ZZZZ",
            "ok@ok.com",
            "9876543210",
            0,
            req,
        )
        data = json.loads(result.content)
        assert any("Branch code" in m for m in data["err_logs"])

    @pytest.mark.parametrize("bad_phone", ["nan", ""])
    def test_invalid_phone_flagged(
        self, db, register_role, employee, branch, rf, bad_phone
    ):
        req = rf.post("/")
        result = dbutil.emp_validation(
            "newdom",
            "NEW3",
            branch.branch_code,
            "ok@ok.com",
            bad_phone,
            0,
            req,
        )
        data = json.loads(result.content)
        assert isinstance(data["err_logs"], list)
        assert any("Phone number" in m for m in data["err_logs"])

    def test_duplicate_emp_id_flagged(
        self, db, register_role, employee, branch, rf
    ):
        req = rf.post("/")
        result = dbutil.emp_validation(
            "newdomain",
            employee.emp_id,
            branch.branch_code,
            "ok@ok.com",
            "9876543210",
            0,
            req,
        )
        data = json.loads(result.content)
        assert any("employee id" in m for m in data["err_logs"])


class TestMoveEmployee:
    def test_failure_when_already_in_branch(self, db, employee):
        result = dbutil.move_employee(
            employee.sl_no, employee.emp_id, employee.branch_code_id
        )
        assert json.loads(result.content)["err_logs"] == "fail"

    def test_success_when_branch_different(self, db, employee, ro_branch):
        result = dbutil.move_employee(
            employee.sl_no, employee.emp_id, ro_branch.branch_code
        )
        assert json.loads(result.content)["err_logs"] == "success"


class TestBranchValidation:
    def test_success_for_new_branch(self, db, rf):
        result = dbutil.branch_validation("NEWCODE", "Brand New Branch", 0)
        data = json.loads(result.content)
        assert data["err_logs"] == "success"
        assert data["brnch_code"] == "yes"
        assert data["brnch_name"] == "yes"

    def test_duplicate_branch_code(self, db, branch):
        result = dbutil.branch_validation(branch.branch_code, "New Name", 0)
        data = json.loads(result.content)
        assert isinstance(data["err_logs"], list)
        assert any("Branch Code" in m for m in data["err_logs"])
        assert data["brnch_code"] == "no"

    def test_duplicate_branch_name_case_insensitive(self, db, branch):
        result = dbutil.branch_validation(
            "OTHERCODE", branch.branch_name.upper(), 0
        )
        data = json.loads(result.content)
        assert any("Branch Name" in m for m in data["err_logs"])
        assert data["brnch_name"] == "no"
