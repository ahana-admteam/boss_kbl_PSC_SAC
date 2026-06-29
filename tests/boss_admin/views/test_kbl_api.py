"""Tests for boss_admin/views/kbl_api.py."""
import json
from unittest.mock import MagicMock, patch

import pytest

from boss_admin.views import kbl_api
from boss_admin.views.kbl_api import KBLAPIWrapper


class TestEncryptDecrypt:
    def test_encrypt_calls_jwe(self, monkeypatch, tmp_path):
        cert = tmp_path / "uatreqenc25.pem"
        cert.write_bytes(b"PEM")
        monkeypatch.setattr(
            "boss_admin.views.kbl_api.settings.base.KEYS_ROOT", str(tmp_path)
        )
        public_key = MagicMock()
        monkeypatch.setattr(
            "boss_admin.views.kbl_api.jwk.JWK.from_pem", lambda b: public_key
        )
        jwe_token = MagicMock()
        jwe_token.serialize.return_value = "encrypted"
        monkeypatch.setattr(
            "boss_admin.views.kbl_api.jwe.JWE",
            lambda payload, recipient, protected: jwe_token,
        )
        assert KBLAPIWrapper.encrypt({"k": "v"}) == "encrypted"

    def test_decrypt_returns_dict(self, monkeypatch, tmp_path):
        cert = tmp_path / "plain.pem"
        cert.write_bytes(b"PEM")
        monkeypatch.setattr(
            "boss_admin.views.kbl_api.settings.base.KEYS_ROOT", str(tmp_path)
        )
        private_key = MagicMock()
        monkeypatch.setattr(
            "boss_admin.views.kbl_api.jwk.JWK.from_pem", lambda b: private_key
        )
        jwetoken = MagicMock()
        jwetoken.payload = b'{"x": 1}'
        monkeypatch.setattr(
            "boss_admin.views.kbl_api.jwe.JWE", lambda: jwetoken
        )
        assert KBLAPIWrapper.decrypt("blob") == {"x": 1}


class TestOAuthBearer:
    def test_returns_access_token(self, monkeypatch):
        resp = MagicMock()
        resp.json.return_value = {"access_token": "TOK"}
        post = MagicMock(return_value=resp)
        monkeypatch.setattr("boss_admin.views.kbl_api.requests.post", post)
        assert KBLAPIWrapper.OAuthBearer("scp", "http://x") == "TOK"
        post.assert_called_once()


