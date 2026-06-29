"""Tests for psc_views.NotifyMail.rejectionMailerFunction."""
from unittest.mock import MagicMock, patch

import pytest

from preliminaryscreeningcommittee_review.views import psc_views


def _setup_mail_session(req, employee, psc_record):
    from box import Box

    req.session["config_data"] = {
        "module": {
            "PSC001": {
                "mail_configuration": {
                    "MAIL_CC": ["cc@example.com"],
                    "TO_MAIL": "to@example.com",
                    "SUBJECT": "Rejection {type} #{id}",
                    "BODY_line1": "Rejected {type} {id} by {rejected_by} on {rejection_date}\n",
                    "BODY_line2": "Remarks: {reject_remarks} Level: {reject_level}",
                    "Smtp_Server": "smtp.example.com",
                    "Smtp_Port": "587",
                    "Email_User": "no-reply@example.com",
                    "Email_Password": "pw",
                }
            }
        }
    }
    req.session["new_roles"] = "BO_M"


class TestRejectionMailerFunction:
    def test_smtp_path_psc(
        self, psc_session_req, db, psc_record, employee, monkeypatch
    ):
        from boss_admin.models import DesignationMatrix

        DesignationMatrix.objects.create(
            role_type="Branch",
            role_name="BO Maker",
            role_code="BO_M",
            designations=["x"],
        )
        req = psc_session_req()
        _setup_mail_session(req, employee, psc_record)
        server = MagicMock()
        monkeypatch.setattr(
            "preliminaryscreeningcommittee_review.views.psc_views.smtplib.SMTP",
            MagicMock(return_value=server),
        )
        reject_json = [
            {
                "rej_lvl": "BO",
                "rej_date": "01/01/2026",
                "rej_remarks": "Bad data",
            }
        ]
        psc_views.NotifyMail.rejectionMailerFunction(
            req, psc_record.psc_rec_id, "PSC", reject_json
        )
        # SMTP setup methods called
        server.starttls.assert_called_once()
        server.login.assert_called_once()
        server.sendmail.assert_called_once()

    def test_smtp_path_sac(
        self, psc_session_req, db, sac_record, employee, monkeypatch
    ):
        from boss_admin.models import DesignationMatrix

        DesignationMatrix.objects.create(
            role_type="Branch",
            role_name="BO Maker",
            role_code="BO_M",
            designations=["x"],
        )
        req = psc_session_req()
        _setup_mail_session(req, employee, sac_record)
        server = MagicMock()
        monkeypatch.setattr(
            "preliminaryscreeningcommittee_review.views.psc_views.smtplib.SMTP",
            MagicMock(return_value=server),
        )
        reject_json = [
            {
                "rej_lvl": "RO",
                "rej_date": "01/01/2026",
                "rej_remarks": "Issue",
            }
        ]
        psc_views.NotifyMail.rejectionMailerFunction(
            req, sac_record.sac_rec_id, "SAC", reject_json
        )
        server.sendmail.assert_called_once()

    def test_exception_path_propagates_when_session_role_missing(
        self, psc_session_req, employee, monkeypatch
    ):
        """The except branch references `session_role` which isn't defined
        if the DesignationMatrix lookup at the top of the try block fails.
        That makes the rescue itself raise a NameError."""
        # No DesignationMatrix row created → IndexError on session_role lookup
        # → except branch tries to print using `session_role` → NameError
        req = psc_session_req()
        _setup_mail_session(req, employee, None)
        with pytest.raises((NameError, IndexError, UnboundLocalError)):
            psc_views.NotifyMail.rejectionMailerFunction(
                req, "X", "BAD", [{"rej_lvl": "BO", "rej_date": "x", "rej_remarks": "y"}]
            )
