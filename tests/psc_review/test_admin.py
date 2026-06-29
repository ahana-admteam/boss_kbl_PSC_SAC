"""Tests for preliminaryscreeningcommittee_review/admin.py."""
import importlib

from django.contrib import admin


class TestAdminRegistrations:
    def test_admin_module_registers_models(self):
        importlib.import_module(
            "preliminaryscreeningcommittee_review.admin"
        )
        from preliminaryscreeningcommittee_review.models import (
            CreditFacilityTable,
            CustomerTable,
            DocumentTable,
            MOMTable,
            PSCTable,
            SACTable,
            SecuritiesTable,
        )

        for model in (
            CustomerTable,
            PSCTable,
            SACTable,
            MOMTable,
            CreditFacilityTable,
            SecuritiesTable,
            DocumentTable,
        ):
            assert model in admin.site._registry

    def test_psc_admin_list_display(self):
        from preliminaryscreeningcommittee_review.admin import PSCTableAdmin

        assert "psc_rec_id" in PSCTableAdmin.list_display

    def test_sac_admin_list_display(self):
        from preliminaryscreeningcommittee_review.admin import SACTableAdmin

        assert "sac_rec_id" in SACTableAdmin.list_display

    def test_customer_admin_list_display(self):
        from preliminaryscreeningcommittee_review.admin import (
            CustomerTableAdmin,
        )

        assert "cust_id" in CustomerTableAdmin.list_display
