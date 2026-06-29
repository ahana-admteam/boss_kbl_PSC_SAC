"""Tests for psc_views.update_PSC_SAC_MOM_logs helper."""
from unittest.mock import MagicMock

import pytest

from preliminaryscreeningcommittee_review.views import psc_views


def _make_log_dict():
    return {
        "bo_maker": [],
        "ro_maker": [],
        "ho_maker": [],
        "bo_checker": [],
        "ro_checker": [],
        "ho_checker": [],
        "convener": [],
    }


def _instance(log_attr_name, log_dict):
    inst = MagicMock()
    setattr(inst, log_attr_name, log_dict)
    return inst


class TestUpdatePSCLogs:
    @pytest.mark.parametrize(
        "role_value,expected_key",
        [
            ("edit1", "bo_maker"),
            ("edit2", "ro_maker"),
            ("edit3", "ho_maker"),
            ("approve1", "bo_checker"),
            ("approve2", "ro_checker"),
            ("approve3", "ho_checker"),
            ("convener", "convener"),
        ],
    )
    def test_appends_to_correct_role_key(self, role_value, expected_key):
        log_dict = _make_log_dict()
        inst = _instance("psc_users_log", log_dict)
        user_log = {"ses_key": "S1", "status": "Submitted", "user": "u"}
        psc_views.update_PSC_SAC_MOM_logs(inst, role_value, user_log, "PSC")
        # log entry was appended to the right list
        assert inst.psc_users_log[expected_key][0] == user_log
        inst.save.assert_called_once()

    def test_appends_status_to_existing_session(self):
        log_dict = _make_log_dict()
        existing = {"ses_key": "SAME", "status": "Submitted", "user": "u"}
        log_dict["bo_maker"].append(existing)
        inst = _instance("psc_users_log", log_dict)
        new_log = {"ses_key": "SAME", "status": "Re-submitted", "user": "u"}
        psc_views.update_PSC_SAC_MOM_logs(inst, "edit1", new_log, "PSC")
        # Original status updated; no second entry
        assert len(inst.psc_users_log["bo_maker"]) == 1
        assert "Submitted" in inst.psc_users_log["bo_maker"][0]["status"]
        assert "Re-submitted" in inst.psc_users_log["bo_maker"][0]["status"]


class TestUpdateSACLogs:
    def test_sac_branch_executes(self):
        log_dict = _make_log_dict()
        inst = _instance("sac_users_log", log_dict)
        psc_views.update_PSC_SAC_MOM_logs(
            inst, "edit2", {"ses_key": "S", "status": "X"}, "SAC"
        )
        inst.save.assert_called_once()
