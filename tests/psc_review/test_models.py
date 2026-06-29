"""Tests for preliminaryscreeningcommittee_review/models.py."""
import datetime

import pytest

from preliminaryscreeningcommittee_review.models import (
    CreditFacilityTable,
    CustomerTable,
    DocumentTable,
    MOMTable,
    PSCTable,
    SACTable,
    SecuritiesTable,
)


class TestMOMTable:
    def test_create(self, mom):
        assert mom.id is not None
        assert mom.meeting_id == "MOM1"

    def test_db_table(self):
        assert MOMTable._meta.db_table == "mom_table"

    def test_int_dunder(self, mom):
        assert mom.__int__() == mom.id


class TestCustomerTable:
    def test_create(self, customer):
        assert customer.id is not None
        assert customer.cust_id == "CUST1"

    def test_unique_psc_rec_id(self, customer, db, employee, branch):
        with pytest.raises(Exception):
            CustomerTable.objects.create(
                created_user=employee.emp_id,
                psc_rec_id="PSC123",  # duplicate
                cust_id="CUST2",
                borrower_name="X",
                branch_code=branch,
                last_modified_user=employee.emp_id,
            )

    def test_db_table(self):
        assert CustomerTable._meta.db_table == "customer_table"


class TestPSCTable:
    def test_create(self, psc_record):
        assert psc_record.id is not None

    def test_db_table(self):
        assert PSCTable._meta.db_table == "psc_table"

    def test_int_dunder(self, psc_record):
        assert psc_record.__int__() == psc_record.id


class TestCreditFacilityTable:
    def test_create(self, credit_facility):
        assert credit_facility.id is not None

    def test_db_table(self):
        assert CreditFacilityTable._meta.db_table == "creditfacility_table"


class TestSecuritiesTable:
    def test_create(self, securities):
        assert securities.id is not None

    def test_db_table(self):
        assert SecuritiesTable._meta.db_table == "securities_table"


class TestSACTable:
    def test_create(self, sac_record):
        assert sac_record.id is not None

    def test_db_table(self):
        assert SACTable._meta.db_table == "sac_table"


class TestDocumentTable:
    def test_create(self, document):
        assert document.document_id is not None

    def test_db_table(self):
        assert DocumentTable._meta.db_table == "document_table"
