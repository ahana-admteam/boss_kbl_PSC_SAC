"""Tests for boss_admin/models.py."""
import datetime

import pytest

from boss_admin.models import (
    AuditorConnectionMaster,
    BranchMaster,
    BranchVerification,
    DesignationMatrix,
    EmployeeMaster,
    EmployeeRegisterRoleMaster,
    Log,
    LocationMaster,
    PhoneMaster,
    PropertyDocuments,
    RegistersMaster,
    RegistersRoleMaster,
    RuleSetup,
    Session,
)


class TestBranchMaster:
    def test_str_returns_branch_code(self, db, branch):
        assert str(branch) == "BR001"

    def test_from_500_with_no_records(self, db):
        BranchMaster.objects.all().delete()
        assert BranchMaster.from_500() == 1

    def test_from_500_increments_largest(self, db, branch, ro_branch):
        # branch.sl_no = 1, ro_branch.sl_no = 2
        assert BranchMaster.from_500() == 3

    def test_meta_db_table(self):
        assert BranchMaster._meta.db_table == "branch_master"

    def test_meta_ordering(self):
        assert BranchMaster._meta.ordering == ["sl_no"]


class TestEmployeeMaster:
    def test_str_returns_domain_id(self, db, employee):
        assert str(employee) == "test_user"

    def test_from_500_no_records(self, db):
        EmployeeMaster.objects.all().delete()
        assert EmployeeMaster.from_500() == 1

    def test_from_500_increments(self, db, employee, branch):
        EmployeeMaster.objects.create(
            sl_no=5,
            domain_id="u2",
            emp_id="EMP002",
            emp_name="x",
            pwd="p",
            branch_code=branch,
            branch_id=branch,
        )
        assert EmployeeMaster.from_500() == 6

    def test_meta_db_table(self):
        assert EmployeeMaster._meta.db_table == "employee_master"


class TestRegistersMaster:
    def test_str_returns_registers_code(self, db, register_master):
        assert str(register_master) == "PSC001"

    def test_from_500_no_records(self, db):
        RegistersMaster.objects.all().delete()
        assert RegistersMaster.from_500() == 1

    def test_from_500_increments(self, db, register_master):
        # register_master.sl_no=1
        assert RegistersMaster.from_500() == 2


class TestRegistersRoleMaster:
    def test_str_returns_role_name(self, db, register_role):
        assert str(register_role) == "PSC BO Maker"

    def test_meta_db_table(self):
        assert RegistersRoleMaster._meta.db_table == "registers_role_master"


class TestEmployeeRegisterRoleMaster:
    def test_create_works(self, db, emp_register_role):
        assert emp_register_role.pk is not None

    def test_meta_db_table(self):
        assert (
            EmployeeRegisterRoleMaster._meta.db_table
            == "employee_register_role_master"
        )


class TestAuditorConnectionMaster:
    def test_meta_db_table(self):
        assert (
            AuditorConnectionMaster._meta.db_table == "auditor_connection_master"
        )


class TestSession:
    def test_meta_db_table(self):
        assert Session._meta.db_table == "session_data"

    def test_create(self, db):
        s = Session.objects.create(ses_key="K", ses_data="D")
        assert s.ses_id is not None


class TestLog:
    def test_create(self, db, employee):
        l = Log.objects.create(emp_id=employee, status="Login")
        assert l.log_id is not None

    def test_meta_db_table(self):
        assert Log._meta.db_table == "log_data"


class TestPhoneMaster:
    def test_str_returns_mobile_as_string(self, db):
        p = PhoneMaster.objects.create(Mobile=9991112222)
        assert str(p) == "9991112222"

    def test_meta_db_table(self):
        assert PhoneMaster._meta.db_table == "phone_master"

    def test_defaults(self, db):
        p = PhoneMaster.objects.create(Mobile=1)
        assert p.isVerified is False
        assert p.counter == 0


class TestRuleSetup:
    def test_str_returns_register(self, db, employee):
        r = RuleSetup.objects.create(
            register="REG1",
            rule_type="auto",
            rule_data={"x": 1},
            created_user=employee,
            modified_user=employee,
        )
        assert str(r) == "REG1"

    def test_meta_db_table(self):
        assert RuleSetup._meta.db_table == "rule_setup_table"


class TestBranchVerification:
    def test_str_returns_start_date(self, db, branch, employee):
        b = BranchVerification.objects.create(
            branch_code=branch,
            start_date=datetime.date(2026, 1, 1),
            end_date=datetime.date(2026, 12, 31),
            created_user=employee,
            modified_user=employee,
        )
        assert str(b) == "2026-01-01"


class TestPropertyDocuments:
    def test_str_returns_packet_id(self, db):
        p = PropertyDocuments.objects.create(packet_id="PK01")
        assert str(p) == "PK01"

    def test_meta_db_table(self):
        assert PropertyDocuments._meta.db_table == "property_document_table"


class TestLocationMaster:
    def test_str_returns_id_as_str(self, db, branch):
        loc = LocationMaster.objects.create(
            location_code=branch, city="X", pin_code="123"
        )
        assert str(loc) == str(loc.id)


class TestDesignationMatrix:
    def test_str_returns_id(self, db):
        d = DesignationMatrix.objects.create(
            role_type="Head",
            role_name="HO",
            role_code="HO_M",
            role_dept="Cred",
            designations=["Officer"],
            is_active=True,
        )
        assert str(d) == str(d.id)

    def test_meta_db_table(self):
        assert DesignationMatrix._meta.db_table == "designation_matrix"
