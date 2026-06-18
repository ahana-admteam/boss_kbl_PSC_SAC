from django.shortcuts import render
from distutils.command.config import config
import datetime
from boss_admin.file_upload import fileUpload
from django.core.paginator import Paginator
from datetime import date, timedelta, datetime
from django.contrib import messages
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from boss_admin.views import my_login_required
from boss_admin.models import EmployeeMaster, BranchMaster, RegistersMaster, RegistersRoleMaster, EmployeeRegisterRoleMaster
from boss_v1.boss_log import screeningcommittee_logging as sc_log
from box import Box
from boss_admin.views.main import generic_export
from boss_admin.views.authentication import my_login_required
from pathlib import Path
from notifications_app.models import Notification
from notifications_app.utilities import create_notification
import json
from django.http import JsonResponse
from ..models import *
from . import psc_views
from django.db.models import Count
import pandas as pd
from boss_admin.models import BranchMaster, DesignationMatrix

app_name = 'preliminaryscreeningcommittee_review'


@my_login_required
def sac_review(request,pk):
    """
    welcome
    :param request:
    :return:
    """
    config_data = Box(request.session['config_data'])
    tenant = config_data.tenant
    title = config_data.module.PSC001.sac_display_name
    tenant_image = config_data.logo_image.image_path
    file_extension = config_data.file_extension
    ynstatus = config_data.module.PSC001.ynstatus
    drop_values = []
    roles= request.session['new_roles'].split("_")
    for k, v in file_extension.items():
        drop_values.append(v)
    drop_values = tuple(drop_values)
    branch_data = BranchMaster.objects.filter(
        branch_code=request.session['branch_code']).values('branch_name', 'zone')
    emp_list = list(EmployeeRegisterRoleMaster.objects.filter(
        role_id__role_desc='psc001maker1').values_list('emp_id', flat=True))
    empData = EmployeeMaster.objects.filter(active=True, emp_id__in=emp_list).order_by('emp_name').exclude(
        emp_name="").exclude(emp_id=request.session['emp_id']).values('emp_id', 'emp_name', 'branch_code__zone', 'branch_code')
    datadisable = ''
    # print(branch)
    try:
        if request.is_ajax() and request.method == 'POST':
            # json
            json_basicdetails = json.loads(request.POST['json_basicdetails'])
            json_creditsanction = json.loads(request.POST['json_creditsanction'])
            json_fraud_element = json.loads(request.POST['json_fraud_element'])
            addr_lett_date = request.POST['addr_lett_date']
            json_reply_date = json.loads(request.POST['json_reply_date'])
            rep_auth_remarks = request.POST['rep_auth_remarks']
            ob_regional_head = request.POST['ob_regional_head']
            ob_dept_head = request.POST['ob_dept_head']
            files = request.POST['file_values']
            status = request.POST.get('status')
            session_role = DesignationMatrix.objects.filter(role_code=request.session['new_roles']).values('role_name')[0]['role_name']
            json_reject_remarks_data = json.loads(request.POST['json_reject_remarks_data'])
            json_reject_remarks_div = None
            sac_review_data = [{"basic_details":json_basicdetails},{"credit_sanction":json_creditsanction},{"fraud_element":json_fraud_element},{"addr_lett_date":addr_lett_date},{"reply_date":json_reply_date},{"rep_auth_remarks":rep_auth_remarks},{"ob_regional_head":ob_regional_head},{"ob_dept_head":ob_dept_head},{'pk':pk},{'files':files},{'role_value':'edit2'},{'status':status},{'reject_remarks':json_reject_remarks_data},{'reject_remarks_div':json_reject_remarks_div}]
            ss = psc_views.SavetoDB.sac_db_store(request ,sac_review_data)
            # print('ss',ss)
            if ss.status_code == 200:
            # if (len(files) > 0):        
            #         files_values = json.loads(files)
            #         # print(files_values,"filed documents")
            #         fileUpload.file_upload.insert_documents(
            #                     'SAC', 'SAC300831027002',files_values, request.session['emp_id'])
                if status == 'Draft':
                    print("User Id: {}, Designation: {}, Role: {}, Action: {}, Message: {}".format(request.session['emp_id'], request.session['designation'], session_role, "SAC Review Form", "SAC review Form Drafted ID-"+json_basicdetails[0]['sac_no']))
                    messages.success(request, "SAC form with SAC No %s saved as draft." %json_basicdetails[0]['sac_no'])
                elif status == 'Submitted':
                    print("User Id: {}, Designation: {}, Role: {}, Action: {}, Message: {}".format(request.session['emp_id'], request.session['designation'], session_role, "SAC Review Form", "SAC review Form Submitted ID-"+json_basicdetails[0]['sac_no']))
                    messages.success(request, "SAC form with SAC No %s submitted successfully" %json_basicdetails[0]['sac_no'])
                elif status == 'Rejected':
                    print("User Id: {}, Designation: {}, Role: {}, Action: {}, Message: {}".format(request.session['emp_id'], request.session['designation'], session_role, "SAC Review Form", "SAC review Form Rejected ID-"+json_basicdetails[0]['sac_no']))
                    messages.success(request,'SAC form with SAC No %s rejected successfully' %json_basicdetails[0]['sac_no'])
                elif status == 'Approved':
                    print("User Id: {}, Designation: {}, Role: {}, Action: {}, Message: {}".format(request.session['emp_id'], request.session['designation'], session_role, "SAC Review Form", "SAC review Form Approved ID-"+json_basicdetails[0]['sac_no']))
                    messages.success(request,'SAC form with SAC No %s approved successfully' %json_basicdetails[0]['sac_no'])
                return HttpResponse("success")
            else:
                messages.error(request,'error code %s' %ss)
                return HttpResponse("error")
        else:
            sac_data = list(SACTable.objects.filter(psc_rec_id__npa_status=True,id=pk).values(*psc_views.sac_all_data))
            psc__id = sac_data[0]['psc_rec_id']
            psc__i = sac_data[0]['psc_rec_id__cust_id']
            psc__cid = CustomerTable.objects.filter(cust_id=psc__i).values('id')[0]['id']
            sac_data_updated = CustomerTable.objects.filter(cust_id=psc__i).values('lapses_details')[0]['lapses_details']
            sac_staff_no = sac_data_updated["records"][0]['staff_no']
            sac_staff_name = sac_data_updated["records"][0]['staff_name']
            sac_staff_branch_code = sac_data_updated["records"][0]['staff_branch_code']
            sac_staff_designation = sac_data_updated["records"][0]['staff_designation']
            sac_staff_lapses_details = sac_data_updated["records"][0]['staff_lapses_details']
            staff_accountability = PSCTable.objects.filter(id=psc__id).values('staff_accountability')[0]['staff_accountability']
            psc_rec_id = PSCTable.objects.filter(id=psc__id).values('psc_rec_id')[0]['psc_rec_id']
            all_aod = staff_accountability['all_aod']
            file_data = fileUpload.file_upload.get_all_documents("preliminaryscreeningcommittee_review", psc_rec_id)
            section_data = list(item['section'] for item in file_data)
            # print("all_aod",all_aod)
            # print("sac_staff_nos", sac_staff_nos)
            mom_lapses_data = PSCTable.objects.filter(id=psc__id).values('mom_lapse_desc')[0]['mom_lapse_desc']
            #print('psc__cid',psc__cid)
            if 'psc001checker1' in roles:
                datadisable = 'checker'
            creditsanctiontable_data = CreditFacilityTable.objects.filter(psc_id=psc__cid).values(*psc_views.creditsanction_all_data)
            securitiestable_data = SecuritiesTable.objects.filter(psc_id=psc__cid).values(*psc_views.securities_all_data)
            #print('creditsanctiontable_data',creditsanctiontable_data,psc__cid)
            context = {'title': title, 'tenant_image': tenant_image,'sac_data':sac_data, 
            "sac_staff_no":sac_staff_no,"sac_staff_name":sac_staff_name,"sac_staff_branch_code":sac_staff_branch_code,"sac_staff_designation":sac_staff_designation,"sac_staff_lapses_details":sac_staff_lapses_details,
                        "tenant": tenant, "branch_data": branch_data,"ynstatus":ynstatus,'datadisable':datadisable,'mom_lapses_data':mom_lapses_data,"all_aod":all_aod,"section_data":section_data,'creditsanctiontable_data':creditsanctiontable_data,'securitiestable_data':securitiestable_data}
            return render(request, 'preliminaryscreeningcommittee_review/sac_review.html', context=context)
    except Exception as e:
        # sc_log.error(str(e))
        print('sac error',e)
        return redirect('sac_review')

