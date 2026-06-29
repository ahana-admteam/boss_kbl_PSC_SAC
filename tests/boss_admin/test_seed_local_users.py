"""Tests for boss_admin management command seed_local_users."""
import io

import pytest


@pytest.mark.django_db
class TestSeedLocalUsers:
    def test_creates_branches_register_and_users(self):
        from django.core.management import call_command
        from boss_admin.models import (
            BranchMaster,
            EmployeeMaster,
            RegistersMaster,
            RegistersRoleMaster,
            EmployeeRegisterRoleMaster,
        )

        buf = io.StringIO()
        call_command("seed_local_users", stdout=buf)

        assert BranchMaster.objects.filter(branch_code="BR001").exists()
        assert BranchMaster.objects.filter(branch_code="BR002").exists()
        assert BranchMaster.objects.filter(branch_code="BR003").exists()
        assert RegistersMaster.objects.filter(registers_code="PSC001").exists()
        assert RegistersRoleMaster.objects.filter(
            role_desc="psc001maker1"
        ).exists()
        assert EmployeeMaster.objects.filter(domain_id="psc_bo_maker").exists()
        assert EmployeeMaster.objects.filter(domain_id="convener").exists()
        # Role assignments exist
        assert EmployeeRegisterRoleMaster.objects.count() >= 1

    def test_idempotent(self):
        """Running twice does not produce duplicates."""
        from django.core.management import call_command
        from boss_admin.models import EmployeeMaster

        call_command("seed_local_users", stdout=io.StringIO())
        first_count = EmployeeMaster.objects.count()
        call_command("seed_local_users", stdout=io.StringIO())
        second_count = EmployeeMaster.objects.count()
        assert first_count == second_count

    def test_updates_password_on_existing_user(self):
        from django.core.management import call_command
        from boss_admin.models import EmployeeMaster

        call_command("seed_local_users", stdout=io.StringIO())
        emp = EmployeeMaster.objects.get(domain_id="psc_bo_maker")
        emp.pwd = "different"
        emp.save()

        call_command("seed_local_users", stdout=io.StringIO())
        emp.refresh_from_db()
        assert emp.pwd == "test123"
