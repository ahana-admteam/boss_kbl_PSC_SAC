from django.contrib import admin
from .models import *

class CustomerTableAdmin(admin.ModelAdmin):
    """
        CustomerTableAdmin
    """
    list_display = ('id','creation_date','created_user','psc_rec_id','cust_id','borrower_name','branch_code','total_exposure','acc_count','current_role','status','last_modified_date','last_modified_user')
    search_fields = ['id','psc_rec_id','cust_id','borrower_name','branch_code','total_exposure','acc_count','current_role','status']
    
admin.site.register(CustomerTable, CustomerTableAdmin)


class PSCTableAdmin(admin.ModelAdmin):
    """
        PSCTableAdmin
    """
    list_display = ('id', 'psc_rec_id', 'branch_code', 'region_name', 'cust_id', 'npa_date', 'nap_tag', 'npa_status',
                    'status',  'npa_reasons', 'ob_branch_head', 'ob_regional_head', 'ob_dept_head',  'mom_lapse', 'current_role')
    search_fields = ['id', 'psc_rec_id', 'region_name',
                     'status', 'current_role', 'mom_id', 'borrower_name']


admin.site.register(PSCTable, PSCTableAdmin)


class SACTableAdmin(admin.ModelAdmin):
    """
        SACTableAdmin
    """
    list_display = ('id', 'psc_rec_id', 'sac_rec_id', 'emp_name', 'staff_no', 'present_designation',
                    'present_working', 'status', 'psc_date',  'mom_lapse', 'current_role')
    search_fields = ['id', 'sac_rec_id',  'status', 'current_role', 'mom_id']


admin.site.register(SACTable, SACTableAdmin)


class MOMTableAdmin(admin.ModelAdmin):
    """
        MOMTableAdmin
    """
    list_display = ('id', 'created_user', 'meeting_id', 'mom_date', 'mom_closure_date',
                    'active', 'last_modified_date', 'last_modified_user', 'review_type')
    search_fields = ['id', 'created_user', 'meeting_id', 'mom_date', 'audience',
                     'active', 'last_modified_date', 'last_modified_user', 'review_type']


admin.site.register(MOMTable, MOMTableAdmin)


class CreditFacilityTableAdmin(admin.ModelAdmin):
    """
        CreditFacilityTableAdmin
    """
    list_display = ('id', 'psc_id', 'npa_balance', 'balance', 'advance_purpose',
                    'npa_date', 'last_modified_date', 'last_modified_user')
    search_fields = ['id', 'psc_id', 'credit_feci_slno', 'reference_num',
                     'account_nature',  'lan', 'sanctioned_limit', 'last_modified_user']


admin.site.register(CreditFacilityTable, CreditFacilityTableAdmin)


class SecuritiesTableAdmin(admin.ModelAdmin):
    """
        SecuritiesTableAdmin
    """
    list_display = ('id', 'psc_id', 'security_nature', 'lan', 'security_type',
                    'cersai_num', 'last_modified_date', 'last_modified_user')
    search_fields = ['id', 'psc_id', 'security_nature', 'lan',
                     'security_type', 'cersai_num', 'last_modified_user']


admin.site.register(SecuritiesTable, SecuritiesTableAdmin)


class DocumentTableAdmin(admin.ModelAdmin):
    """
        DocumentTableAdmin
    """
    list_display = ('document_id', 'created_user', 'section', 'review_type', 'review_id',
                    'app', 'file_name', 'file_type', 'last_modified_date', 'last_modified_user')
    search_fields = ['document_id', 'created_user', 'section', 'review_type', 'review_id',
                     'app', 'file_name', 'file_type', 'last_modified_date', 'last_modified_user']


admin.site.register(DocumentTable, DocumentTableAdmin)
