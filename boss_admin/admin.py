"""
admin
"""
from django.contrib import admin
import decimal, csv
from django.http import HttpResponse
from .models import BranchMaster, EmployeeMaster, RegistersMaster,\
    RegistersRoleMaster, EmployeeRegisterRoleMaster, \
    AuditorConnectionMaster, Session, Log, PhoneMaster, RuleSetup, BranchVerification, LocationMaster, DesignationMatrix


def export_branch_master_excel(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="branch_data.csv"'
    writer = csv.writer(response)
    writer.writerow(['Sr No', 'Branch Name', 'Branch Code', 'Status', 'Created By', 'Created Date'])
    books = queryset.values_list('sl_no', 'branch_name', 'branch_code', 'active', 'created_user', 'created_date')
    for book in books:
        writer.writerow(book)
    return response
    
export_branch_master_excel.short_description = 'Export to csv'

class BranchMasterAdmin(admin.ModelAdmin):
    """
    BranchMaster
    """
    list_display = ('sl_no', 'branch_name', 'branch_code', 'zone', 'active',
                    'created_user', 'created_date', 'modified_date')
    #display the columns in db for table
    search_fields = ['branch_name', 'branch_code']
    actions = [export_branch_master_excel]

admin.site.register(BranchMaster, BranchMasterAdmin)


def export_Employee_master_excel(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="Employee_data.csv"'
    writer = csv.writer(response)
    writer.writerow(['Sl_no', 'Employee Id', 'Emp Name', 'Domain Id','Designation',
                    'Email Id','Remarks', 'Branch Code', 'Status',
                    'Role', 'Created By', 'Created Date', 'Dtstmp'])
    books = queryset.values_list('sl_no', 'emp_id', 'emp_name', 'domain_id','designation',
                    'email_id','remarks', 'branch_code', 'active',
                    'role', 'created_user', 'created_date', 'modified_date')
    for book in books:
        writer.writerow(book)
    return response
    
export_Employee_master_excel.short_description = 'Export to csv'

class EmployeeMasterAdmin(admin.ModelAdmin):
    """
        EmployeeMasterAdmin
    """
    list_display = ('sl_no', 'emp_id', 'emp_name', 'pwd', 'domain_id','designation',
                    'email_id','remarks', 'branch_code', 'function', 'sub_function', 'job_role', 'active',
                    'role', 'created_user', 'created_date', 'modified_user', )

    # if you want django admin to show the search bar, just add this line
    search_fields = ['emp_id', 'emp_name', 'role']
    actions = [export_Employee_master_excel]

admin.site.register(EmployeeMaster, EmployeeMasterAdmin)

class RegistersMasterAdmin(admin.ModelAdmin):
    """
        RegistersMasterAdmin
    """
    list_display = ('sl_no', 'registers_code', 'registers_type',
                    'registers_desc','is_active')

admin.site.register(RegistersMaster, RegistersMasterAdmin)

class RegistersRoleMasterAdmin(admin.ModelAdmin):
    """
        RegistersRoleMasterAdmin
    """
    list_display = ('role_id', 'role_name', 'role_desc', 'registers_code','is_active')

admin.site.register(RegistersRoleMaster, RegistersRoleMasterAdmin)

def export_Employee_Role_Master_excel(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="Employee_Role_data.csv"'
    writer = csv.writer(response)
    writer.writerow(['Register Role Id', 'Employee Id', 'Register Code', 'Role Id','Assigner Id',
                    'Designation', 'Branch Code',
                     'Created Date', 'Status'])
    books = queryset.values_list('emp_reg_role_id', 'emp_id__domain_id', 'registers_code', 'role_id',
                    'created_user', 'designation',
                    'branch_code', 'created_date', 'is_active')
    for book in books:
        writer.writerow(book)
    return response

export_Employee_Role_Master_excel.short_description = 'Export to csv'

class EmployeeRegisterRoleMasterAdmin(admin.ModelAdmin):
    """
        EmployeeRegisterRoleMasterAdmin
    """
    list_display = ('emp_reg_role_id', 'emp_id', 'registers_code', 'role_id',
                    'created_user', 'designation',
                    'branch_code', 'modified_date', 'created_date', 'is_active')

    search_fields = [ 'emp_id__domain_id']
    actions = [export_Employee_Role_Master_excel]

admin.site.register(EmployeeRegisterRoleMaster, EmployeeRegisterRoleMasterAdmin)

class AuditorConnectionMasterAdmin(admin.ModelAdmin):
    """
        AuditorConnectionMasterAdmin
    """
    list_display = ('emp_reg_role_id', 'emp_id', 'registers_code', 'role_id',
                    'created_user', 'designation',
                    'branch_code', 'assigner_branch_code','modified_date',
                    'created_date', 'is_active')

admin.site.register(AuditorConnectionMaster, AuditorConnectionMasterAdmin)

class SessionAdmin(admin.ModelAdmin):
    """
        SessionAdmin
    """
    list_display = ('ses_id', 'ses_key', 'ses_data')
admin.site.register(Session, SessionAdmin)

class LogAdmin(admin.ModelAdmin):
    """
        LogAdmin
    """
    list_display=('log_id', 'emp_id', 'log_date','log_ip','in_out',
                  'ses_key','status')
admin.site.register(Log, LogAdmin)

class PhoneMasterAdmin(admin.ModelAdmin):
    """
        phoneModelAdminAdmin
    """
    
admin.site.register(PhoneMaster,  PhoneMasterAdmin)

class RuleSetupAdmin(admin.ModelAdmin):
    """
        RuleSetupAdmin
    """
    list_display = ('register', 'rule_type', 'rule_data','modified_date')

    search_fields = [ 'register','rule_type','rule_data']

admin.site.register(RuleSetup, RuleSetupAdmin)

class BranchVerificationAdmin(admin.ModelAdmin):
    """
        BranchVerificationAdmin
    """
    list_display = ('branch_code', 'start_date', 'end_date','modified_date')

    search_fields = [ 'start_date','end_date']

admin.site.register(BranchVerification, BranchVerificationAdmin)

class LocationMasterAdmin(admin.ModelAdmin):
    """
        ComplaintsRegistersAdmin
    """
    fields = ('location_code','address','city','pin_code','latittude','longitude','building','floor','room')
    list_display = ('id','location_code','address','city','pin_code','latittude','longitude','building','floor','room')
    search_fields = ['location_code']
admin.site.register(LocationMaster, LocationMasterAdmin)

class DesignationMatrixAdmin(admin.ModelAdmin):
    """
        DesignationMatrixAdmin
    """
    list_display = ('id','created_date','role_type','role_name','role_code','designations','last_modified_user','last_modified_date','is_active','role_dept')
    search_fields = ['designations','role_type','role_name','role_code','role_dept']
admin.site.register(DesignationMatrix, DesignationMatrixAdmin)