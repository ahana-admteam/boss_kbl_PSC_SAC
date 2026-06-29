"""Tests for boss_admin/admin.py."""
import csv
import io

import pytest


class TestAdminRegistrations:
    """Importing boss_admin.admin should register many models."""

    def test_models_registered(self):
        from django.contrib import admin
        from boss_admin.models import (
            BranchMaster,
            BranchVerification,
            DesignationMatrix,
            EmployeeMaster,
            EmployeeRegisterRoleMaster,
            LocationMaster,
            Log,
            PhoneMaster,
            RegistersMaster,
            RegistersRoleMaster,
            RuleSetup,
            Session,
            AuditorConnectionMaster,
        )
        # Forces import
        import boss_admin.admin  # noqa: F401

        for model in (
            BranchMaster,
            EmployeeMaster,
            RegistersMaster,
            RegistersRoleMaster,
            EmployeeRegisterRoleMaster,
            AuditorConnectionMaster,
            Session,
            Log,
            PhoneMaster,
            RuleSetup,
            BranchVerification,
            LocationMaster,
            DesignationMatrix,
        ):
            assert model in admin.site._registry


class TestExportActions:
    def test_export_branch_master_excel(self, db, branch, ro_branch):
        from boss_admin.admin import export_branch_master_excel
        from boss_admin.models import BranchMaster

        qs = BranchMaster.objects.all()
        response = export_branch_master_excel(None, None, qs)
        assert response["Content-Type"] == "text/csv"
        assert (
            'attachment; filename="branch_data.csv"'
            in response["Content-Disposition"]
        )
        rows = list(csv.reader(io.StringIO(response.content.decode())))
        assert rows[0] == [
            "Sr No",
            "Branch Name",
            "Branch Code",
            "Status",
            "Created By",
            "Created Date",
        ]
        # 2 branches + header
        assert len(rows) == 3

    def test_export_employee_master_excel(self, db, employee):
        from boss_admin.admin import export_Employee_master_excel
        from boss_admin.models import EmployeeMaster

        qs = EmployeeMaster.objects.all()
        response = export_Employee_master_excel(None, None, qs)
        assert (
            'attachment; filename="Employee_data.csv"'
            in response["Content-Disposition"]
        )
        rows = list(csv.reader(io.StringIO(response.content.decode())))
        assert "Employee Id" in rows[0]
        assert len(rows) == 2  # header + 1 emp

    def test_export_employee_role_master_excel(
        self, db, emp_register_role
    ):
        from boss_admin.admin import export_Employee_Role_Master_excel
        from boss_admin.models import EmployeeRegisterRoleMaster

        qs = EmployeeRegisterRoleMaster.objects.all()
        response = export_Employee_Role_Master_excel(None, None, qs)
        assert (
            'attachment; filename="Employee_Role_data.csv"'
            in response["Content-Disposition"]
        )

    def test_export_short_descriptions(self):
        from boss_admin import admin as a

        assert a.export_branch_master_excel.short_description == "Export to csv"
        assert (
            a.export_Employee_master_excel.short_description == "Export to csv"
        )
        assert (
            a.export_Employee_Role_Master_excel.short_description
            == "Export to csv"
        )


class TestAdminListDisplays:
    def test_branch_admin_list_display(self):
        from boss_admin.admin import BranchMasterAdmin

        assert "branch_code" in BranchMasterAdmin.list_display
        assert "active" in BranchMasterAdmin.list_display

    def test_employee_admin_search_fields(self):
        from boss_admin.admin import EmployeeMasterAdmin

        assert "emp_id" in EmployeeMasterAdmin.search_fields
