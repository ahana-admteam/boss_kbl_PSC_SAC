"""Tests for boss_admin/views/kbl_auth.py."""
import json
from unittest.mock import MagicMock, patch

import pytest

from boss_admin.views import kbl_auth


class TestSimCheck:
    def test_string_match_ignores_punctuation_and_case(self):
        assert kbl_auth.sim_check("BO-Maker", "bomaker") is True

    def test_string_no_match(self):
        assert kbl_auth.sim_check("Officer", "Manager") is False

    def test_list_match(self):
        assert kbl_auth.sim_check("BO Maker", ["BO_MAKER", "Other"]) is True

    def test_list_no_match(self):
        assert kbl_auth.sim_check("Officer", ["Manager", "Director"]) is False

    def test_empty_list_returns_false(self):
        assert kbl_auth.sim_check("anything", []) is False

    def test_special_chars_normalized(self):
        assert kbl_auth.sim_check("RO-Maker/Officer", "romakerofficer") is True


class TestLoginVerification:
    def test_raises_when_file_missing(self):
        """The file open is outside the try block, so a missing key file raises."""
        with pytest.raises((FileNotFoundError, OSError)):
            kbl_auth.login_verification("x", "y", "z")

    def test_db_path_success(self, db, employee, tmp_path, monkeypatch):
        keys_dir = tmp_path / "boss_admin" / "keys"
        keys_dir.mkdir(parents=True)
        (keys_dir / f"private_key_{employee.domain_id}_dt.pem").write_text("x")
        monkeypatch.setattr(
            "boss_admin.views.kbl_auth.settings.BASE_DIR", str(tmp_path)
        )
        monkeypatch.setattr(
            "boss_admin.views.kbl_auth.file_decrpyt_contents", lambda f: "x"
        )
        cipher = MagicMock()
        cipher.decrypt.return_value = employee.pwd.encode("utf-8")
        monkeypatch.setattr(
            "boss_admin.views.kbl_auth.RSA.importKey", lambda x: MagicMock()
        )
        monkeypatch.setattr(
            "boss_admin.views.kbl_auth.PKCS1_OAEP.new",
            lambda key, hashAlgo: cipher,
        )
        monkeypatch.setattr(
            "boss_admin.views.kbl_auth.base64.b64decode", lambda x: b"c"
        )
        resp = kbl_auth.login_verification(employee.domain_id, "x", "dt")
        body = json.loads(resp.content)
        assert body["msg"] == "success"

    def test_db_path_wrong_password_returns_fail(
        self, db, employee, tmp_path, monkeypatch
    ):
        keys_dir = tmp_path / "boss_admin" / "keys"
        keys_dir.mkdir(parents=True)
        (keys_dir / f"private_key_{employee.domain_id}_dt.pem").write_text("x")
        monkeypatch.setattr(
            "boss_admin.views.kbl_auth.settings.BASE_DIR", str(tmp_path)
        )
        monkeypatch.setattr(
            "boss_admin.views.kbl_auth.file_decrpyt_contents", lambda f: "x"
        )
        cipher = MagicMock()
        cipher.decrypt.return_value = b"WRONG"
        monkeypatch.setattr(
            "boss_admin.views.kbl_auth.RSA.importKey", lambda x: MagicMock()
        )
        monkeypatch.setattr(
            "boss_admin.views.kbl_auth.PKCS1_OAEP.new",
            lambda key, hashAlgo: cipher,
        )
        monkeypatch.setattr(
            "boss_admin.views.kbl_auth.base64.b64decode", lambda x: b"c"
        )
        resp = kbl_auth.login_verification(employee.domain_id, "x", "dt")
        assert json.loads(resp.content)["msg"] == "fail"

    def test_ad_login_path_calls_ad_login_test(
        self, db, tmp_path, monkeypatch
    ):
        """If AD_LOGIN=True and ad_login_test returns falsy, returns fail."""
        keys_dir = tmp_path / "boss_admin" / "keys"
        keys_dir.mkdir(parents=True)
        (keys_dir / "private_key_x_dt.pem").write_text("x")
        monkeypatch.setattr(
            "boss_admin.views.kbl_auth.settings.BASE_DIR", str(tmp_path)
        )
        monkeypatch.setattr(
            "boss_admin.views.kbl_auth.file_decrpyt_contents", lambda f: "x"
        )
        cipher = MagicMock()
        cipher.decrypt.return_value = b"pwd"
        monkeypatch.setattr(
            "boss_admin.views.kbl_auth.RSA.importKey", lambda x: MagicMock()
        )
        monkeypatch.setattr(
            "boss_admin.views.kbl_auth.PKCS1_OAEP.new",
            lambda k, hashAlgo: cipher,
        )
        monkeypatch.setattr(
            "boss_admin.views.kbl_auth.base64.b64decode", lambda x: b"c"
        )
        monkeypatch.setattr(
            "boss_admin.views.kbl_auth.base.AD_LOGIN", True
        )
        monkeypatch.setattr(
            "boss_admin.views.kbl_auth.ad_login_test", lambda d, p: False
        )
        resp = kbl_auth.login_verification("x", "y", "dt")
        assert json.loads(resp.content)["msg"] == "fail"


