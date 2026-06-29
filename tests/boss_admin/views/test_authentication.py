"""Tests for boss_admin/views/authentication.py."""
import json
import pathlib
from unittest.mock import MagicMock, patch

import pytest

from boss_admin.views import authentication


class TestGetHostname:
    def test_strips_port_and_returns_tenant(self, rf):
        req = rf.get("/", HTTP_HOST="kotak.localhost:8000")
        assert authentication.get_hostname(req) == "kotak"

    def test_lowercases(self, rf):
        req = rf.get("/", HTTP_HOST="KOTAK.LOCALHOST")
        assert authentication.get_hostname(req) == "kotak"

    def test_ip_address(self, rf):
        req = rf.get("/", HTTP_HOST="13.68.238.3:8443")
        assert authentication.get_hostname(req) == "13"


class TestFileGetContents:
    def test_reads_file_via_settings_base_dir(self, tmp_path, monkeypatch):
        # Build path the function expects
        keys_dir = tmp_path / "boss_admin" / "keys"
        keys_dir.mkdir(parents=True)
        (keys_dir / "data.pem").write_text("PEM-CONTENT")

        monkeypatch.setattr(
            "boss_admin.views.authentication.settings.BASE_DIR",
            str(tmp_path),
        )
        assert authentication.file_get_contents("data.pem") == "PEM-CONTENT"


class TestFileDecryptContents:
    def test_reads_arbitrary_file(self, tmp_path):
        path = tmp_path / "x.pem"
        path.write_text("PRIV-KEY")
        assert authentication.file_decrpyt_contents(str(path)) == "PRIV-KEY"


class TestErrorView:
    def test_renders_error_404_template(self, rf):
        req = rf.get("/notfound")
        with patch("boss_admin.views.authentication.render") as rnd:
            rnd.return_value = "rendered"
            res = authentication.error_404(req, Exception("nope"))
        rnd.assert_called_once()
        assert res == "rendered"


class TestMyLoginRequired:
    def test_no_session_redirects_to_login(self, rf):
        req = rf.get("/")
        req.session = {}
        # messages
        from django.contrib.messages.storage.fallback import FallbackStorage

        setattr(req, "_messages", FallbackStorage(req))

        @authentication.my_login_required
        def view(request):
            return "ok"

        resp = view(req)
        assert resp.status_code == 302
        assert "/login" in resp["Location"]

    def test_existing_session_calls_view(self, rf, db):
        from boss_admin.models import Session

        Session.objects.create(ses_key="X1")
        req = rf.get("/")
        req.session = {"ses_key": "X1"}
        from django.contrib.messages.storage.fallback import FallbackStorage

        setattr(req, "_messages", FallbackStorage(req))

        @authentication.my_login_required
        def view(request):
            return "view-called"

        assert view(req) == "view-called"

    def test_unknown_session_returns_error(self, rf, db):
        req = rf.get("/")
        req.session = {"ses_key": "ZZ"}
        from django.contrib.messages.storage.fallback import FallbackStorage

        setattr(req, "_messages", FallbackStorage(req))

        @authentication.my_login_required
        def view(request):
            return "view-called"

        with patch.object(
            authentication, "render", return_value="error-rendered"
        ) as rnd:
            res = view(req)
        # error_404 path renders the error template
        assert res == "error-rendered"


class TestFileEncrypt:
    def test_creates_key_files(self, tmp_path, monkeypatch, rf):
        monkeypatch.setattr(
            "boss_admin.views.authentication.settings.BASE_DIR",
            str(tmp_path),
        )
        req = rf.post(
            "/file_encrypt", {"myid": "user1", "dtstmp": "12345"}
        )
        resp = authentication.file_encrypt(req)
        # Files should have been created in tmp_path/boss_admin/keys
        keys_dir = tmp_path / "boss_admin" / "keys"
        files = list(keys_dir.glob("*.pem"))
        names = {f.name for f in files}
        assert "private_key_user1_12345.pem" in names
        assert "public_key_user1_12345.pem" in names
        assert "BEGIN" in resp.content.decode() or len(resp.content) > 0

    def test_handles_exception_gracefully(self, rf):
        req = rf.post("/file_encrypt", {})
        # No myid/dtstmp -> file naming uses Nones, path operations succeed
        # but RSA stuff should still run; we just verify no exception escapes
        # (function prints and returns None on error).
        try:
            authentication.file_encrypt(req)
        except Exception:
            pytest.fail("file_encrypt must not propagate exceptions")


