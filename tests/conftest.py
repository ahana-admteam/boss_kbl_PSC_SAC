"""Shared pytest fixtures for the BOSS test suite.

Provides:
- A Django RequestFactory wrapper that attaches sessions/messages.
- A mocked session config_data Box that views deeply index into.
- Helpers to create BranchMaster / EmployeeMaster / RegistersMaster
  / RegistersRoleMaster / EmployeeRegisterRoleMaster fixtures.
- LDAP, Oracle, and Redis mocks.
"""
from __future__ import annotations

import datetime as _dt
import io
import os
import sys
from unittest import mock

import pytest

# Ensure project root on sys.path so `boss_admin` and friends import.
_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)


# ── Django setup happens via pytest-django reading DJANGO_SETTINGS_MODULE ──


@pytest.fixture(autouse=True)
def _disable_print(monkeypatch, capsys):
    """The codebase is littered with print() calls; we don't want them
    polluting pytest output but we DO want to be able to assert on them
    where it matters."""
    # nothing forced — capsys already captures, this fixture just exists
    # to make the dependency explicit
    yield


@pytest.fixture
def config_data_dict():
    """A minimally complete config_data dict suitable for wrapping in a Box."""
    return {
        "tenant": "demo",
        "logo_image": {"image_path": "/static/logo.png"},
        "global_styles": "/static/styles.css",
        "module": {
            "AD001": {
                "display_name": {
                    "admin": "Admin",
                    "document_movement": "Documents",
                },
                "properties": {
                    "register_role_master": {},
                    "register_master": {},
                },
            },
            "IN001": {"display_name": "Inward"},
            "PSC001": {
                "app_name": "PSC App",
                "sac_display_name": "SAC",
                "display_name": "PSC",
                "ynstatus": ["Yes", "No"],
            },
        },
        "notification_configurations": {"required": "False"},
        "file_folder": {"file_path": "/tmp/boss-test"},
        "file_extension": {"pdf": "pdf", "docx": "docx"},
        "reports_type": ["A", "B"],
    }


@pytest.fixture
def config_data_box(config_data_dict):
    from box import Box

    return Box(config_data_dict)


@pytest.fixture
def rf():
    from django.test import RequestFactory

    return RequestFactory()


def _attach_session(request, data=None):
    """Attach a usable session dict to a RequestFactory request."""
    from django.contrib.sessions.backends.signed_cookies import SessionStore

    request.session = SessionStore()
    if data:
        for k, v in data.items():
            request.session[k] = v
    request.session.save()
    return request


def _attach_messages(request):
    from django.contrib.messages.storage.fallback import FallbackStorage

    setattr(request, "_messages", FallbackStorage(request))
    return request


@pytest.fixture
def make_request(rf, config_data_dict):
    """Build a Django request with session, messages, and a sensible
    default session payload."""

    def _make(
        path="/",
        method="get",
        data=None,
        session=None,
        ajax=False,
        host="demo.localhost",
    ):
        method = method.lower()
        kw = {"HTTP_HOST": host}
        if ajax:
            kw["HTTP_X_REQUESTED_WITH"] = "XMLHttpRequest"
        builder = getattr(rf, method)
        request = builder(path, data or {}, **kw)
        sess = {
            "ses_key": "test-ses-key",
            "emp_id": "EMP001",
            "emp_name": "Test Emp",
            "branch_code": "BR001",
            "domain_id": "test_user",
            "designation": "Tester",
            "emp_desig_role": "Tester",
            "active": True,
            "branch_name": "Test Branch",
            "tenant": "demo",
            "new_roles": "psc001maker1",
            "audit_roles": "",
            "config_data": dict(config_data_dict),
        }
        if session:
            sess.update(session)
        _attach_session(request, sess)
        _attach_messages(request)
        return request

    return _make


@pytest.fixture
def branch(db):
    from boss_admin.models import BranchMaster

    return BranchMaster.objects.create(
        sl_no=1,
        branch_code="BR001",
        branch_name="Test Branch",
        active=True,
        zone="BR002",
        zone_name="South",
        created_user="tester",
    )


@pytest.fixture
def ro_branch(db):
    from boss_admin.models import BranchMaster

    return BranchMaster.objects.create(
        sl_no=2,
        branch_code="BR002",
        branch_name="Regional Office",
        active=True,
        zone="BR002",
        zone_name="South",
        created_user="tester",
    )