class TestAPICalls:
    """Each top-level API method delegates to OAuthBearer + encrypt + post + decrypt."""

    def _patch_pipeline(self, monkeypatch, response_payload=None):
        monkeypatch.setattr(
            "boss_admin.views.kbl_api.KBLAPIWrapper.OAuthBearer",
            staticmethod(lambda scope, url: "TOK"),
        )
        monkeypatch.setattr(
            "boss_admin.views.kbl_api.KBLAPIWrapper.encrypt",
            staticmethod(lambda payload: "ENC"),
        )
        resp = MagicMock()
        resp.json.return_value = {"Response": "ENC-RESP"}
        # Configurable truthiness via response_payload
        if response_payload is not None:
            resp.json.return_value = response_payload
        monkeypatch.setattr(
            "boss_admin.views.kbl_api.requests.post",
            MagicMock(return_value=resp),
        )
        monkeypatch.setattr(
            "boss_admin.views.kbl_api.KBLAPIWrapper.decrypt",
            staticmethod(lambda blob: {"status": "ok"}),
        )

    def test_npa_status_api_success(self, monkeypatch):
        self._patch_pipeline(monkeypatch)
        result = KBLAPIWrapper.NPAStatusAPI("ACC1")
        assert result == {"status": "ok"}

    def test_npa_status_api_failure(self, monkeypatch):
        monkeypatch.setattr(
            "boss_admin.views.kbl_api.KBLAPIWrapper.OAuthBearer",
            staticmethod(lambda *a, **kw: (_ for _ in ()).throw(
                RuntimeError("api down")
            )),
        )
        result = KBLAPIWrapper.NPAStatusAPI("ACC1")
        assert result == {"response": "Response not received as API is down"}

    def test_psc_dashboard_api_success(self, monkeypatch):
        self._patch_pipeline(monkeypatch)
        assert KBLAPIWrapper.PSCDashboardAPI("BR001") == {"status": "ok"}

    def test_psc_dashboard_api_failure(self, monkeypatch):
        monkeypatch.setattr(
            "boss_admin.views.kbl_api.KBLAPIWrapper.OAuthBearer",
            staticmethod(
                lambda *a, **kw: (_ for _ in ()).throw(RuntimeError("x"))
            ),
        )
        assert KBLAPIWrapper.PSCDashboardAPI("BR001") == {
            "response": "Response not received as API is down"
        }

    def test_branch_data_api_success(self, monkeypatch):
        self._patch_pipeline(monkeypatch)
        assert KBLAPIWrapper.BranchDataAPI() == {"status": "ok"}

    def test_branch_data_api_failure(self, monkeypatch):
        monkeypatch.setattr(
            "boss_admin.views.kbl_api.KBLAPIWrapper.OAuthBearer",
            staticmethod(
                lambda *a, **kw: (_ for _ in ()).throw(RuntimeError("x"))
            ),
        )
        assert KBLAPIWrapper.BranchDataAPI() == {
            "response": "Response not received as API is down"
        }

    def test_emp_data_api_success(self, monkeypatch):
        self._patch_pipeline(monkeypatch)
        assert KBLAPIWrapper.EmpDataAPI("EMP1") == {"status": "ok"}

    def test_emp_data_api_failure(self, monkeypatch):
        monkeypatch.setattr(
            "boss_admin.views.kbl_api.KBLAPIWrapper.OAuthBearer",
            staticmethod(
                lambda *a, **kw: (_ for _ in ()).throw(RuntimeError("x"))
            ),
        )
        assert KBLAPIWrapper.EmpDataAPI("EMP1") == {
            "response": "Response not received as API is down"
        }

    def test_customer_assets_api_success(self, monkeypatch):
        self._patch_pipeline(monkeypatch)
        assert KBLAPIWrapper.CustomerAssetsAPI("CUST1") == {"status": "ok"}

    def test_customer_assets_api_falsey_response(self, monkeypatch):
        """When requests.post returns a falsy response, returns a string msg."""
        monkeypatch.setattr(
            "boss_admin.views.kbl_api.KBLAPIWrapper.OAuthBearer",
            staticmethod(lambda *a, **kw: "TOK"),
        )
        monkeypatch.setattr(
            "boss_admin.views.kbl_api.KBLAPIWrapper.encrypt",
            staticmethod(lambda *a, **kw: "ENC"),
        )
        # Falsy response object: bool(MagicMock) is True by default, so set explicitly
        resp = MagicMock()
        resp.__bool__ = lambda self: False
        monkeypatch.setattr(
            "boss_admin.views.kbl_api.requests.post",
            MagicMock(return_value=resp),
        )
        result = KBLAPIWrapper.CustomerAssetsAPI("CUST1")
        assert isinstance(result, str)

    def test_customer_assets_api_failure(self, monkeypatch):
        monkeypatch.setattr(
            "boss_admin.views.kbl_api.KBLAPIWrapper.OAuthBearer",
            staticmethod(
                lambda *a, **kw: (_ for _ in ()).throw(RuntimeError("x"))
            ),
        )
        result = KBLAPIWrapper.CustomerAssetsAPI("CUST1")
        assert "Response not received" in result["response"]


class TestModuleConstants:
    def test_auth_urls_contains_keys(self):
        assert {
            "npa_status",
            "dashboard",
            "branch_data",
            "emp_details",
            "customer_assets",
        } <= set(kbl_api.auth_urls.keys())

    def test_service_urls_contains_keys(self):
        assert {
            "npa_status",
            "dashboard",
            "branch_data",
            "emp_details",
            "customer_assets",
        } <= set(kbl_api.service_urls.keys())

    def test_client_credentials_exposed(self):
        assert kbl_api.client_id
        assert kbl_api.client_secret
