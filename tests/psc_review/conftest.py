"""PSC-specific fixtures."""
from datetime import datetime

import pytest


@pytest.fixture
def mom(db, employee):
    from preliminaryscreeningcommittee_review.models import MOMTable

    return MOMTable.objects.create(
        created_user=employee.emp_id,
        meeting_id="MOM1",
        mom_creation_date=datetime(2026, 1, 1),
        mom_date=datetime(2026, 1, 10),
        audience={"members": ["a", "b"]},
        last_modified_user=employee.emp_id,
        review_type="PSC",
        mom_users_log={
            "ho_checker": [],
            "convener": [],
        },
    )


@pytest.fixture
def customer(db, employee, branch):
    from preliminaryscreeningcommittee_review.models import CustomerTable

    return CustomerTable.objects.create(
        created_user=employee.emp_id,
        psc_rec_id="PSC123",
        sac_rec_id="SAC123",
        psc_review_id="PSCR123",
        sac_review_id="SACR123",
        cust_id="CUST1",
        borrower_name="Borrower",
        branch_code=branch,
        region_name="South",
        total_exposure="1000",
        acc_count="1",
        current_role="BO Maker",
        status="Submitted",
        last_modified_user=employee.emp_id,
        sac_details={"status": "active"},
        lapses_details={"records": [{"staff_no": "S1"}]},
    )


@pytest.fixture
def psc_record(db, employee, branch):
    from preliminaryscreeningcommittee_review.models import PSCTable

    return PSCTable.objects.create(
        created_user=employee.emp_id,
        psc_rec_id="PSC123",
        branch_code=branch,
        region_name="South",
        cust_id="CUST1",
        facility_num="F1",
        sanc_limit=1000000,
        npa_date=datetime(2025, 6, 1),
        nap_tag="Sub-standard",
        npa_status=True,
        status="Submitted",
        current_role="BO Maker",
        borrower_name="BN",
        last_modified_user=employee.emp_id,
    )


@pytest.fixture
def sac_record(db, employee, psc_record):
    from preliminaryscreeningcommittee_review.models import SACTable

    return SACTable.objects.create(
        created_user=employee.emp_id,
        psc_rec_id=psc_record,
        sac_rec_id="SAC123",
        emp_name="E",
        staff_no="S1",
        present_designation="Officer",
        present_working="Active",
        status="Submitted",
        psc_date=datetime(2025, 7, 1),
        last_modified_user=employee.emp_id,
        current_role="RO Maker",
    )


@pytest.fixture
def credit_facility(db, employee, customer):
    from preliminaryscreeningcommittee_review.models import CreditFacilityTable

    return CreditFacilityTable.objects.create(
        created_user=employee.emp_id,
        psc_id=customer,
        credit_feci_slno=1,
        reference_num="REF1",
        sanction_date=datetime(2024, 1, 1),
        account_nature="OD",
        advance_nature="Sec",
        lan="LAN1",
        sanctioned_limit=500000.00,
        due_date=datetime(2026, 1, 1),
        npa_balance=100000.00,
        balance=200000.00,
        advance_purpose="Misc",
        npa_date=datetime(2025, 6, 1),
        asset_classification="Sub-standard",
        last_modified_user=employee.emp_id,
    )


@pytest.fixture
def securities(db, employee, customer):
    from preliminaryscreeningcommittee_review.models import SecuritiesTable

    return SecuritiesTable.objects.create(
        created_user=employee.emp_id,
        psc_id=customer,
        security_nature="Property",
        lan="LAN1",
        security_type="Mortgage",
        sanction_valuation=500000.00,
        sanction_valuation_date=datetime(2024, 1, 1),
        latest_valuation=600000.00,
        latest_valuation_date=datetime(2025, 12, 1),
        insurance_value=400000.00,
        cersai_num="CER1",
        last_modified_user=employee.emp_id,
    )


@pytest.fixture
def document(db, employee):
    from preliminaryscreeningcommittee_review.models import DocumentTable

    return DocumentTable.objects.create(
        created_user=employee.emp_id,
        section="S1",
        review_type="PSC",
        review_id="PSC123",
        app="preliminaryscreeningcommittee_review",
        file="data",
        file_name="a.pdf",
        file_type="pdf",
    )


@pytest.fixture
def psc_session_req(rf, db, config_data_dict, employee, branch):
    """Authenticated session request factory for PSC views."""
    from boss_admin.models import Session
    from django.contrib.messages.storage.fallback import FallbackStorage

    Session.objects.create(ses_key="PSC-SES")

    def _make(method="get", path="/", data=None, ajax=False, session_extra=None):
        m = method.lower()
        kw = {}
        if ajax:
            kw["HTTP_X_REQUESTED_WITH"] = "XMLHttpRequest"
        req = getattr(rf, m)(path, data or {}, **kw)
        sess = {
            "ses_key": "PSC-SES",
            "emp_id": employee.emp_id,
            "emp_name": employee.emp_name,
            "designation": "Officer",
            "branch_code": branch.branch_code,
            "branch_name": branch.branch_name,
            "config_data": dict(config_data_dict),
            "new_roles": "psc001maker1",
        }
        if session_extra:
            sess.update(session_extra)
        req.session = sess
        setattr(req, "_messages", FallbackStorage(req))
        return req

    return _make