class TestFetchRolesAndCheckRole:
    """Tests for the fetch_roles + check_role helpers."""

    def test_check_role_success(self):
        resp = authentication.check_role("psc001maker1", "psc001maker1_other")
        assert resp.status_code == 200
        assert json.loads(resp.content)["msg"] == "success"

    def test_check_role_failure(self):
        resp = authentication.check_role("ghost", "psc001maker1_other")
        assert resp.status_code == 400
        assert json.loads(resp.content)["msg"] == "failure"

    def test_fetch_roles_loggedin_user_both_roles(
        self, db, emp_register_role, employee
    ):
        resp = authentication.fetch_roles(
            employee.emp_id, employee.branch_code_id, "loggedin_user_roles"
        )
        body = json.loads(resp.content)
        assert body["msg"] == "success"
        assert "psc001maker1" in body["user_roles"]

    def test_fetch_roles_with_role_check_success(
        self, db, emp_register_role, employee
    ):
        resp = authentication.fetch_roles(
            employee.emp_id, employee.branch_code_id, "psc001maker1"
        )
        body = json.loads(resp.content)
        assert body["msg"] == "success"

    def test_fetch_roles_with_role_check_failure(
        self, db, emp_register_role, employee
    ):
        resp = authentication.fetch_roles(
            employee.emp_id, employee.branch_code_id, "no_such_role"
        )
        body = json.loads(resp.content)
        assert body["msg"] == "failure"


class TestLoadSession:
    def test_returns_failure_when_no_employee_match(self, db, rf):
        req = rf.post("/")
        req.session = {}
        resp = authentication.load_session(
            "nosuchuser", req, "demo", "SES1"
        )
        assert resp.status_code == 200
        assert json.loads(resp.content)["msg"] == "failure"

    def test_returns_success_when_employee_exists(
        self, db, employee, monkeypatch
    ):
        # Set authentication.config_data global
        authentication.config_data = {"x": "y"}
        monkeypatch.setattr(
            "boss_admin.views.authentication.get_ip_address",
            lambda: "127.0.0.1",
        )
        # request needs a session dict
        from django.test import RequestFactory

        rf = RequestFactory()
        req = rf.post("/")
        req.session = {}
        result = authentication.load_session(
            employee.domain_id, req, "demo", "SES1"
        )
        assert result == "success"
        assert req.session["ses_key"] == "SES1"
        assert req.session["emp_id"] == employee.emp_id