@my_login_required
def sac_update(request,pk,val):
    """
    welcome
    :param request:
    :return:
    """
    config_data = Box(request.session['config_data'])
    tenant = config_data.tenant
    title = config_data.module.PSC001.sac_display_name
    tenant_image = config_data.logo_image.image_path
    file_extension = config_data.file_extension
    ynstatus = config_data.module.PSC001.ynstatus
    drop_values = []
    for k, v in file_extension.items():
        drop_values.append(v)
    drop_values = tuple(drop_values)
    branch_data = BranchMaster.objects.filter(
        branch_code=request.session['branch_code']).values('branch_name', 'zone')
    emp_list = list(EmployeeRegisterRoleMaster.objects.filter(
        role_id__role_desc='psc001maker1').values_list('emp_id', flat=True))
    empData = EmployeeMaster.objects.filter(active=True, emp_id__in=emp_list).order_by('emp_name').exclude(
        emp_name="").exclude(emp_id=request.session['emp_id']).values('emp_id', 'emp_name', 'branch_code__zone', 'branch_code')
    # print(branch)
    msgDisplay = False
    try:
        if request.is_ajax() and request.method == 'POST':
            # json
            json_basicdetails = json.loads(request.POST['json_basicdetails'])
            json_creditsanction = json.loads(request.POST['json_creditsanction'])
            json_fraud_element = json.loads(request.POST['json_fraud_element'])
            addr_lett_date = request.POST['addr_lett_date']
            json_reply_date = json.loads(request.POST['json_reply_date'])
            rep_auth_remarks = request.POST['rep_auth_remarks']
            ob_regional_head = request.POST['ob_regional_head']
            ob_dept_head = request.POST['ob_dept_head']
            files = request.POST['file_values']
            status = request.POST.get('status')
            session_role = DesignationMatrix.objects.filter(role_code=request.session['new_roles']).values('role_name')[0]['role_name']
            json_reject_remarks_data = json.loads(request.POST['json_reject_remarks_data'])
            # if len(json_reject_remarks_data) > 15:
            #     PSC_rec_id = SACTable.objects.get(id=pk)
            #     PSCTable.objects.filter(id=PSC_rec_id).update(npa_status=False)
            #     # print(PSC_rec_id)
            if val in ['approve2', 'approve3'] and len(json_reject_remarks_data) > 14:
                PSC_rec_id = SACTable.objects.filter(id=pk).values('psc_rec_id')[0]['psc_rec_id']
                print('PSC_rec_id',PSC_rec_id)
                # PSCTable.objects.filter(id=PSC_rec_id).update(npa_status=False)
                psc_cust_id = PSCTable.objects.filter(id=PSC_rec_id).values('cust_id')[0]['cust_id']
                print('psc_cust_id',psc_cust_id)
                PSCTable.objects.filter(cust_id=psc_cust_id).update(npa_status=False,status='Terminated')
                CustomerTable.objects.filter(npa_status=True,cust_id=psc_cust_id).update(npa_status=False,status='Terminated')
                msgDisplay = True
            if val == 'approve2' or val == 'approve3':
                json_reject_remarks_div = json.loads(request.POST['json_reject_remarks_div'])
            else:
                json_reject_remarks_div = None
            if val == 'edit2':
                ob_regional_head = request.POST['ob_regional_head']
            else:
                ob_regional_head = SACTable.objects.filter(id=pk).values('ob_regional_head')
                ob_regional_head = ob_regional_head
            if val == 'edit3':
                ob_dept_head = request.POST['ob_dept_head']
            else:
                ob_dept_head = SACTable.objects.filter(id=pk).values('ob_dept_head')
                ob_dept_head = ob_dept_head
            sac_review_data = [{"basic_details":json_basicdetails},{"credit_sanction":json_creditsanction},{"fraud_element":json_fraud_element},{"addr_lett_date":addr_lett_date},{"reply_date":json_reply_date},{"rep_auth_remarks":rep_auth_remarks},{"ob_regional_head":ob_regional_head},{"ob_dept_head":ob_dept_head},{'pk':pk},{'files':files},{'role_value':val},{'status':status},{'reject_remarks':json_reject_remarks_data},{'reject_remarks_div':json_reject_remarks_div}]

            
            # print(sac_review_data)
            ss = psc_views.SavetoDB.sac_db_store(request ,sac_review_data)
            # print('data',ss)
            if ss.status_code == 200:
                if status == 'Draft':
                    print("User Id: {}, Designation: {}, Role: {}, Action: {}, Message: {}".format(request.session['emp_id'], request.session['designation'], session_role, "SAC Review update Form", "SAC review update Form Drafted ID-"+json_basicdetails[0]['sac_no']))
                    messages.success(request, "SAC form with SAC No %s saved as draft." %json_basicdetails[0]['sac_no'])
                elif status == 'Submitted':
                    print("User Id: {}, Designation: {}, Role: {}, Action: {}, Message: {}".format(request.session['emp_id'], request.session['designation'], session_role, "SAC Review update Form", "SAC review update Form Submitted ID-"+json_basicdetails[0]['sac_no']))
                    messages.success(request, "SAC form with SAC No %s submitted successfully" %json_basicdetails[0]['sac_no'])
                elif status == 'Re-submitted':
                    print("User Id: {}, Designation: {}, Role: {}, Action: {}, Message: {}".format(request.session['emp_id'], request.session['designation'], session_role, "SAC Review update Form", "SAC review update Form Submitted ID-"+json_basicdetails[0]['sac_no']))
                    messages.success(request, "SAC form with SAC No %s re submitted successfully" %json_basicdetails[0]['sac_no'])
                elif status == 'Rejected':
                    # psc_views.NotifyMail.mailerFunction(request,json_basicdetails[0]['sac_no'],'SAC')
                    #print('msgDisplay',msgDisplay)
                    if msgDisplay == False:
                        print("User Id: {}, Designation: {}, Role: {}, Action: {}, Message: {}".format(request.session['emp_id'], request.session['designation'], session_role, "SAC Review update Form", "SAC review update Form Rejected ID-"+json_basicdetails[0]['sac_no']))
                        messages.success(request,'SAC form with SAC No %s rejected successfully' %json_basicdetails[0]['sac_no'])
                    elif msgDisplay == True:
                        print("User Id: {}, Designation: {}, Role: {}, Action: {}, Message: {}".format(request.session['emp_id'], request.session['designation'], session_role, "SAC Review update Form", "SAC review update Form exceeded maximum number of rejections ID-"+json_basicdetails[0]['sac_no']))
                        messages.error(request, "SAC form with SAC No %s exceeded maximum number of rejections and the account has been deleted" %json_basicdetails[0]['sac_no'])
                elif status == 'Approved':
                    print("User Id: {}, Designation: {}, Role: {}, Action: {}, Message: {}".format(request.session['emp_id'], request.session['designation'], session_role, "SAC Review update Form", "SAC review update Form Approved ID-"+json_basicdetails[0]['sac_no']))
                    messages.success(request,'SAC form with SAC No %s approved successfully' %json_basicdetails[0]['sac_no'])
                return HttpResponse("success")
            else:
                messages.error(request,'error code %s' %ss)
                return HttpResponse("error")

        else:
            sac_form_data = SACTable.objects.filter(psc_rec_id__npa_status=True,id=pk).values(*psc_views.sac_all_data)
            psc__id = sac_form_data[0]['psc_rec_id']
            psc__i = sac_form_data[0]['psc_rec_id__cust_id']
            psc__cid = CustomerTable.objects.filter(cust_id=psc__i).values('id')[0]['id']
            sac_data_updated = CustomerTable.objects.filter(cust_id=psc__i).values('lapses_details')[0]['lapses_details']            
            sac_rec_id = sac_form_data[0]['sac_rec_id']
            file_data = fileUpload.file_upload.get_all_documents(app_name, sac_rec_id)
            section_data = set(item['section'] for item in file_data)
            staff_accountability = PSCTable.objects.filter(id=psc__id).values('staff_accountability')[0]['staff_accountability']
            sac_data_updated = CustomerTable.objects.filter(cust_id=psc__i).values('lapses_details')[0]['lapses_details']

            sac_staff_lapses_details = sac_data_updated["records"][0]['staff_lapses_details']

            psc_rec_id = PSCTable.objects.filter(id=psc__id).values('psc_rec_id')[0]['psc_rec_id']
            all_aod = staff_accountability['all_aod']
            file_data1 = fileUpload.file_upload.get_all_documents("preliminaryscreeningcommittee_review", psc_rec_id)
            section_data1 = list(item['section'] for item in file_data1)
            cust_idsac = CustomerTable.objects.filter(cust_id=sac_form_data[0]['psc_rec_id__cust_id']).values('id')[0]['id']
            creditsanctiontable_data = CreditFacilityTable.objects.filter(psc_id=cust_idsac).values(*psc_views.creditsanction_all_data)  
            psc_reject_remarks = sac_form_data[0]['reject_remarks']
            mom_lapses_data = PSCTable.objects.filter(id=psc__id).values('mom_lapse_desc')[0]['mom_lapse_desc']
            psc_remarks_count = len(psc_reject_remarks)
            # print(psc_remarks_count)
            #print('creditsanctiontable_data',creditsanctiontable_data)
                            # print(f"File Content: {file_content}")
            lapses_data = sac_form_data[0]['lapses_data']
            # print(lapses_data)
            # lapses_branch = lapses_data['lapses_branch']
            fraud_element = lapses_data['fraud_element']
            addr_lett_date = lapses_data['addr_lett_date']
            reply_date = lapses_data['reply_date']
            rep_auth_remarks = lapses_data['rep_auth_remarks']
            
            def process_accountability_data(key_dd, key):
                data = lapses_data.get(key, [])
                condition = data[0].get(f"{key_dd}") if data else None
                if condition:
                    return data
                else:
                    return []
            fraud_element = process_accountability_data('fraud_element_dd', 'fraud_element')
            reply_date = process_accountability_data('reply_date_dd', 'reply_date')
            reject_remarks = sac_form_data[0]['reject_remarks']
            context = {'title': title, 'tenant_image': tenant_image,
                       "tenant": tenant, "branch_data": branch_data,'ynstatus':ynstatus,'sac_data':sac_form_data,'fraud_element':fraud_element,'reply_date':reply_date,'file_data':file_data,'section_data':section_data,"section_data1":section_data1,"sac_staff_lapses_details":sac_staff_lapses_details, 'creditsanctiontable_data':creditsanctiontable_data,'maker_role':val,"all_aod":all_aod,'lapses_data':lapses_data,'reject_remarks':reject_remarks,'sac_remarks_count':psc_remarks_count,'mom_lapses_data':mom_lapses_data}
            return render(request, 'preliminaryscreeningcommittee_review/sac_update.html', context=context)
    except Exception as e:
        sc_log.error(str(e))
        return redirect('sac_update')

