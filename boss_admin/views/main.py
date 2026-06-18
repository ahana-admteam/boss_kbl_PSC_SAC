"""
import , view page
"""
from datetime import datetime
from django.http import HttpResponse,JsonResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import FileSystemStorage
from django.conf import settings
import os
from django.utils.decorators import method_decorator
from boss_admin.dbutil import generate_session_ses_key, get_ip_address, con_current_login,ad_login_test, fixed_asset_title
from boss_admin.models import  Session, Log
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from boss_admin.dbutil import fixed_asset_title
import ldap3
from tablib import Dataset
from .authentication import my_login_required
from box import Box
from boss_admin.models import BranchMaster, EmployeeMaster
import csv
from django.db.models import Q
import tablib
from tablib import Dataset
import pandas as pd
from datetime import date, timedelta, datetime
from boss_admin.file_upload import fileUpload
from .kbl_api import KBLAPIWrapper as kApi
import json
# from tenants.utilities import get_tenant


@my_login_required
def log_out(request):
    """
    log_out
    :param request:
    :return:
    """
    try:
        # print('logout function')
        #make roles and roles == 0
        request.session['roles'] = 0
        request.session['roles1'] = 0
        #make Login status to Logout
        Log.objects.filter(emp_id=request.session['emp_id'],
                           ses_key=request.session['ses_key']).update(in_out=datetime.now(),
                                                                      status='Logout')
        #delete ses_key
        session_del = Session.objects.filter(ses_key=request.session['ses_key'])
        session_del.delete()
        #######################
        # New code
        request.session.flush()
        del request.session['emp_id']

        return redirect('login_page')
    except:
        # raise
        return redirect('login_page')


# def documents_manage(request):
#     config_data = Box(request.session['config_data'])
#     tenant = config_data.tenant
#     title = config_data.module.AD001.display_name.document_movement
#     tenant_image = config_data.logo_image.image_path
#     doc_list = PropertyDocuments.objects.values('id','date','source_branch__branch_name','status','destination_branch__branch_code','source_branch__branch_code',
#         'destination_branch__branch_name','sender__emp_name','sender__emp_id','mail_type','remarks','packet_contents').order_by('status','-date')
#     return render(request, 'boss_admin/documents_manage.html', context={'mail_list':doc_list, 'title':title,'tenant_image': tenant_image, "tenant":tenant})


# def documents_verify(request):
#     if request.is_ajax() and request.method == 'POST':
#         id = request.POST['req_id']
#         ho_remarks = request.POST['remarks']
#         PropertyDocuments.objects.filter(id=id).update(status='Verified',ho_remarks=ho_remarks)
#         messages.success(request, 'Verified Succesfully')
#         return HttpResponse('Success')


# add_branch export view
@my_login_required
def add_branch_export_view(request):
    if request.method == "POST":
        fromdate = request.POST['export_fromdate']
        todate = request.POST['export_todate']
        table_name = BranchMaster   
        
        data = generic_export(request,table_name,fromdate,todate)
        if data:
            return data
        else:
            return redirect('add_branch')
    else:
        print('invalid')

# add_employee export view
@my_login_required
def add_employee_export_view(request):
    if request.method == "POST":
        fromdate = request.POST['export_fromdate']
        todate = request.POST['export_todate']
        table_name = EmployeeMaster   
        
        data = generic_export(request,table_name,fromdate,todate)
        if data:
            return data
        else:
            return redirect('add_employee')
    else:
        print('invalid')

# generic export function

def generic_export(request,table_name,fromdate,todate):
    if fromdate and todate:
        dto = datetime.strptime(todate, '%Y-%m-%d').date()
        todate = dto + timedelta(days=1)
        data = list(table_name.objects.filter(created_date__range=[fromdate, todate]).values())
    else:
        data = list(table_name.objects.values())
   
    df = pd.DataFrame.from_records(data)
    excel_data = df.to_csv(r'export.csv', header=True, index=False, encoding='utf-8')
    
    with open("export.csv", "rb") as excel:
        file_data = excel.read()
        response = HttpResponse(file_data, content_type='application/ms-excel/csv')
        response['Content-Disposition'] = 'attachment; filename=' + table_name.__name__ + '.csv'
        return response

# def generic_file_upload(request):
#     try:
#         if request.method == "POST":
#             request_file = request.FILES['file'] if 'file' in request.FILES else None
#             if request_file:
#                 uploaded_app_name = request.POST.get('app_name')
#                 uploaded_section_name = request.POST.get('section_name')
#                 file_name = request_file.name

#                 fs = FileSystemStorage()
#                 file = fs.save(file_name, request_file)
#                 fileurl = fs.url(file)
#                 print(fileurl)
#         return HttpResponse("File uploaded.")
#     except Exception as e:
#         return HttpResponse(e)

from django.http import JsonResponse


def Document_delete(request):
    if request.is_ajax() and request.method == "POST":
        id = request.POST['file_id']
        file_data_val = fileUpload.file_upload.delete_documents(id)
        return HttpResponse({'file_data': file_data_val})


def Document_view(request):
    # print('doc view')
    if request.is_ajax() and request.method == "GET":
        id = request.GET['document_id']
        file_data_val = fileUpload.file_upload.get_single_document(id)
        # print('file_data_val',file_data_val)
        return JsonResponse({'file_data': file_data_val})

@my_login_required
def api_check(request):
    try:
        #print('api_check')
        config_data = Box(request.session['config_data'])
        tenant = config_data.tenant
        display_name = config_data.module
        tenant_image = config_data.logo_image.image_path
        title = "API/CRON Check"
        if request.is_ajax() and request.method == "POST":
            requestData = request.POST['requestData']
            apiType = request.POST['apiType']
            if apiType == 'HUPMINQ':
                responseData = kApi.EmpDataAPI(requestData)
                jsonResponseData = json.dumps(responseData)
            elif apiType == 'Dashboard':
                responseData = kApi.PSCDashboardAPI(requestData)
                jsonResponseData = json.dumps(responseData)
            elif apiType == 'Branch':
                #print("branch")
                responseData = kApi.BranchDataAPI()
                jsonResponseData = json.dumps(responseData)
            elif apiType ==  'PSC':
                responseData = kApi.NPAStatusAPI(requestData)
                jsonResponseData = json.dumps(responseData)
            elif apiType == 'CustomerAssets':
                responseData = kApi.CustomerAssetsAPI(requestData)
                jsonResponseData = json.dumps(responseData)
            elif apiType == 'DashboardCRON':
                # responseData = kApi.PSCDashboardAPI(requestData)
                jsonResponseData = 'Dashboard CRON'
            elif apiType == 'BranchCRON':
                # responseData = kApi.BranchDataAPI()
                jsonResponseData = 'Branch CRON'
            elif apiType ==  'PSC_CRON':
                # responseData = kApi.NPAStatusAPI(requestData)
                jsonResponseData = 'PSC CRON'
            else:
                responseData = 'Invalid'
            return JsonResponse({'responseData': jsonResponseData,"api":apiType})
        else:
            context = {'tenant_image': tenant_image, "tenant":tenant, "display_name":display_name, 'title':title}
            return render(request, 'boss_admin/assign_role_page/api_check.html', context)
    except Exception as e:
        print(e)