class TestLoginVerification:
    """Tests for login_verification — covers RSA decrypt and DB lookup."""

    def test_raises_when_key_file_missing(self, rf):
        """The file open is OUTSIDE the try/except, so missing files raise."""
        with pytest.raises((FileNotFoundError, OSError)):
            authentication.login_verification("x", "y", "z")

    def test_db_auth_path_success(
        self, db, employee, tmp_path, monkeypatch
    ):
        """Mock RSA decryption to return employee's password."""
        from boss_admin.views import authentication as auth

        monkeypatch.setattr(
            "boss_admin.views.authentication.settings.BASE_DIR",
            str(tmp_path),
        )
        keys_dir = tmp_path / "boss_admin" / "keys"
        keys_dir.mkdir(parents=True)
        (keys_dir / f"private_key_{employee.domain_id}_dt.pem").write_text("x")
        monkeypatch.setattr(
            "boss_admin.views.authentication.file_decrpyt_contents",
            lambda f: "x",
        )
        # Patch RSA/cipher chain to give us employee.pwd back
        rsa_key = MagicMock()
        cipher = MagicMock()
        cipher.decrypt.return_value = employee.pwd.encode("utf-8")
        monkeypatch.setattr(
            "boss_admin.views.authentication.RSA.importKey", lambda x: rsa_key
        )
        monkeypatch.setattr(
            "boss_admin.views.authentication.PKCS1_OAEP.new",
            lambda k, hashAlgo: cipher,
        )
        # base64.b64decode also gets a string — let it run normally
        monkeypatch.setattr(
            "boss_admin.views.authentication.base64.b64decode",
            lambda x: b"ciphertext",
        )

        resp = auth.login_verification(employee.domain_id, "ANY", "dt")
        body = json.loads(resp.content)
        assert body["msg"] == "success"
        assert body["emp_id"] == employee.emp_id

    def test_db_auth_path_wrong_password(
        self, db, employee, tmp_path, monkeypatch
    ):
        keys_dir = tmp_path / "boss_admin" / "keys"
        keys_dir.mkdir(parents=True)
        (keys_dir / f"private_key_{employee.domain_id}_dt.pem").write_text("x")
        monkeypatch.setattr(
            "boss_admin.views.authentication.settings.BASE_DIR",
            str(tmp_path),
        )
        monkeypatch.setattr(
            "boss_admin.views.authentication.file_decrpyt_contents",
            lambda f: "x",
        )
        cipher = MagicMock()
        cipher.decrypt.return_value = b"WRONG_PASSWORD"
        monkeypatch.setattr(
            "boss_admin.views.authentication.RSA.importKey", lambda x: MagicMock()
        )
        monkeypatch.setattr(
            "boss_admin.views.authentication.PKCS1_OAEP.new",
            lambda k, hashAlgo: cipher,
        )
        monkeypatch.setattr(
            "boss_admin.views.authentication.base64.b64decode",
            lambda x: b"x",
        )
        resp = authentication.login_verification(employee.domain_id, "p", "dt")
        assert json.loads(resp.content)["msg"] == "fail"


class TestLoginView:
    def test_get_renders_login_page_when_config_dir_exists(
        self, tmp_path, monkeypatch, rf, config_data_dict
    ):
        # Place config file at tmp_path/boss_v1/configurations/ahana/ahana.config.json
        cfg_dir = tmp_path / "boss_v1" / "configurations" / "ahana"
        cfg_dir.mkdir(parents=True)
        (cfg_dir / "ahana.config.json").write_text(json.dumps(config_data_dict))

        monkeypatch.setattr(
            "boss_admin.views.authentication.settings.BASE_DIR",
            str(tmp_path),
        )

        req = rf.get("/", HTTP_HOST="ahana.localhost")
        with patch.object(
            authentication, "render", return_value="rendered"
        ) as rnd:
            res = authentication.login(req)
        rnd.assert_called_once()
        assert res == "rendered"

    def test_get_falls_back_to_ahana_when_tenant_missing(
        self, tmp_path, monkeypatch, rf, config_data_dict
    ):
        cfg_dir = tmp_path / "boss_v1" / "configurations" / "ahana"
        cfg_dir.mkdir(parents=True)
        (cfg_dir / "ahana.config.json").write_text(json.dumps(config_data_dict))
        monkeypatch.setattr(
            "boss_admin.views.authentication.settings.BASE_DIR", str(tmp_path)
        )

        req = rf.get("/", HTTP_HOST="unknown.localhost")
        with patch.object(
            authentication, "render", return_value="rendered"
        ):
            res = authentication.login(req)
        assert res == "rendered"


class TestHomePage:
    def test_redirects_on_exception(self, rf, db):
        from boss_admin.models import Session

        Session.objects.create(ses_key="HSESS")
        req = rf.get("/home")
        req.session = {"ses_key": "HSESS"}
        from django.contrib.messages.storage.fallback import FallbackStorage

        setattr(req, "_messages", FallbackStorage(req))
        # config_data global not set → exception path → redirect
        resp = authentication.home_page(req)
        assert resp.status_code == 302
