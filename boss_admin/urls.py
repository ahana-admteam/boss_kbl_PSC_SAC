"""
urls
"""
from django.urls import path

from .views import main, authentication, roles_manage, kbl_reports, kbl_auth


urlpatterns = [
    #### Authentication URLs ########
    path('', authentication.login, name='login_page'),
    path('home', authentication.home_page, name='home_page'),
    path('file_encrypt', authentication.file_encrypt, name='file_encrypt'),
    
    #### Role Management URLs ########
    path('role_assign', roles_manage.get_registers_list, name='role_assign_page'),
    path('add_role', roles_manage.add_role, name='add_role'),
    path('app_admin', roles_manage.app_admin, name='app_admin'),
    path('add_branch_admin',roles_manage.add_branch_admin,name='add_branch_admin'),
    path('select_auditor', roles_manage.select_auditor, name='select_auditor'),
    path('add_auditor', roles_manage.add_auditor, name='add_auditor'),
    path('delete', roles_manage.delete_roles, name='delete_roles'),
    path('auditor_delete', roles_manage.delete_auditor_role, name='delete_auditor_role'),
    path('admin_func', roles_manage.admin_func, name='admin_func'),

    ###Branch & User Management
    path('add_branch', roles_manage.add_branch, name='add_branch'),
    path('add_branch_ajax/', roles_manage.add_branch_ajax, name='add_branch_ajax'),
    path('add_employee', roles_manage.add_employee, name='add_employee'),
    path('branch_upload_new', roles_manage.branch_upload_new, name ='branch_upload_new'),
    path('employee_upload_new', roles_manage.employee_upload_new, name ='employee_upload_new'),
    path('add_employee_ajax/', roles_manage.add_employee_ajax, name='add_employee_ajax'),
    path('branch_data_search', roles_manage.branch_data_search, name='branch_data_search'),
    path('employee_data_search', roles_manage.employee_data_search, name='employee_data_search'),
    path('emp_data_export', roles_manage.emp_data_export, name='emp_data_export'),
    path('branch_data_export', roles_manage.branch_data_export, name='branch_data_export'),
    path('delete_branch/', roles_manage.delete_branch, name='delete_branch'),
    path('delete_employee/', roles_manage.delete_employee, name='delete_employee'),
    path('transfer_employee/', roles_manage.transfer_employee, name='transfer_employee'),
    path('upload_err_logs_export', roles_manage.upload_err_logs_export, name='upload_err_logs_export'),
  
    path('logout', main.log_out, name='log_out'), #registration page

    # generic export function url
    path('generic_export', main.generic_export, name='generic_export'),

    # add_branch export
    path("add_branch_export/", main.add_branch_export_view, name='add_branch_export'),
    # add_employee export
    path("add_employee_export/", main.add_employee_export_view, name='add_employee_export'),

    #Cash Management
    path('viewfile/', main.Document_view, name='Document_view'),
    path('deletefile/', main.Document_delete, name='Document_delete'),

    #Designation  Matrix
    path('designation_matrix', roles_manage.designation_matrix, name='designation_matrix'),
    path('edit_designationmatrix', roles_manage.edit_designationmatrix, name='edit_designationmatrix'),
    path('edit_designationmatrix/<int:pk>', roles_manage.edit_designationmatrix, name='edit_designationmatrix'),

    #KBL Reports
    path('kbl_reports', kbl_reports.kbl_reports, name='kbl_reports'),
    path('kbl_report', kbl_reports.kbl_report, name='kbl_report'),
    path('kbl_report/<str:val>', kbl_reports.kbl_report, name='kbl_report'),
    path('download_excel_A', kbl_reports.download_excel_A, name='download_excel_A'),
    path('download_excel_B', kbl_reports.download_excel_B, name='download_excel_B'),

    #API Check
    path('api_check', main.api_check, name='api_check')

]