class TestLoadSession:
    def _ad_payload(self, **overrides):
        attrs = {
            "sAMAccountName": "test_user",
            "employeeID": "EMP001",
            "givenName": "Tester",
            "physicalDeliveryOfficeName": "BR001",
            "title": "Officer",
            "department": "BO",
        }
        attrs.update(overrides)
        return {"entries": [{"attributes": attrs}]}

    def test_returns_title_na_when_title_empty(
        self, rf, db, branch, monkeypatch
    ):
        from boss_admin.models import DesignationMatrix

        DesignationMatrix.objects.create(
            role_type="Branch",
            role_name="BO_OFFICER",
            role_code="BOM",
            designations=["Officer"],
        )
        kbl_auth.config_data = {"x": 1}
        req = rf.post("/")
        req.session = {}
        payload = self._ad_payload(title="")
        result = kbl_auth.load_session(payload, req, "demo", "SES")
        # JsonResponse with title na
        assert json.loads(result.content)["msg"] == "title na"

    def test_returns_dept_na_for_head_with_empty_dept(
        self, rf, db, monkeypatch
    ):
        from boss_admin.models import BranchMaster

        BranchMaster.objects.create(
            sl_no=10, branch_code="001", branch_name="HO",
        )
        kbl_auth.config_data = {"x": 1}
        req = rf.post("/")
        req.session = {}
        payload = self._ad_payload(
            physicalDeliveryOfficeName="001", title="Manager", department=""
        )
        result = kbl_auth.load_session(payload, req, "demo", "SES")
        body = json.loads(result.content)
        assert body["msg"] == "department na"

    def test_returns_success_when_matched_branch_role(
        self, rf, db, branch, monkeypatch
    ):
        from boss_admin.models import DesignationMatrix

        DesignationMatrix.objects.create(
            role_type="Branch",
            role_name="BO_OFFICER",
            role_code="BOM",
            designations=["Officer"],
        )
        kbl_auth.config_data = {"x": 1}
        monkeypatch.setattr(
            "boss_admin.views.kbl_auth.get_ip_address", lambda: "127.0.0.1"
        )
        req = rf.post("/")
        req.session = {}
        payload = self._ad_payload(physicalDeliveryOfficeName="BR001")
        result = kbl_auth.load_session(payload, req, "demo", "SES")
        assert result == "success"
        assert req.session["new_roles"] == "BOM"
        assert req.session["emp_id"] == "EMP001"

    def test_trailing_dot_in_emp_name_stripped(
        self, rf, db, branch, monkeypatch
    ):
        from boss_admin.models import DesignationMatrix

        DesignationMatrix.objects.create(
            role_type="Branch",
            role_name="BO_OFFICER",
            role_code="BOM",
            designations=["Officer"],
        )
        kbl_auth.config_data = {"x": 1}
        monkeypatch.setattr(
            "boss_admin.views.kbl_auth.get_ip_address", lambda: "127.0.0.1"
        )
        req = rf.post("/")
        req.session = {}
        payload = self._ad_payload(
            physicalDeliveryOfficeName="BR001", givenName="Tester ."
        )
        kbl_auth.load_session(payload, req, "demo", "SES")
        assert req.session["emp_name"] == "Tester"

    def test_returns_failure_on_exception(self, rf, db, monkeypatch):
        kbl_auth.config_data = {"x": 1}
        req = rf.post("/")
        req.session = {}
        from django.contrib.messages.storage.fallback import FallbackStorage

        setattr(req, "_messages", FallbackStorage(req))
        # Missing 'entries' key triggers KeyError → failure JSON
        result = kbl_auth.load_session({}, req, "demo", "SES")
        assert json.loads(result.content)["msg"] == "failure"


class TestLoginView:
    def test_login_get_renders_when_config_exists(
        self, rf, tmp_path, monkeypatch, config_data_dict
    ):
        cfg_dir = tmp_path / "boss_v1" / "configurations" / "ahana"
        cfg_dir.mkdir(parents=True)
        (cfg_dir / "ahana.config.json").write_text(json.dumps(config_data_dict))
        monkeypatch.setattr(
            "boss_admin.views.kbl_auth.settings.BASE_DIR", str(tmp_path)
        )
        req = rf.get("/", HTTP_HOST="ahana.localhost")
        with patch.object(kbl_auth, "render", return_value="rendered") as rnd:
            res = kbl_auth.login(req)
        assert res == "rendered"


class TestHomePage:
    def test_redirects_on_exception(self, db, rf):
        from boss_admin.models import Session

        Session.objects.create(ses_key="K")
        req = rf.get("/home")
        req.session = {"ses_key": "K", "new_roles": "X"}
        from django.contrib.messages.storage.fallback import FallbackStorage

        setattr(req, "_messages", FallbackStorage(req))
        resp = kbl_auth.home_page(req)
        assert resp.status_code == 302