@pytest.fixture
def ho_branch(db):
    from boss_admin.models import BranchMaster

    return BranchMaster.objects.create(
        sl_no=3,
        branch_code="001",
        branch_name="Head Office",
        active=True,
        zone="001",
        zone_name="HO",
        created_user="tester",
    )


@pytest.fixture
def employee(db, branch):
    from boss_admin.models import EmployeeMaster

    return EmployeeMaster.objects.create(
        sl_no=1,
        domain_id="test_user",
        emp_id="EMP001",
        emp_name="Test Emp",
        pwd="pass",
        designation="Tester",
        branch_code=branch,
        branch_id=branch,
        active=True,
        email_id="test@example.com",
        phone_number=9999999999,
    )


@pytest.fixture
def register_master(db):
    from boss_admin.models import RegistersMaster

    return RegistersMaster.objects.create(
        sl_no=1,
        registers_code="PSC001",
        registers_type="PSC",
        registers_desc="Preliminary Screening Committee",
        is_active=True,
    )


@pytest.fixture
def register_role(db, register_master):
    from boss_admin.models import RegistersRoleMaster

    return RegistersRoleMaster.objects.create(
        role_name="PSC BO Maker",
        role_desc="psc001maker1",
        registers_code=register_master,
        is_active=True,
    )


@pytest.fixture
def emp_register_role(db, employee, register_master, register_role, branch):
    from boss_admin.models import EmployeeRegisterRoleMaster

    return EmployeeRegisterRoleMaster.objects.create(
        emp_id=employee,
        registers_code=register_master,
        role_id=register_role,
        branch_code=branch,
        branch_id=branch,
        is_active=True,
        designation="Tester",
    )


@pytest.fixture
def mock_ldap(monkeypatch):
    """Replace ldap3 Server and Connection with mocks. Connection.bind()
    returns True by default; tests can override the return value."""
    server_mock = mock.MagicMock(name="LDAPServer")
    conn_mock = mock.MagicMock(name="LDAPConnection")
    conn_mock.bind.return_value = True
    conn_mock.unbind.return_value = True
    conn_mock.search.return_value = True
    conn_mock.response_to_json.return_value = (
        '{"entries":[{"attributes":'
        '{"sAMAccountName":"test_user","employeeID":"EMP001",'
        '"givenName":"Tester","physicalDeliveryOfficeName":"BR001",'
        '"title":"Maker","department":"BO"}}]}'
    )

    def _server_factory(*args, **kwargs):
        return server_mock

    def _conn_factory(*args, **kwargs):
        return conn_mock

    monkeypatch.setattr("boss_admin.dbutil.Server", _server_factory)
    monkeypatch.setattr("boss_admin.dbutil.Connection", _conn_factory)
    return conn_mock


@pytest.fixture
def mock_socket(monkeypatch):
    monkeypatch.setattr(
        "boss_admin.dbutil.socket.gethostname", lambda: "test-host"
    )
    monkeypatch.setattr(
        "boss_admin.dbutil.socket.gethostbyname", lambda h: "127.0.0.1"
    )


@pytest.fixture
def mock_requests(monkeypatch):
    """Patch requests.post used by KBLAPIWrapper."""
    response_mock = mock.MagicMock()
    response_mock.json.return_value = {"access_token": "tok", "Response": "enc-resp"}

    post = mock.MagicMock(return_value=response_mock)
    monkeypatch.setattr("boss_admin.views.kbl_api.requests.post", post)
    return post, response_mock


@pytest.fixture
def freeze_time():
    """Tiny wrapper around freezegun's freeze_time."""
    import freezegun

    return freezegun.freeze_time


@pytest.fixture
def tmp_log_dir(tmp_path):
    """Temp directory tests can use for log/file rotation tests."""
    d = tmp_path / "logs"
    d.mkdir()
    return d


@pytest.fixture
def fake_file_storage(monkeypatch, tmp_path):
    """Point FileSystemStorage at a temp directory."""
    from django.core.files.storage import FileSystemStorage

    monkeypatch.setattr(FileSystemStorage, "location", str(tmp_path))
    return tmp_path
