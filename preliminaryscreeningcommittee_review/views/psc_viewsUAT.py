import shutil
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse, FileResponse
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Case, When, Value, IntegerField, Count
from django.views.decorators.csrf import csrf_exempt
from boss_admin.models import BranchMaster, DesignationMatrix
from boss_admin.views import my_login_required
from boss_v1.boss_log import screeningcommittee_logging as sc_log
from boss_admin.file_upload import fileUpload
from box import Box
from boss_admin.views.main import generic_export
from boss_admin.views.authentication import my_login_required
from ..models import *
from . import sac_views
import json
import pandas as pd
from openpyxl import Workbook
import io, os, time, base64, tempfile
from reportlab.lib.pagesizes import A4, legal, landscape, letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.lib import colors
from boss_v1 import settings
from PIL import Image as PIMG
from PyPDF2 import PdfReader, PdfMerger, PdfWriter
from fpdf import FPDF
from datetime import date, timedelta, datetime
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from email.message import EmailMessage
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
import smtplib
from io import BytesIO
from boss_admin.views.kbl_api import KBLAPIWrapper
app_name = 'preliminaryscreeningcommittee_review'

def get_apidata(request):
    config_data = Box(request.session['config_data'])
    is_api_data = config_data.module.PSC001.is_api_data
    if is_api_data:
        print("data will come from json")
    else:
        print("no data")
    return 

def update_PSC_SAC_MOM_logs(instanceLog, role_value, user_log,accType):
        #print('update_PSC_SAC_MOM_logs',role_value,user_log,accType)
        session_key = user_log['ses_key']
        status = user_log['status']

        # Function to append status to existing session ID
        def append_or_create(log_list):
            #print('append_or_create')
            # Check if sessionKey already exists in the log list
            for log in log_list:
                #print('log',log)
                if log['ses_key'] == session_key:
                    # Append the status to the same sessionKey entry
                    log['status'] += f", {status}"  # Use comma or space to separate statuses
                    return
            # If sessionKey doesn't exist, append the new user_log
            log_list.append(user_log)

        # Append or create the user_log entry based on role_value
        if accType == 'PSC':
            # Retrieve the current psc_users_log
            psc_users_log = instanceLog.psc_users_log
            if role_value == 'edit1':
                append_or_create(psc_users_log['bo_maker'])
            elif role_value == 'edit2': 
                append_or_create(psc_users_log['ro_maker'])
            elif role_value == 'edit3': 
                append_or_create(psc_users_log['ho_maker'])
            elif role_value == 'approve1': 
                append_or_create(psc_users_log['bo_checker'])
            elif role_value == 'approve2': 
                append_or_create(psc_users_log['ro_checker'])
            elif role_value == 'approve3': 
                append_or_create(psc_users_log['ho_checker'])
            elif role_value == 'convener': 
                append_or_create(psc_users_log['convener'])

            # Update and save the log in the database
            instanceLog.psc_users_log = psc_users_log
            instanceLog.save()
        elif accType == 'SAC':
            #print('SAC',instanceLog,role_value,user_log,accType)
            # Retrieve the current psc_users_log
            sac_users_log = instanceLog.sac_users_log
            if role_value == 'edit2': 
                
                append_or_create(sac_users_log['ro_maker'])
                #print('edit2')
            elif role_value == 'edit3': 
                append_or_create(sac_users_log['ho_maker'])
            elif role_value == 'approve2': 
                append_or_create(sac_users_log['ro_checker'])
            elif role_value == 'approve3': 
                append_or_create(sac_users_log['ho_checker'])
            elif role_value == 'convener': 
                append_or_create(sac_users_log['convener'])
            instanceLog.sac_users_log = sac_users_log
            instanceLog.save()
        elif accType == 'MOM':
            mom_users_log = instanceLog.mom_users_log
            #print('mom_users_log',mom_users_log)
            if role_value == 'createEdit': 
                append_or_create(mom_users_log['ho_checker'])
            elif role_value == 'close': 
                append_or_create(mom_users_log['convener'])
            instanceLog.mom_users_log = mom_users_log
            instanceLog.save()

class SavetoDB:
    def psc_db_store(request, data):
        try:
            psc_form_data = data
            # print('psc_form_data', psc_form_data)
            
            files = psc_form_data[42]['files']
            role_value = psc_form_data[43]['role_value']
            
            # return
            basic_details = psc_form_data[0]['basic_details']
            psc_rec_id = basic_details['psc_num']
            psc_form_date = basic_details['psc_form_date']
            psc_branch = basic_details['psc_branch']
            psc_region = basic_details['psc_region']
            rejection_remarks = psc_form_data[40]['reject_remarks_div']
            
            if psc_form_data[38]['status'] == 'Rejected':
                rejection_level = rejection_remarks[0]['rej_lvl']
            else:
                rejection_level = None

            if role_value == 'edit1':
                if psc_form_data[38]['status'] == 'Draft':
                    current_role = 'BO Maker'
                elif psc_form_data[38]['status'] == 'Submitted' or psc_form_data[38]['status'] == 'Re-submitted':
                    current_role = 'BO Checker'
            elif role_value == 'approve1':
                if psc_form_data[38]['status'] == 'Rejected':
                    current_role = 'BO Maker'
                elif psc_form_data[38]['status'] == 'Approved':
                    current_role = 'RO Maker'
            if role_value == 'edit2':
                if psc_form_data[38]['status'] == 'Submitted' or psc_form_data[38]['status'] == 'Re-submitted':
                    current_role = 'RO Checker'
            elif role_value == 'approve2':
                if psc_form_data[38]['status'] == 'Rejected':
                    if rejection_level == 'BO':
                        current_role = 'BO Maker'
                    elif rejection_level == 'RO':
                        current_role = 'RO Maker'
                elif psc_form_data[38]['status'] == 'Approved':
                    current_role = 'HO Maker'
            if role_value == 'edit3':
                if psc_form_data[38]['status'] == 'Submitted' or psc_form_data[38]['status'] == 'Re-submitted':
                    current_role = 'HO Checker'
            elif role_value == 'approve3':
                if psc_form_data[38]['status'] == 'Rejected':
                    if rejection_level == 'BO':
                        current_role = 'BO Maker'
                    elif rejection_level == 'RO':
                        current_role = 'RO Maker'
                    elif rejection_level == 'HO':
                        current_role = 'HO Maker'
                elif psc_form_data[38]['status'] == 'Approved':
                    current_role = 'Convener'
            credit_sanction = psc_form_data[1]['credit_sanction']
            securities_values = psc_form_data[2]['securities_values']
            # print(credit_sanction)
            # print("securites_values",securities_values)
            #print('savetodb', psc_form_data[29]['all_aod'])
            # return
            # print('here coming')

            staff_accountability_dict = {
                'pre_sanction': psc_form_data[6]['pre_sanction'],
                'pre_sanction_lapses_sa': psc_form_data[7]['pre_sanction_lapses_sa'],
                'post_sanction': psc_form_data[8]['post_sanction'],
                'post_sanction_sa': psc_form_data[9]['post_sanction_sa'],
                'post_sanction_ma': psc_form_data[10]['post_sanction_ma'],
                'sanction_lapses_po': psc_form_data[11]['sanction_lapses_po'],
                'non_fulfillment_tc': psc_form_data[12]['non_fulfillment_tc'],
                'pow_exceeding_insts': psc_form_data[13]['pow_exceeding_insts'],
                'cersai': psc_form_data[14]['cersai'],
                'valua_remarks_varia': psc_form_data[15]['valua_remarks_varia'],
                'sec_availability': psc_form_data[16]['sec_availability'],
                'loan_pro_woc': psc_form_data[17]['loan_pro_woc'],
                'loan_pro_np': psc_form_data[18]['loan_pro_np'],
                'securities_div': psc_form_data[19]['securities_div'],
                'loan_sec_irregularities': psc_form_data[20]['loan_sec_irregularities'],
                'fraud_cases': psc_form_data[21]['fraud_cases'],
                'other_info': psc_form_data[22]['other_info'],
                'aof': psc_form_data[23]['aof'],
                'post_sanc_doc_irregularities': psc_form_data[24]['post_sanc_doc_irregularities'],
                'cgtmse_loan': psc_form_data[25]['cgtmse_loan'],
                'mortgage_notice': psc_form_data[26]['mortgage_notice'],
                'housing_soc_conf': psc_form_data[27]['housing_soc_conf'],
                'post_mort_ec': psc_form_data[28]['post_mort_ec'],
                'all_aod': psc_form_data[29]['all_aod'],
                'insepction_num': psc_form_data[30]['insepction_num'],
                'staff_data': psc_form_data[31]['staff_data'],
                'ad_sanc_bo': psc_form_data[32]['ad_sanc_bo'],
                'bo_names': psc_form_data[33]['bo_names'],
                'so_sa_name': psc_form_data[34]['so_sa_name']
            }
            staff_accountability = staff_accountability_dict
            #print('staff_accountability_dict',staff_accountability_dict)
            # return
            reject_remarks = psc_form_data[39]['reject_remarks']
            reject_remarks_div = psc_form_data[40]['reject_remarks_div']
            if reject_remarks_div:
                # Get the current datetime
                current_datetime = datetime.now().strftime('%d/%m/%Y %I:%M:%S %p')
                
                # Update the 'rej_date' for each entry in reject_remarks_div
                for remark in reject_remarks_div:
                    remark['rej_date'] = current_datetime  # Replace with the current datetime
                
                # Extend the reject_remarks list with updated reject_remarks_div
                reject_remarks.extend(reject_remarks_div)
            # if reject_remarks_div:
            #     reject_remarks.extend(reject_remarks_div)
            # print('data data data')
            
            pk = psc_form_data[41]['pk']
            
            psc_cust_id = psc_form_data[44]['psc_cust_id']
            psc_facility_nos = PSCTable.objects.filter(cust_id = psc_cust_id).values('id')
            psc_instance = CustomerTable.objects.get(cust_id=psc_cust_id)  
            # print('psc_facility_nos',psc_facility_nos,psc_cust_id,psc_branch)
            start_time = time.time()
            sessionKey = request.session['ses_key']
            PSCuser_log = {
                    'user': request.session['emp_id'],  
                    'ses_key': sessionKey,
                    'designation': request.session['designation'],
                    'status': psc_form_data[38]['status']
                }
            if role_value == 'edit1':
                zone_name = BranchMaster.objects.filter(branch_code=request.session['branch_code']).values('zone_name')[0]['zone_name']
                branch_code_id = BranchMaster.objects.filter(branch_code=request.session['branch_code']).values('sl_no')[0]['sl_no']
            else:
                zone_name = psc_region
                branch_code_id = BranchMaster.objects.filter(branch_name=psc_branch).values('sl_no')[0]['sl_no']
            for fn in psc_facility_nos:    
                # print('psc_facility_nos',fn['facility_num'])
                try:
                    PSCTable.objects.filter(id=fn['id']).update(
                    branch_code = branch_code_id,
                    region_name = zone_name,
                    form_creation_date=psc_form_date,
                    borrower_name=basic_details['borrower_name'],
                    address=basic_details['borrower_address'],
                    constitution=basic_details['constitution'],
                    partners=basic_details['partners'],
                    establishment_date=basic_details['establishment_date'],
                    networth=basic_details['networth'],
                    dealing_since=basic_details['dealing_since'],
                    business_nature=basic_details['business_nature'],
                    guarantors_name=basic_details['guarantors_name'],
                    past_performance=psc_form_data[3]['past_performance'],
                    npa_reasons=psc_form_data[4]['npa_reasons'],
                    recovery_steps=psc_form_data[5]['recovery_steps'],
                    staff_accountability=staff_accountability,
                    ob_branch_head=psc_form_data[35]['ob_branch_head'],
                    ob_regional_head=psc_form_data[36]['ob_regional_head'],
                    ob_dept_head=psc_form_data[37]['ob_dept_head'],
                    status=psc_form_data[38]['status'],
                    reject_remarks=reject_remarks,
                    last_modified_date=datetime.now(),
                    last_modified_user=f"{request.session['emp_name']}({request.session['emp_id']})",
                    current_role=current_role
                    )
                except Exception as e:
                    print('basic details error',e)
                # print('data data data')

                psc_instancelog = PSCTable.objects.get(id=fn['id'])
                update_PSC_SAC_MOM_logs(psc_instancelog, role_value, PSCuser_log,'PSC')
            
            end_time = time.time()
            print('**********time taken to update',end_time-start_time)
            # branch_code_id = BranchMaster.objects.filter(branch_name=psc_branch).values('sl_no')[0]['sl_no']
            # print('here')
            #print('current datetime',datetime.now())
            CustomerTable.objects.filter(npa_status=True,cust_id = psc_cust_id).update(
                branch_code = branch_code_id,
                region_name = zone_name,
                status=psc_form_data[38]['status'],
                last_modified_date=datetime.now(),
                last_modified_user=f"{request.session['emp_name']}({request.session['emp_id']})",
                current_role=current_role,
                review_type='psc',
                psc_review_id = pk
            )
            print('**********time taken to update cust table',end_time-start_time)
            print("credit_sanction ",credit_sanction)
            credit_facility_exists = CreditFacilityTable.objects.filter(psc_id=psc_instance).exists()
            try:
                if credit_facility_exists:
                    CreditFacilityTable.objects.filter(psc_id=psc_instance).delete()

                for cs_item in credit_sanction:
                    cs_slno_value = cs_item['cs_slno']
                    cs_refno_value = cs_item['cs_refno']
                    cs_sanc_date_value = datetime.strptime(cs_item['cs_sanc_date'].strip(), "%d-%m-%Y").replace(hour=5, minute=30)
                    cs_acc_nat_value = cs_item['cs_acc_nat']
                    cs_adv_nat_value = cs_item['cs_adv_nat']
                    cs_lan_value = cs_item['cs_lan']
                    cs_san_lim_value = cs_item['cs_san_lim']
                    cs_duedate_value = datetime.strptime(cs_item['cs_duedate'].strip(), "%d-%m-%Y").replace(hour=5, minute=30)
                    cs_npadate_value = datetime.strptime(cs_item['cs_npadate'].strip(), "%d-%m-%Y").replace(hour=5, minute=30)
                    cs_npa_bal_value = cs_item['cs_npa_bal']
                    cs_bal_value = cs_item['cs_bal']
                    cs_adv_purp_value = cs_item['cs_adv_purp']
                    cs_asst_clss_value = cs_item['cs_asst_clss']
                    cf_aod_data_value = cs_item['cf_aod_data']
                    doc_date_value = datetime.strptime(cs_item['doc_date'].strip(), "%d-%m-%Y").replace(hour=5, minute=30)
                    psc_facility_nos = PSCTable.objects.filter(cust_id = psc_cust_id).values('id')

                    # for fn in psc_facility_nos:
                    
                    creditfacilitytable = CreditFacilityTable(
                        creation_date=datetime.now(),
                        created_user=request.session['emp_id'],
                        psc_id=psc_instance,
                        credit_feci_slno=cs_slno_value,
                        reference_num=cs_refno_value,
                        sanction_date=cs_sanc_date_value,
                        account_nature=cs_acc_nat_value,
                        advance_nature=cs_adv_nat_value,
                        lan=cs_lan_value,
                        sanctioned_limit=cs_san_lim_value,
                        due_date=cs_duedate_value,
                        npa_balance=cs_npa_bal_value,
                        balance=cs_bal_value,
                        advance_purpose=cs_adv_purp_value,
                        npa_date=cs_npadate_value,
                        asset_classification=cs_asst_clss_value,
                        cf_aod_data=cf_aod_data_value,
                        doc_date=doc_date_value,
                        
                        last_modified_date=datetime.now(),
                        last_modified_user=f"{request.session['emp_name']}({request.session['emp_id']})"

                    )
                    creditfacilitytable.save()
            except Exception as e:
                print("credit table error ",e)

            securities_exists = SecuritiesTable.objects.filter(psc_id=psc_instance).exists()
            if securities_exists:
                SecuritiesTable.objects.filter(psc_id=psc_instance).delete()

            for item in securities_values:
                sv_sec_nat_value = item['sv_sec_nat']
                sv_lansv_value = item['sv_lansv']
                sv_sec_type_value = item['sv_sec_type']
                sv_san_val_value = item['sv_san_val']
                sv_san_val_date_value = datetime.strptime(item['sv_san_val_date'].strip(), "%d-%m-%Y").replace(hour=5, minute=30)
                sv_lat_val_value = item['sv_lat_val']
                sv_lat_val_date_value = datetime.strptime(item['sv_lat_val_date'].strip(), "%d-%m-%Y").replace(hour=5, minute=30)
                sv_ins_valid_value = datetime.strptime(item['sv_ins_valid'].strip(), "%d-%m-%Y").replace(hour=5, minute=30)
                sv_ins_value_value = item['sv_ins_value']
                sv_cersai_num_value = item['sv_cersai_num']
                            # psc_facility_nos = PSCTable.objects.filter(cust_id = psc_cust_id).values('id')

                try:
                    securities_existstable = SecuritiesTable(
                    creation_date=datetime.now(),
                    created_user=request.session['emp_id'],
                    psc_id=psc_instance,
                    security_nature=sv_sec_nat_value,
                    lan=sv_lansv_value,
                    security_type=sv_sec_type_value,
                    sanction_valuation=sv_san_val_value,
                    sanction_valuation_date=sv_san_val_date_value,
                    latest_valuation=sv_lat_val_value,
                    latest_valuation_date=sv_lat_val_date_value,
                    insurance_valid_upto=sv_ins_valid_value,
                    insurance_value=sv_ins_value_value,
                    cersai_num=sv_cersai_num_value,
                    last_modified_date=datetime.now(),
                    last_modified_user=f"{request.session['emp_name']}({request.session['emp_id']})"
                    )
                    securities_existstable.save()
                except Exception as e:
                    print("secuirities table error ",e)


            if files:
                files_values = json.loads(files)
                fileUpload.file_upload.insert_documents(
                    'PSC', app_name, psc_rec_id, files_values, request.session['emp_id']
                )
            #print('end')

            return HttpResponse('success')

        except Exception as e:
            sc_log.error('Error while storing data to PSCTable error occurred is ' + e)
            # print('Error while storing data to PSCTable error occurred is ' + e)
            # print(e)
            return HttpResponse(f'Error: {str(e)}', status=500)
    
    def sac_db_store(request,data):
        try:
            sac_form_data = data
            #print('data',sac_form_data)
            basic_details = sac_form_data[0]['basic_details'][0]
            exec_name = basic_details['exec_name']
            staff_no = basic_details['staff_no']
            cur_desig = basic_details['cur_desig']
            cur_addr = basic_details['cur_addr']
            psc_no = basic_details['psc_no']
            # psc_instance = PSCTable.objects.get(id=pk)
            #print('here',psc_no)
            cust_id = PSCTable.objects.filter(psc_rec_id=psc_no).values('cust_id')[0]['cust_id']
            branch_code_id = PSCTable.objects.filter(psc_rec_id=psc_no).values('branch_code')[0]['branch_code']
            region_name = PSCTable.objects.filter(psc_rec_id=psc_no).values('region_name')[0]['region_name']
            # psc_id = CustomerTable.objects.filter(cust_id=cust_id).values('id')[0]['id']
            #print('here 22',branch_code_id,region_name)
            # return
            psc_form_date = basic_details['psc_date']
            #print('psc_form_date',psc_form_date)
            # return
            lapse_branch = basic_details['lapse_branch']
            sac_no = basic_details['sac_no']
            credit_sanction = sac_form_data[1]['credit_sanction']
            # #print('credit_sanction',credit_sanction)
            # return
            fraud_element = sac_form_data[2]['fraud_element']
            addr_lett_date = sac_form_data[3]['addr_lett_date']
            reply_date = sac_form_data[4]['reply_date']
            rep_auth_remarks = sac_form_data[5]['rep_auth_remarks']
            ob_regional_head = sac_form_data[6]['ob_regional_head']
            ob_dept_head = sac_form_data[7]['ob_dept_head']
            pk = sac_form_data[8]['pk']
            files = sac_form_data[9]['files']
            role_value = sac_form_data[10]['role_value']
            status = sac_form_data[11]['status']
            lapses_data = {
                'lapses_branch': lapse_branch,
                'fraud_element': fraud_element,
                'addr_lett_date': addr_lett_date,
                'reply_date': reply_date,
                'rep_auth_remarks': rep_auth_remarks
            }
            reject_remarks = sac_form_data[12]['reject_remarks']
            reject_remarks_div = sac_form_data[13]['reject_remarks_div']
            if reject_remarks_div:
                # Get the current datetime
                current_datetime = datetime.now().strftime('%d/%m/%Y %I:%M:%S %p')
                
                # Update the 'rej_date' for each entry in reject_remarks_div
                for remark in reject_remarks_div:
                    remark['rej_date'] = current_datetime  # Replace with the current datetime
                
                # Extend the reject_remarks list with updated reject_remarks_div
                reject_remarks.extend(reject_remarks_div)
            # if reject_remarks_div:
            #     reject_remarks.extend(reject_remarks_div)
            if sac_form_data[11]['status'] == 'Rejected':
                rejection_level = reject_remarks_div[0]['rej_lvl']
            else:
                rejection_level = None
            #print('role_value',role_value,sac_form_data[11]['status'])
            if role_value == 'edit2':
                if sac_form_data[11]['status'] == 'Draft':
                    current_role = 'RO Maker'
                elif sac_form_data[11]['status'] == 'Submitted' or sac_form_data[11]['status'] == 'Re-submitted':
                    current_role = 'RO Checker'
            elif role_value == 'approve2':
                if sac_form_data[11]['status'] == 'Rejected':
                    current_role = 'RO Maker'
                elif sac_form_data[11]['status'] == 'Approved':
                    current_role = 'HO Maker'
            if role_value == 'edit3':
                if sac_form_data[11]['status'] == 'Submitted' or sac_form_data[11]['status'] == 'Re-submitted':
                    current_role = 'HO Checker'
            elif role_value == 'approve3':
                if sac_form_data[11]['status'] == 'Rejected':
                    if rejection_level == 'RO':
                        current_role = 'RO Maker'
                    elif rejection_level == 'HO':
                        current_role = 'HO Maker'
                elif sac_form_data[11]['status'] == 'Approved':
                    current_role = 'Convener'
          
            sessionKey = request.session['ses_key']
            SACuser_log = {
                    'user': request.session['emp_id'],  
                    'ses_key': sessionKey,
                    'designation': request.session['designation'],
                    'status': sac_form_data[11]['status']
                }
            psc_facility_nos = SACTable.objects.filter(sac_rec_id = sac_no).values('id')
            # psc_instance = CustomerTable.objects.get(cust_id=cust_id)  
            #print('psc_facility_nos',psc_facility_nos)
            # return
            sessionKey = ''
            start_time = time.time()
           
            for fn in psc_facility_nos:
                # return
                try:
                    SACTable.objects.filter(id=fn['id']).update(
                        emp_name = exec_name,
                        staff_no = staff_no,
                        present_designation = cur_desig,
                        present_working = cur_addr,
                        status = status,
                        psc_date = psc_form_date,
                        lapses_data = lapses_data,
                        reject_remarks = reject_remarks,
                        ob_regional_head = ob_regional_head,
                        ob_dept_head = ob_dept_head,
                        last_modified_date = datetime.now(),
                        last_modified_user=f"{request.session['emp_name']}({request.session['emp_id']})",
                        current_role = current_role
                    )
                    sac_instancelog = SACTable.objects.get(id=fn['id'])
                    update_PSC_SAC_MOM_logs(sac_instancelog, role_value, SACuser_log,'SAC')
                except Exception as e:
                    print('SAC store error ', e)
            end_time = time.time()
            print('**********time taken to update',end_time-start_time)
            # branch_code_id = BranchMaster.objects.filter(id=branch_code).values('sl_no')[0]['sl_no']
            # print('here')
            # {"acc_count": 3, "total_exposure": 6600000, "current_role": null, "status": null}
            customer = CustomerTable.objects.get(cust_id=cust_id)
            #print('customer',customer)
            # Update the JSON field
            if customer.sac_details:
                sac_details = customer.sac_details
            else:
                sac_details = {}

            sac_details.update({
                "current_role": current_role,
                "status": status
            })

            # Save the changes
            customer.sac_details = sac_details
            customer.last_modified_date = datetime.now()
            customer.last_modified_user = f"{request.session['emp_name']}({request.session['emp_id']})"
            customer.sac_review_id = pk
            customer.save()
          
            #print('data saved to cs')
            # # Add your SAC file update logic here
            if (len(files) > 0):        
                files_values = json.loads(files)
                fileUpload.file_upload.insert_documents('SAC',app_name,sac_no,files_values, request.session['emp_id'])
                #print('data saved to fu')
            return HttpResponse('success')
        except Exception as e:
            # print(e)
            sc_log.error(e)
            # print('Error while storing data to SACTable error occured is ' + e)
            return HttpResponse(f'SAC Error: {str(e)}', status=500)

    def mom_db_store(request,data,rev_type):
        try:
            #print('data',data)
            # meeting_id = data[0]['meetingId']  
            
            mom_generation_date = data[0]['momGenerationDate']  
            mom_date = data[1]['momDate']  
            audience = data[2]['audience']  
            date_obj = datetime.strptime(mom_date, "%d-%m-%Y")
            formatted_date = date_obj.strftime("%d/%m/%Y")
            mom_count_gen = MOMTable.objects.filter(review_type = 'sac',mom_creation_date__date=datetime.now().date()).count() + 1 
            sessionKey = request.session['ses_key']
            MOMuser_log = {
                    'user': request.session['emp_id'],  
                    'ses_key': sessionKey,
                    'designation': request.session['designation'],
                    'status': 'created'
                }
            # print(meeting_id)
            # return
            # if MOMTable.objects.filter(mom_date__date__in=mom_date)
            # from datetime import datetime

            # mom_date = data[1]['momDate']
            # audience = data[2]['audience']
            today = datetime.now().date()

            # Convert mom_date to datetime object
            mom_date_obj = datetime.strptime(mom_date.strip(), "%d-%m-%Y").replace(hour=5, minute=30).date()
            
            # Check if mom_date is already present in db
            if rev_type == 'PSC1':
                meeting_id = f'PSC1-{mom_count_gen:02d}-{formatted_date}'
                # mom_count = MOMTable.objects.filter(review_type = 'psc',mom_creation_date__date=datetime.now().date()).count() + 1 
                is_today_mom = MOMTable.objects.filter(review_type='PSC1',active=True,mom_date__date=mom_date_obj).exists()
                is_present_today = MOMTable.objects.filter(review_type='PSC1',active=True,mom_date__date=today).exists()
                is_present_before_today = MOMTable.objects.filter(review_type='PSC1',active=True,mom_date__date__lt=today).exists()
                is_present_after_today = MOMTable.objects.filter(review_type='PSC1',active=True,mom_date__date__gt=today).exists()
                count_present_before_today = MOMTable.objects.filter(review_type='PSC1',active=True,mom_date__date__lt=today).count()
                count_present_after_today = MOMTable.objects.filter(review_type='PSC1',active=True,mom_date__date__gt=today).count()
                
                if ((is_present_today and is_present_after_today)):
                    messages.error(request,'MOM cannot be created, Active Current & Active Future Exist')
                elif((is_present_today and is_present_before_today)):
                    messages.error(request,'MOM cannot be created, Active Current & Active Past Exist')
                elif ((is_present_after_today and is_present_before_today)):
                    messages.error(request,'MOM cannot be created, Active Past & Active Future Exist3')
                elif(is_today_mom):
                    messages.error(request,'An active MOM exists for selected date')
                elif(count_present_before_today >= 2):
                    messages.error(request,'MOM cannot be created, 2 Past Active Exist')
                elif(count_present_after_today >= 2):
                    messages.error(request,'MOM cannot be created, 2 Future Active Exist')
                else:
                    # mom_count = MOMTable.objects.filter(review_type = 'psc',mom_date__date=today).count() + 1
                    #print('success')
                    # if is_present_before_today:
                    #     old_loan_count = PSCTable.objects.filter(mom_lapse__isnull=True).count()
                    # return                
                    mom_save = MOMTable.objects.create(
                    created_user = request.session['emp_id'], 
                    meeting_id = meeting_id, 
                    mom_creation_date = datetime.strptime(mom_generation_date.strip(), "%d-%m-%Y").replace(hour=5, minute=30), 
                    mom_date = datetime.strptime(mom_date.strip(), "%d-%m-%Y").replace(hour=5, minute=30), 
                    audience = audience, 
                    last_modified_date = datetime.now(), 
                    last_modified_user=f"{request.session['emp_name']}({request.session['emp_id']})", 
                    review_type = rev_type, 
                    mom_users_log = {"ho_checker": [MOMuser_log],"convener": []}
                    )
                    mom_save.save()
                    mom_id = mom_save.id
                    #print('mom_id',mom_id,meeting_id)

                    mom_total_count(request,mom_id,rev_type)
                    messages.success(request,'MOM created successfully')
            
            elif rev_type == 'PSC2':
                meeting_id = f'PSC2-{mom_count_gen:02d}-{formatted_date}'
                # mom_count = MOMTable.objects.filter(review_type = 'psc',mom_creation_date__date=datetime.now().date()).count() + 1 
                is_today_mom = MOMTable.objects.filter(review_type='PSC2',active=True,mom_date__date=mom_date_obj).exists()
                is_present_today = MOMTable.objects.filter(review_type='PSC2',active=True,mom_date__date=today).exists()
                is_present_before_today = MOMTable.objects.filter(review_type='PSC2',active=True,mom_date__date__lt=today).exists()
                is_present_after_today = MOMTable.objects.filter(review_type='PSC2',active=True,mom_date__date__gt=today).exists()
                count_present_before_today = MOMTable.objects.filter(review_type='PSC2',active=True,mom_date__date__lt=today).count()
                count_present_after_today = MOMTable.objects.filter(review_type='PSC2',active=True,mom_date__date__gt=today).count()
                
                if ((is_present_today and is_present_after_today)):
                    messages.error(request,'MOM cannot be created, Active Current & Active Future Exist')
                elif((is_present_today and is_present_before_today)):
                    messages.error(request,'MOM cannot be created, Active Current & Active Past Exist')
                elif ((is_present_after_today and is_present_before_today)):
                    messages.error(request,'MOM cannot be created, Active Past & Active Future Exist3')
                elif(is_today_mom):
                    messages.error(request,'An active MOM exists for selected date')
                elif(count_present_before_today >= 2):
                    messages.error(request,'MOM cannot be created, 2 Past Active Exist')
                elif(count_present_after_today >= 2):
                    messages.error(request,'MOM cannot be created, 2 Future Active Exist')
                else:
                    # mom_count = MOMTable.objects.filter(review_type = 'psc',mom_date__date=today).count() + 1
                    #print('success')
                    # if is_present_before_today:
                    #     old_loan_count = PSCTable.objects.filter(mom_lapse__isnull=True).count()
                    # return
                    mom_save = MOMTable.objects.create(
                    created_user = request.session['emp_id'], 
                    meeting_id = meeting_id, 
                    mom_creation_date = datetime.strptime(mom_generation_date.strip(), "%d-%m-%Y").replace(hour=5, minute=30), 
                    mom_date = datetime.strptime(mom_date.strip(), "%d-%m-%Y").replace(hour=5, minute=30), 
                    audience = audience, 
                    last_modified_date = datetime.now(), 
                    last_modified_user=f"{request.session['emp_name']}({request.session['emp_id']})",
                    review_type = rev_type, 
                    mom_users_log = {"ho_checker": [MOMuser_log], "convener": []}
                    )
                    mom_save.save()
                    mom_id = mom_save.id
                    #print('mom_id',mom_id)

                    mom_total_count(request,mom_id,rev_type)
                    messages.success(request,'MOM created successfully')
            
            elif rev_type == 'sac':
                meeting_id = f'SAC{mom_count_gen:02d}-{formatted_date}'
                # mom_count = MOMTable.objects.filter(review_type = 'sac',mom_creation_date__date=datetime.now().date()).count() + 1                 
                is_today_mom = MOMTable.objects.filter(review_type = 'sac',active=True,mom_date__date=mom_date_obj).exists()
                is_present_today = MOMTable.objects.filter(review_type = 'sac',active=True,mom_date__date=today).exists()
                is_present_before_today = MOMTable.objects.filter(review_type = 'sac',active=True,mom_date__date__lt=today).exists()
                is_present_after_today = MOMTable.objects.filter(review_type = 'sac',active=True,mom_date__date__gt=today).exists()
                count_present_before_today = MOMTable.objects.filter(review_type = 'sac',active=True,mom_date__date__lt=today).count()
                count_present_after_today = MOMTable.objects.filter(review_type = 'sac',active=True,mom_date__date__gt=today).count()
                
                if ((is_present_today and is_present_after_today)):
                    messages.error(request,'MOM cannot be created, Active Current & Active Future Exist')
                elif((is_present_today and is_present_before_today)):
                    messages.error(request,'MOM cannot be created, Active Current & Active Past Exist')
                elif ((is_present_after_today and is_present_before_today)):
                    messages.error(request,'MOM cannot be created, Active Past & Active Future Exist3')
                elif(is_today_mom):
                    messages.error(request,'An active MOM exists for selected date')
                elif(count_present_before_today >= 2):
                    messages.error(request,'MOM cannot be created, 2 Past Active Exist')
                elif(count_present_after_today >= 2):
                    messages.error(request,'MOM cannot be created, 2 Future Active Exist')
                else:
                    # mom_count = MOMTable.objects.filter(review_type = 'sac',mom_date__date=today).count() + 1
                    #print('success')
                    # return
                    mom_save = MOMTable.objects.create(
                    created_user = request.session['emp_id'], 
                    meeting_id = meeting_id, 
                    mom_creation_date = datetime.strptime(mom_generation_date.strip(), "%d-%m-%Y").replace(hour=5, minute=30), 
                    mom_date = datetime.strptime(mom_date.strip(), "%d-%m-%Y").replace(hour=5, minute=30), 
                    audience = audience, 
                    last_modified_date = datetime.now(), 
                    last_modified_user=f"{request.session['emp_name']}({request.session['emp_id']})",
                    review_type = rev_type, 
                    mom_users_log = {"ho_checker": [MOMuser_log], "convener": []}
                    )
                    mom_save.save()
                    mom_id = mom_save.id
                    mom_total_count(request,mom_id,'sac')
                    messages.success(request,'MOM created successfully')
        except Exception as e:
            # print(e)
            messages.error(request,'MOM could not be created')
            sc_log.error(e)
            # print('MOM related error occured is ' + str(e))
            return HttpResponse(f'Error: {str(e)}', status=500)

class FilterData:
    
    def filter_psc_data(psccustomer_data, psc_zone, psc_review_status):
        #print('psc_zone',psc_zone)
        if psc_zone == 'all' and psc_review_status == 'all':
            return psccustomer_data
        elif psc_zone == 'all' and psc_review_status != 'all':
            return [data for data in psccustomer_data if data.status == psc_review_status]
        elif psc_zone != 'all' and psc_review_status == 'all':
            return [data for data in psccustomer_data if data.branch_code_id == int(psc_zone)]
        elif psc_zone != 'all' and psc_review_status != 'all':
            return [data for data in psccustomer_data if data.status == psc_review_status and data.branch_code_id == int(psc_zone)]
        else:
            return psccustomer_data

        
    def filter_sac_data(saccustomer_data,sac_zone,sac_review_status):
        #print('sac filter')
        if sac_zone == 'all' and sac_review_status == 'all':
            return saccustomer_data
        elif sac_zone == 'all' and sac_review_status != 'all':
            return [data for data in saccustomer_data if data.sac_details.get('status') == sac_review_status]
        elif sac_zone != 'all' and sac_review_status == 'all':
            return [data for data in saccustomer_data if data.branch_code_id == int(sac_zone)]
        elif sac_zone != 'all' and sac_review_status != 'all':
            return [data for data in saccustomer_data if data.sac_details.get('status') == sac_review_status and data.branch_code_id == int(sac_zone)]
        else:
            return saccustomer_data

class SearchData:
    def search_psc_data(psccustomer_data, search):
        # print('psc_data search', psccustomer_data, search)
        if search:
            psccustomer_data = [customer for customer in psccustomer_data if (
                search in str(customer.psc_rec_id) or
                search in str(customer.branch_code) or
                search in str(customer.region_name) or
                search in str(customer.cust_id) or
                search.replace(',', '') in str(customer.total_exposure) or
                search in str(customer.status) or
                search in str(customer.borrower_name) or
                search in str(customer.current_role)
            )]
            # print('searched data', psccustomer_data)
            return psccustomer_data
        else:
            return psccustomer_data

    def search_sac_data(saccustomer_data,search):
        if search:
            saccustomer_data = [customer for customer in saccustomer_data if (
                search in str(customer.sac_rec_id) or
                search in str(customer.branch_code) or
                search in str(customer.region_name) or
                search in str(customer.cust_id) or
                search in str(customer.sac_details.get('status')) or
                search.replace(',', '') in str(customer.sac_details.get('total_exposure')) or
                search in str(customer.borrower_name) or
                search in str(customer.sac_details.get('current_role'))
            )]
            # print('searched data', saccustomer_data)
            #print(sac_data)
            return saccustomer_data
        else:
            return saccustomer_data
        
    def search_mom_data(data, search):
        if search:
            if search == 'True':
                mom_data = data.filter(
                    Q(meeting_id__icontains=search) |
                    Q(mom_creation_date__icontains=search) |
                    Q(mom_date__icontains=search) |
                    Q(audience__icontains=search) |
                    Q(active= True)
                )
                return mom_data
            
            elif search == 'False':
                mom_data = data.filter(
                    Q(meeting_id__icontains=search) |
                    Q(mom_creation_date__icontains=search) |
                    Q(mom_date__icontains=search) |
                    Q(audience__icontains=search) |
                    Q(active=False)
                )
                return mom_data
            
            else:
                mom_data = data.filter(
                    Q(meeting_id__icontains=search) |
                    Q(mom_creation_date__icontains=search) |
                    Q(mom_date__icontains=search) |
                    Q(audience__icontains=search)
                )
                return mom_data
        else:
            return data

class ExportData:
    def export_psc_data(pscall_export, psc_zone, psc_review_status):
        # print('psc_zone,psc_review_status',psc_zone,psc_review_status)
        if psc_zone == 'all' and psc_review_status == 'all':
            return pscall_export
        elif psc_zone == 'all' and psc_review_status != 'all':
            return [data for data in pscall_export if data.get('status') == psc_review_status]
        elif psc_zone != 'all' and psc_review_status == 'all':
            return [data for data in pscall_export if data.get('branch_code') == int(psc_zone)]
        elif psc_zone != 'all' and psc_review_status != 'all':
            return [data for data in pscall_export if data.get('status') == psc_review_status and data.get('branch_code') == int(psc_zone)]
        else:
            return pscall_export

    def export_sac_data(sac_data,sac_zone,sac_review_status):
        # print('sac_data export',sac_data,sac_zone,sac_review_status)
        if sac_zone == 'all' and sac_review_status == 'all':
            return sac_data
        elif sac_zone == 'all' and sac_review_status != 'all':
            return sac_data.filter(sac_details__status=sac_review_status)
        elif sac_zone != 'all' and sac_review_status == 'all':
            return sac_data.filter(branch_code=int(sac_zone))
        elif sac_zone != 'all' and sac_review_status != 'all':
            return sac_data.filter(sac_details__status=sac_review_status, branch_code=int(sac_zone))
        else:
            return sac_data

psc_all_data = ['id','creation_date','created_user','psc_rec_id','branch_code_id__branch_code','branch_code_id__zone_name','branch_code_id__branch_name','region_name','cust_id','facility_num','sanc_limit','npa_date','npa_date__date','nap_tag','npa_status','status','borrower_name','address','constitution','partners','establishment_date','networth','dealing_since','business_nature','guarantors_name','past_performance','npa_reasons','recovery_steps','staff_accountability','ob_branch_head','ob_regional_head','ob_dept_head','reject_remarks','mom_lapse','mom_lapse_desc','mom_br_head','mom_id','last_modified_date','last_modified_user','current_role','form_creation_date']

creditsanction_all_data = ['id', 'creation_date', 'created_user', 'psc_id', 'credit_feci_slno', 'cf_aod_data','doc_date','reference_num', 'sanction_date', 'account_nature', 'advance_nature', 'lan', 'sanctioned_limit', 'due_date', 'npa_balance', 'balance', 'advance_purpose', 'npa_date', 'asset_classification', 'last_modified_date', 'last_modified_user']

securities_all_data = ['id', 'creation_date', 'created_user', 'psc_id', 'security_nature', 'lan', 'security_type', 'sanction_valuation', 'sanction_valuation_date', 'latest_valuation', 'latest_valuation_date', 'insurance_valid_upto', 'insurance_value', 'cersai_num', 'last_modified_date', 'last_modified_user']

mom_all_data = ['id','created_user','meeting_id','mom_creation_date','mom_date','audience','loan_count','mom_closure_date','active','last_modified_date','last_modified_user','review_type']

sac_all_data = ['id','creation_date','created_user','psc_rec_id','sac_rec_id','emp_name','staff_no','present_designation','present_working','status','psc_date','lapses_data','reject_remarks','ob_regional_head','ob_dept_head','mom_lapse','mom_lapse_desc','mom_br_head','mom_id','last_modified_date','last_modified_user','current_role','psc_rec_id__branch_code_id__branch_code','psc_rec_id__branch_code_id__branch_name','psc_rec_id__cust_id','psc_rec_id__borrower_name','psc_rec_id__facility_num','psc_rec_id__sanc_limit','psc_rec_id__region_name','psc_rec_id__npa_date','psc_rec_id__npa_date__date','psc_rec_id__nap_tag','psc_rec_id__psc_rec_id','psc_rec_id__form_creation_date']

# PSC & SAC
@my_login_required
def dashboard(request):
    """
    welcome
    :param request:
    :return:
    """
    try:
        session_role = DesignationMatrix.objects.filter(role_code=request.session['new_roles']).values('role_name')[0]['role_name']
        config_data = Box(request.session['config_data'])
        tenant = config_data.tenant 
        tenant_image = config_data.logo_image.image_path
        # print('session data',request.session['new_roles'], request.session['designation'])
        current_role = DesignationMatrix.objects.filter(role_code=request.session['new_roles']).values('role_name')[0]['role_name']
        roles = request.session['new_roles'].split("_")
        if 'psc001maker1' in roles or 'psc001checker1' in roles or 'psc001maker3' in roles or 'psc001checker3' in roles:
            title = config_data.module.PSC001.app_namepsc
        elif 'sac001maker3' in roles or 'sac001checker3' in roles:
            title = config_data.module.PSC001.app_namesac
        else:
            title = config_data.module.PSC001.app_name
        region_list = BranchMaster.objects.values_list('zone',flat=True).distinct().exclude(branch_code='001')
        zoneData = BranchMaster.objects.values("zone").distinct().order_by("zone").exclude(branch_code='001')
        _branch = request.session['branch_code']
        br_sl_no = BranchMaster.objects.filter(branch_code=_branch).values("sl_no")[0]['sl_no']
        # print(br_sl_no)
        zone_filter = BranchMaster.objects.filter(branch_code=_branch).values("zone").order_by("zone")
        branch_code_data = BranchMaster.objects.filter(zone=zone_filter[0]['zone']).values('sl_no','branch_code','branch_name')
        branch_code_HO_data = BranchMaster.objects.values('sl_no','branch_code','branch_name')
        current_emp_data = f"{request.session['emp_name']}({request.session['emp_id']})" 
        # print('region_list,_branch',branch_code_data)
        # RO Data
        if _branch in region_list:
            #RO Maker/Checker Dashboard
            ro_list = BranchMaster.objects.filter(zone=_branch).values_list('branch_code',flat=True).distinct()
            # print(((ro_list)))
            pscall_accounts = CustomerTable.objects.filter(
                Q(review_type='psc') | Q(review_type__isnull=True),npa_status=True,
            ).annotate(
                status_order=Case(
                    When(Q(status='Approved') & Q(current_role='RO Maker'), then=Value(0)),
                    When(Q(status='Approved') & ~Q(current_role='RO Maker'), then=Value(4)),
                    When(status__in=[ 'Draft', 'Rejected'], then=Value(1)),
                    When(status = 'Convened', then=Value(5)),
                    When(status__in=[ 'Re-submitted', 'Submitted'], then=Value(3)),
                    default=Value(2),
                    output_field=IntegerField(),
                )
            ).order_by('status_order', '-last_modified_date')            
            pscfiltered_accounts = []
            for account in pscall_accounts:
                if account.branch_code:
                    if str(account.branch_code) in list(ro_list):
                        pscfiltered_accounts.append(account)
                else:
                    pscfiltered_accounts.append(account)
            psccustomer_data = pscfiltered_accounts
            pscall_accountsApproval = CustomerTable.objects.filter(
                Q(review_type='psc') | Q(review_type__isnull=True),npa_status=True,
            ).annotate(
                status_order=Case(
                    When(status__in=[ 'Re-submitted', 'Submitted'], then=Value(0)),
                    default=Value(1),
                    output_field=IntegerField(),
                )
            ).order_by('status_order', '-last_modified_date')            
            pscfiltered_accountsApproval = []
            for account in pscall_accountsApproval:
                if account.branch_code:
                    if str(account.branch_code) in list(ro_list):
                        pscfiltered_accountsApproval.append(account)
                else:
                    pscfiltered_accountsApproval.append(account)
            psccustomer_dataApproval = pscfiltered_accountsApproval
            sacall_accounts = CustomerTable.objects.filter(npa_status=True,sac_details__isnull=False).annotate(
                    status_order=Case(
                        When(Q(sac_details__status='Approved') & Q(current_role='RO Maker'), then=Value(0)),
                        When(Q(sac_details__status='Approved') & ~Q(current_role='RO Maker'), then=Value(3)),
                        When(sac_details__status__in=[ 'Draft', 'Rejected'], then=Value(1)),
                        When(sac_details__status = 'Convened', then=Value(4)),
                        When(sac_details__status__in=[ 'Re-submitted', 'Submitted'], then=Value(2)),
                        default=Value(1),
                        output_field=IntegerField(),
                    )
                ).order_by('status_order', '-last_modified_date')
            #print('sacall_accounts',sacall_accounts)
            sacfiltered_accounts = []
            for account in sacall_accounts:
                if account.branch_code:
                    if str(account.branch_code) in list(ro_list):
                        sacfiltered_accounts.append(account)
                else:
                    sacfiltered_accounts.append(account)
            saccustomer_data = sacfiltered_accounts
            sacall_accountsApproval = CustomerTable.objects.filter(npa_status=True,sac_details__isnull=False).annotate(
                    status_order=Case(
                        When(sac_details__status__in=[ 'Draft', 'Rejected'], then=Value(0)),
                        When(sac_details__status__in=[ 'Convened', 'Approved'], then=Value(3)),
                        When(sac_details__status__in=[ 'Re-submitted', 'Submitted'], then=Value(2)),
                        default=Value(1),
                        output_field=IntegerField(),
                    )
                ).order_by('status_order', '-last_modified_date')
            #print('sacall_accounts',sacall_accounts)
            sacfiltered_accountsApproval = []
            for account in sacall_accountsApproval:
                if account.branch_code:
                    if str(account.branch_code) in list(ro_list):
                        sacfiltered_accountsApproval.append(account)
                else:
                    sacfiltered_accountsApproval.append(account)
            saccustomer_dataApproval = sacfiltered_accountsApproval
            psc_data = PSCTable.objects.filter(
            npa_status=True,
            branch_code_id__branch_code__in=ro_list
                ).values(*psc_all_data).annotate(
                    status_order=Case(
                        When(status__in=['Submitted','Convened','Approved'], then=Value(1)),
                        default=Value(0),
                        output_field=IntegerField(),
                    )
                ).order_by('status_order', '-last_modified_date')
            
            sac_data = SACTable.objects.filter(psc_rec_id__npa_status=True,psc_rec_id__branch_code_id__branch_code__in=ro_list).values(*sac_all_data).annotate(
                status_order=Case(
                    When(status__in=['Submitted','Convened','Approved'], then=Value(1)),
                    default=Value(0),
                    output_field=IntegerField(),
                )
            ).order_by('status_order', '-last_modified_date')
            sac_data_export = SACTable.objects.filter(psc_rec_id__npa_status=True,psc_rec_id__branch_code__in=ro_list).values('sac_rec_id','psc_rec_id__branch_code','psc_rec_id__region_name','psc_rec_id__cust_id','psc_rec_id__facility_num','psc_rec_id__sanc_limit','psc_rec_id__npa_date','psc_rec_id__nap_tag','psc_rec_id__borrower_name','status')
        # HO Data
            print("User Id: {}, Designation: {}, Role: {}, Action: {}, Message: RO Dashboard Opened".format(request.session['emp_id'], request.session['designation'], session_role, "RO Dashboard"))

        elif _branch == '001':
            #HO Maker/Checker Dashboard
            ro_list = BranchMaster.objects.values_list('branch_code',flat=True).distinct()
            pscall_accounts = CustomerTable.objects.filter(
                Q(review_type='psc') | Q(review_type__isnull=True),npa_status=True
            ).annotate(
                status_order=Case(
                    When(Q(status='Approved') & Q(current_role='HO Maker'), then=Value(0)),
                    When(Q(status='Approved') & ~Q(current_role='HO Maker'), then=Value(4)),
                    When(status__in=[ 'Draft', 'Rejected'], then=Value(1)),
                    When(status = 'Convened', then=Value(5)),
                    When(status__in=[ 'Re-submitted', 'Submitted'], then=Value(3)),
                    default=Value(2),
                    output_field=IntegerField(),
                )
            ).order_by('status_order', '-last_modified_date')    
            pscfiltered_accounts = []
            for account in pscall_accounts:
                if account.branch_code:
                    if str(account.branch_code) in list(ro_list):
                        pscfiltered_accounts.append(account)
                else:
                    pscfiltered_accounts.append(account)
            psccustomer_data = pscfiltered_accounts
            # Checker
            pscall_accountsApproval = CustomerTable.objects.filter(
                Q(review_type='psc') | Q(review_type__isnull=True),npa_status=True
            ).annotate(
                status_order=Case(
                    When(status__in=[ 'Re-submitted', 'Submitted'], then=Value(0)),
                    default=Value(1),
                    output_field=IntegerField(),
                )
            ).order_by('status_order', '-last_modified_date')    
            pscfiltered_accountsApproval = []
            for account in pscall_accountsApproval:
                if account.branch_code:
                    if str(account.branch_code) in list(ro_list):
                        pscfiltered_accountsApproval.append(account)
                else:
                    pscfiltered_accountsApproval.append(account)
            psccustomer_dataApproval = pscfiltered_accountsApproval
            #print('psccustomer_data',psccustomer_data)
            sacall_accounts = sacall_accounts = CustomerTable.objects.filter(npa_status=True,sac_details__isnull=False).annotate(
                    status_order=Case(
                        When(Q(sac_details__status='Approved') & Q(current_role='HO Maker'), then=Value(0)),
                        When(Q(sac_details__status='Approved') & ~Q(current_role='HO Maker'), then=Value(3)),
                        When(sac_details__status__in=[ 'Draft', 'Rejected'], then=Value(1)),
                        When(sac_details__status = 'Convened', then=Value(4)),
                        When(sac_details__status__in=[ 'Re-submitted', 'Submitted'], then=Value(2)),
                        default=Value(1),
                        output_field=IntegerField(),
                    )
                ).order_by('status_order', '-last_modified_date')
            sacfiltered_accounts = []
            for account in sacall_accounts:
                if account.branch_code:
                    if str(account.branch_code) in list(ro_list):
                        sacfiltered_accounts.append(account)
                else:
                    sacfiltered_accounts.append(account)
            saccustomer_data = sacfiltered_accounts
            sacall_accountsApproval = CustomerTable.objects.filter(npa_status=True,sac_details__isnull=False).annotate(
                    status_order=Case(
                        When(sac_details__status__in=[ 'Re-submitted', 'Submitted'], then=Value(0)),
                        default=Value(1),
                        output_field=IntegerField(),
                    )
                ).order_by('status_order', '-last_modified_date')
            sacfiltered_accountsApproval = []
            for account in sacall_accountsApproval:
                if account.branch_code:
                    if str(account.branch_code) in list(ro_list):
                        sacfiltered_accountsApproval.append(account)
                else:
                    sacfiltered_accountsApproval.append(account)
            saccustomer_dataApproval = sacfiltered_accountsApproval
            psc_data = PSCTable.objects.filter(npa_status=True,branch_code_id__branch_code__in=ro_list
                ).values(*psc_all_data).annotate(
                    status_order=Case(
                        When(status__in=['Submitted','Convened','Approved'], then=Value(1)),
                        default=Value(0),
                        output_field=IntegerField(),
                    )
                ).order_by('status_order', '-last_modified_date')
            

            sac_data = SACTable.objects.filter(psc_rec_id__npa_status=True,psc_rec_id__branch_code__in=ro_list).values(*sac_all_data).annotate(
                status_order=Case(
                    When(status__in=['Submitted','Convened','Approved'], then=Value(1)),
                    default=Value(0),
                    output_field=IntegerField(),
                )
            ).order_by('status_order', '-last_modified_date')
            sac_data_export = SACTable.objects.filter(psc_rec_id__npa_status=True,psc_rec_id__branch_code__in=ro_list).values('sac_rec_id','psc_rec_id__branch_code','psc_rec_id__region_name','psc_rec_id__cust_id','psc_rec_id__facility_num','psc_rec_id__sanc_limit','psc_rec_id__npa_date','psc_rec_id__nap_tag','psc_rec_id__borrower_name','status','current_role')
            print("User Id: {}, Designation: {}, Role: {}, Action: {}, Message: HO Dashboard Opened".format(request.session['emp_id'], request.session['designation'], session_role, "HO Dashboard"))

        # BO Data
        else:
            #Branch Maker/Checker Dashboard
            pscall_accounts = CustomerTable.objects.filter(
                Q(review_type='psc') | Q(review_type__isnull=True),npa_status=True
            ).annotate(
                status_order=Case(
                    When(status__in=[ 'Draft', 'Rejected'], then=Value(0)),
                    When(status__in=[ 'Convened', 'Approved'], then=Value(3)),
                    When(status__in=[ 'Re-submitted', 'Submitted'], then=Value(2)),
                    default=Value(1),
                    output_field=IntegerField(),
                )
            ).order_by('status_order', '-last_modified_date')    
            pscfiltered_accounts = []
            for account in pscall_accounts:
                if account.branch_code:
                    if str(account.branch_code) == request.session.get('branch_code'):
                        pscfiltered_accounts.append(account)
                else:
                    pscfiltered_accounts.append(account)
            psccustomer_data = pscfiltered_accounts
            pscall_accountsApproval = CustomerTable.objects.filter(
                Q(review_type='psc') | Q(review_type__isnull=True),npa_status=True
            ).annotate(
                status_order=Case(
                    When(status__in=[ 'Re-submitted', 'Submitted'], then=Value(0)),
                    default=Value(1),
                    output_field=IntegerField(),
                )
            ).order_by('status_order', '-last_modified_date')    
            pscfiltered_accountsApproval = []
            for account in pscall_accountsApproval:
                if account.branch_code:
                    if str(account.branch_code) == request.session.get('branch_code'):
                        pscfiltered_accountsApproval.append(account)
                else:
                    pscfiltered_accountsApproval.append(account)
            psccustomer_dataApproval = pscfiltered_accountsApproval
            
            sacall_accounts = CustomerTable.objects.filter(npa_status=True,sac_details__isnull=False).annotate(
                    status_order=Case(
                        When(sac_details__status__in=[ 'Draft', 'Rejected'], then=Value(0)),
                        When(sac_details__status__in=[ 'Convened', 'Approved'], then=Value(3)),
                        When(sac_details__status__in=[ 'Re-submitted', 'Submitted'], then=Value(2)),
                        default=Value(1),
                        output_field=IntegerField(),
                    )
                ).order_by('status_order', '-last_modified_date')
            # CustomerTable.objects.filter(npa_status=True,sac_details__isnull=False).all().order_by('-last_modified_date')
            sacfiltered_accounts = []
            for account in sacall_accounts:
                if account.branch_code:
                    if str(account.branch_code) == request.session.get('branch_code'):
                        sacfiltered_accounts.append(account)
                else:
                    sacfiltered_accounts.append(account)
            saccustomer_data = sacfiltered_accounts
            sacall_accountsApproval = CustomerTable.objects.filter(npa_status=True,sac_details__isnull=False).annotate(
                    status_order=Case(
                        When(sac_details__status__in=[ 'Re-submitted', 'Submitted'], then=Value(0)),
                        default=Value(1),
                        output_field=IntegerField(),
                    )
                ).order_by('status_order', '-last_modified_date')
            # CustomerTable.objects.filter(npa_status=True,sac_details__isnull=False).all().order_by('-last_modified_date')
            sacfiltered_accountsApproval = []
            for account in sacall_accountsApproval:
                if account.branch_code:
                    if str(account.branch_code) == request.session.get('branch_code'):
                        sacfiltered_accountsApproval.append(account)
                else:
                    sacfiltered_accountsApproval.append(account)
            saccustomer_dataApproval = sacfiltered_accountsApproval
            # sorted(sacfiltered_accounts, key=lambda x: x.last_modified_date, reverse=True)
            psc_data = PSCTable.objects.filter(npa_status=True,branch_code_id__branch_code=request.session['branch_code']).values(*psc_all_data).annotate(
                    status_order=Case(
                        When(status__in=['Submitted','Convened','Approved'], then=Value(1)),
                        default=Value(0),
                        output_field=IntegerField(),
                    )
                ).order_by('status_order', '-last_modified_date')
            
            
            sac_data = SACTable.objects.filter(psc_rec_id__npa_status=True,psc_rec_id__branch_code=request.session['branch_code']).values(*sac_all_data).annotate(
                status_order=Case(
                    When(status__in=['Submitted','Convened','Approved'], then=Value(1)),
                    default=Value(0),
                    output_field=IntegerField(),
                )
            ).order_by('status_order', '-last_modified_date')
            sac_data_export = SACTable.objects.filter(psc_rec_id__npa_status=True,psc_rec_id__branch_code=request.session['branch_code']).values('sac_rec_id','psc_rec_id__branch_code','psc_rec_id__region_name','psc_rec_id__cust_id','psc_rec_id__facility_num','psc_rec_id__sanc_limit','psc_rec_id__npa_date','psc_rec_id__nap_tag','psc_rec_id__borrower_name','status','current_role')
            print("User Id: {}, Designation: {}, Role: {}, Action: {}, Message: BO Dashboard Loaded".format(request.session['emp_id'], request.session['designation'], session_role, "BO Dashboard"))
        pscall_export = CustomerTable.objects.filter(npa_status=True,review_type='psc').values('psc_rec_id', 'branch_code', 'cust_id', 'borrower_name', 'total_exposure', 'status', 'current_role').order_by('-last_modified_date')
        sacall_export = CustomerTable.objects.filter(npa_status=True,sac_details__isnull=False).values('sac_rec_id', 'branch_code', 'cust_id', 'borrower_name','sac_details__status','sac_details__current_role').order_by('-last_modified_date')

        if 'psc001maker1' in roles or 'psc001checker1' in roles:
            psc_data = psc_data
            pscall_export = pscall_export
            psccustomer_data = psccustomer_data
            # print('psc_data',psc_data)
        elif 'psc001maker2' in roles or 'psc001checker2' in roles:
            #print('here')
            psc_data = psc_data.filter( Q(current_role__in=['HO Maker', 'HO Checker', 'RO Maker', 'RO Checker', 'Convener']) |
                        Q(status='Convened'))
            pscall_export = pscall_export.filter( Q(current_role__in=['HO Maker', 'HO Checker', 'RO Maker', 'RO Checker', 'Convener']) |Q(status='Convened'))
            psccustomer_data = [customer for customer in psccustomer_data if customer.current_role in ['HO Maker', 'HO Checker', 'RO Maker', 'RO Checker', 'Convener'] or customer.status == 'Convened']
            # print('psccustomer_data',psccustomer_data)
        elif 'psc001maker3' in roles or 'psc001checker3' in roles:
            
            psc_data = psc_data.filter( Q(current_role__in=['HO Maker', 'HO Checker', 'Convener']) |
                    Q(status='Convened'))
            psccustomer_data = [customer for customer in psccustomer_data if customer.current_role in ['HO Maker', 'HO Checker', 'Convener'] or customer.status == 'Convened']
            # print('in maker3 checker3',psccustomer_data)
            pscall_export = pscall_export.filter(Q(current_role__in=['HO Maker', 'HO Checker', 'Convener']) |
                    Q(status='Convened'))

        if 'psc001maker2' in roles or 'psc001checker2' in roles:
            sac_data = sac_data
            saccustomer_data = saccustomer_data
            sac_data_export = sac_data_export
            # print('sac_data',sac_data)
        elif 'sac001maker3' in roles or 'sac001checker3' in roles:
            sac_data = sac_data.filter(Q(current_role__in=['HO Maker', 'HO Checker', 'Convener']) |
                    Q(status='Convened'))
            saccustomer_data = [
                customer for customer in saccustomer_data
                if customer.sac_details.get('current_role') in ['HO Maker', 'HO Checker', 'Convener'] or customer.sac_details.get('status') == 'Convened'
            ]

            # print('saccustomer_data',saccustomer_data)
            sac_data_export = sac_data_export.filter(Q(current_role__in=['HO Maker', 'HO Checker', 'Convener']) |
                    Q(status='Convened'))
        if request.method == "POST":
            psc_zone_filter = request.POST.get('psc_zone')
            psc_review_status_filter = request.POST.get('psc_review_status')
            search = request.POST.get('search_psc')
            psc_zone_export = request.POST.get('psc_zone_export')
            psc_review_status_export = request.POST.get('psc_review_status_export')
            sac_zone_filter = request.POST.get('sac_zone_filter')
            sac_review_status_filter = request.POST.get('sac_review_status')
            sac_search = request.POST.get('search_sac')
            sac_zone_export = request.POST.get('sac_zone_export')
            sac_review_status_export = request.POST.get('sac_review_status_export')  
            # print(sac_zone_filter,sac_review_status_filter,'sac_zone_filter,sac_review_status_filter') 
            if psc_zone_filter and psc_review_status_filter:
                print("User Id: {}, Designation: {}, Role: {}, Action: {}, Message: PSC Filter Option Clicked in Dashboard".format(request.session['emp_id'], request.session['designation'], session_role, "PSC Filter"))
                if 'psc001maker1' in roles or 'psc001checker1' in roles:
                    psccustomer_data = FilterData.filter_psc_data(psccustomer_data, br_sl_no, psc_review_status_filter)
                else:
                    psccustomer_data = FilterData.filter_psc_data(psccustomer_data, psc_zone_filter, psc_review_status_filter)
            elif search:
                print("User Id: {}, Designation: {}, Role: {}, Action: {}, Message: PSC Search Option Clicked in Dashboard".format(request.session['emp_id'], request.session['designation'], session_role, "PSC Search"))
                psccustomer_data = SearchData.search_psc_data(psccustomer_data, search)
                # customer_data = SearchData.search_psc_data(customer_data, search)
            elif psc_zone_export and psc_review_status_export:
                print("User Id: {}, Designation: {}, Role: {}, Action: {}, Message: PSC Export Option Clicked in Dashboard".format(request.session['emp_id'], request.session['designation'], session_role, "PSC Export"))
                if 'psc001maker1' in roles or 'psc001checker1' in roles:
                    pscall_export = ExportData.export_psc_data(pscall_export,br_sl_no,psc_review_status_export)
                else:
                    #print(pscall_export)
                    pscall_export = ExportData.export_psc_data(pscall_export,psc_zone_export,psc_review_status_export)
                    #print('export data',pscall_export)
                #print(psccustomer_dataExport,len(psccustomer_dataExport))
                if len(pscall_export) == 0:
                    messages.error(request, "No data found for applied filters to export.")
                    return redirect('dashboard')

                else:
                    #print('here')
                    response = HttpResponse(content_type='application/ms-excel')
                    response['Content-Disposition'] = 'attachment; filename="PSC_report.xlsx"'
                    columns = ['PSC Srl Num',	'Branch Code',	'Customer ID',	'Borrower Name',	'Total Exposure','PSC status','Current Role']
                    df4 = pd.DataFrame(pscall_export)
                    # #print((df4.columns))
                    # df4.drop(df4.columns[[11]], axis=1, inplace=True)
                    df4.to_excel(excel_writer=response, engine="xlsxwriter",
                                header=columns, index=False)  # with other applicable parameters
                    return response
            
            elif sac_zone_filter and sac_review_status_filter:
                #print('saccustomer_data',sacall_export)
                print("User Id: {}, Designation: {}, Role: {}, Action: {}, Message: SAC Filter Option Clicked in Dashboard".format(request.session['emp_id'], request.session['designation'], session_role, "SAC Filter"))
                saccustomer_data = FilterData.filter_sac_data(saccustomer_data, sac_zone_filter, sac_review_status_filter)
            elif sac_search:
                print("User Id: {}, Designation: {}, Role: {}, Action: {}, Message: SAC Search Option Clicked in Dashboard".format(request.session['emp_id'], request.session['designation'], session_role, "SAC Search"))
                saccustomer_data = SearchData.search_sac_data(saccustomer_data, sac_search)
            elif sac_zone_export and sac_review_status_export:
                print("User Id: {}, Designation: {}, Role: {}, Action: {}, Message: SAC Export Option Clicked in Dashboard".format(request.session['emp_id'], request.session['designation'], session_role, "SAC Export"))
                sacall_export = ExportData.export_sac_data(sacall_export,sac_zone_export,sac_review_status_export)
                #print(sac_data_export,len(sac_data_export))
                if len(sacall_export) == 0:
                    messages.error(request, "No data found for applied filters to export.")
                    return redirect('dashboard')

                else:
                    response = HttpResponse(content_type='application/ms-excel')
                    response['Content-Disposition'] = 'attachment; filename="SAC_report.xlsx"'
                    columns = ['SAC Srl Num', 'Branch Code', 'Customer ID','Borrower Name',	'SAC status',	'Current Role']
                    # for item in sacall_export:
                    #     if 'psc_rec_id__npa_date' in item:
                    #         item['psc_rec_id__npa_date'] = item['psc_rec_id__npa_date'].replace(tzinfo=None)
                    df4 = pd.DataFrame(sacall_export)
                    # print((df4.columns))
                    # df4.drop(df4.columns[[11]], axis=1, inplace=True)
                    df4.to_excel(excel_writer=response, engine="xlsxwriter",
                                header=columns, index=False)  # with other applicable parameters
                    return response
        
            # print('search',psc_data)
        psc_paginator = Paginator(psccustomer_data, 10)
        psc_page_number = request.GET.get('page')
        psc_page_obj = psc_paginator.get_page(psc_page_number)

        # sac_data = SACTable.objects.all().order_by('-last_modified_date')
        sac_paginator = Paginator(saccustomer_data, 10)
        sac_page_number = request.GET.get('page')
        sac_page_obj = sac_paginator.get_page(sac_page_number)
        # branch_code_filter = BranchMaster.objects.filter(zone=)
        region_data_psc = PSCTable.objects.values('region_name').annotate(num_regions=Count('region_name'))
        region_data_sac = SACTable.objects.values('psc_rec_id__region_name').annotate(num_regions=Count('psc_rec_id__region_name'))
        # print('region_data_sac',region_data_sac)
        context = {
            'title': title,
            'tenant_image': tenant_image,
            'tenant': tenant,
            'psc_data': psc_data,
            'psccustomer_data':psc_page_obj,
            'saccustomer_data':sac_page_obj,
            'sac_data': psc_data,
            'branch_code_data':branch_code_data,
            'branch_code_HO_data':branch_code_HO_data,
            'region_data_psc': region_data_psc,
            'region_data_sac': region_data_sac,
            'psccustomer_dataApproval': psccustomer_dataApproval,
            'saccustomer_dataApproval': saccustomer_dataApproval,
            "current_emp_data": current_emp_data
        }
        # sc_log.info('Dashboard was accessed')
        return render(request, 'preliminaryscreeningcommittee_review/dashboard.html', context=context)
    except Exception as e:
        # Log the exception
        # print(e)
        sc_log.error(e)
        print("User Id: {}, Designation: {}, Role: {}, Action: {}, Message: {}".format(request.session['emp_id'], request.session['designation'], session_role, "Dashboard Error", e))
        return redirect('dashboard')

@my_login_required
def fetch_employee_data(request):
    config_data = Box(request.session['config_data'])
    is_api_data = config_data.module.PSC001.is_api_data
    session_role = DesignationMatrix.objects.filter(role_code=request.session['new_roles']).values('role_name')[0]['role_name']
    #print('is_api_data',is_api_data,'true')
    if request.is_ajax() and request.method == 'POST':
        staff_no = request.POST.get("staff_no")
        #print('staff_no',staff_no)
        try:
            if staff_no:
                if is_api_data == True:
                    
                    # HUPMINQtoken = KBLAPIWrapper.OAuthBearer()
                    
                    encHUPMINQ = KBLAPIWrapper.EmpDataAPI(staff_no)
                    # print('HUPMINQtoken,encHUPMINQ',HUPMINQtoken,encHUPMINQ)
                    # dec_data = HUPMINQAPICall.APIDataFetch(HUPMINQtoken,encHUPMINQ)
                    
                    # encHUPMINQ = HUPMINQAPICall.decryption(dec_data["Response"])
                    # print('encHUPMINQ',len(encHUPMINQ),encHUPMINQ)
                    if len(encHUPMINQ) > 2:
                        #print('in 1st if')
                        if staff_no[1:] == encHUPMINQ['empId']:
                            #print(staff_no[1:] == encHUPMINQ['empId'])
                            employee_data = encHUPMINQ
                            return JsonResponse(employee_data)
                        else:
                            return JsonResponse({"error": "Employee not found"}, status=404)
                    else:
                        #print('in 1st else')
                        sc_log.error('Employee fetch API error: Employee not found')
                        print("User Id: {}, Designation: {}, Role: {}, Action: {}, Message: Employee fetch API error: Employee not found".format(request.session['emp_id'], request.session['designation'], session_role, "API Error"))
                        return JsonResponse({"error": "Employee not found"}, status=404)
                else:
                    dummy_data = {
                                    "654321": {
                                        "empId": "654321",
                                        "solId": "4560",
                                        "empName": "Ashok Kumar",
                                        "designation": "Software Engineer",
                                        "workclass": "HO Checker"
                                    },
                                    "987654": {
                                        "empId": "987654",
                                        "solId": "7890",
                                        "empName": "John Smith",
                                        "designation": "System Analyst",
                                        "workclass": "Quality Assurance"
                                    },
                                    "123456": {
                                        "empId": "123456",
                                        "solId": "1357",
                                        "empName": "Emily Johnson",
                                        "designation": "Database Administrator",
                                        "workclass": "Database Manager"
                                    },
                                    "234567": {
                                        "empId": "234567",
                                        "solId": "2468",
                                        "empName": "Michael Brown",
                                        "designation": "Network Engineer",
                                        "workclass": "Network Administrator"
                                    },
                                    "345678": {
                                        "empId": "345678",
                                        "solId": "3579",
                                        "empName": "Jessica Miller",
                                        "designation": "Software Developer",
                                        "workclass": "Team Lead"
                                    },
                                    "456789": {
                                        "empId": "456789",
                                        "solId": "4680",
                                        "empName": "David Wilson",
                                        "designation": "Project Manager",
                                        "workclass": "Project Lead"
                                    },
                                    "567890": {
                                        "empId": "567890",
                                        "solId": "5791",
                                        "empName": "Emma Garcia",
                                        "designation": "Business Analyst",
                                        "workclass": "Business Analyst Lead"
                                    },
                                    "678901": {
                                        "empId": "678901",
                                        "solId": "6802",
                                        "empName": "Daniel Martinez",
                                        "designation": "Software Engineer",
                                        "workclass": "Developer"
                                    },
                                    "789012": {
                                        "empId": "789012",
                                        "solId": "7913",
                                        "empName": "Olivia Rodriguez",
                                        "designation": "UX Designer",
                                        "workclass": "UX Lead"
                                    },
                                    "890123": {
                                        "empId": "890123",
                                        "solId": "8024",
                                        "empName": "William Hernandez",
                                        "designation": "Systems Analyst",
                                        "workclass": "Systems Analyst Lead"
                                    },
                                    "901234": {
                                        "empId": "901234",
                                        "solId": "9135",
                                        "empName": "Sophia Lopez",
                                        "designation": "Software Developer",
                                        "workclass": "Senior Developer"
                                    },
                                    "012345": {
                                        "empId": "012345",
                                        "solId": "0246",
                                        "empName": "Alexander Gonzalez",
                                        "designation": "Network Administrator",
                                        "workclass": "Senior Network Engineer"
                                    },
                                    "543210": {
                                        "empId": "543210",
                                        "solId": "5319",
                                        "empName": "Ethan Perez",
                                        "designation": "Project Manager",
                                        "workclass": "Lead Project Manager"
                                    },
                                    "678901": {
                                        "empId": "678901",
                                        "solId": "6258",
                                        "empName": "Mia Moore",
                                        "designation": "Business Analyst",
                                        "workclass": "Senior Business Analyst"
                                    },
                                    "432109": {
                                        "empId": "432109",
                                        "solId": "7473",
                                        "empName": "Abigail Taylor",
                                        "designation": "System Administrator",
                                        "workclass": "Lead System Administrator"
                                    }
                                }

                    if staff_no in dummy_data:
                        employee_data = dummy_data[staff_no]
                        return JsonResponse(employee_data)
                    else:
                        print("User Id: {}, Designation: {}, Role: {}, Action: {}, Message: Employee fetch API error: Employee not found".format(request.session['emp_id'], request.session['designation'], session_role, "Employee Fetch Error"))
                        return JsonResponse({"error": "Employee not found"}, status=404)

            else:
                return JsonResponse({"error": "Employee not found"}, status=400)
            # print('here coming')

        except Exception as e:
            sc_log.error(e)
            print("User Id: {}, Designation: {}, Role: {}, Action: {}, Message: {}".format(request.session['emp_id'], request.session['designation'], session_role, "Employee Fetch Error", e))
            # print('Employee fetch API error: ' + str(e))
            # print('emp data api',e)


def get_psc_data(request):
    if request.method == 'POST' and request.is_ajax():
        cust_id = request.POST.get('cust_id')
        # Fetch MOM data associated with p_data_id
        try:
            customer_data = list(CustomerTable.objects.filter(npa_status=True,cust_id=cust_id).values('psc_rec_id','cust_id','borrower_name','branch_code_id__branch_code','total_exposure'))
            psc_data = list(PSCTable.objects.filter(cust_id=cust_id).values(*psc_all_data))
            current_branch_code = request.session['branch_code']
            region_name = BranchMaster.objects.filter(branch_code=current_branch_code).values('zone_name')[0]['zone_name']
            if current_branch_code == '001':
                head_office = '001'
            else:
                head_office = ''
            # print('branch_code',current_branch_code,region_name,head_office)
            # print('psc_data',customer_data)
            context = {
            'psc_data': psc_data,
            'customer_data': customer_data,
            'branch_code': current_branch_code,
            'region_name': region_name,
            'head_office': head_office,
            'roles': request.session['new_roles'].split("_")
            }
            return JsonResponse({'data':(context)})
        except MOMTable.DoesNotExist:
            return JsonResponse({'error': 'PSC data not found'}, status=404)
    return JsonResponse({'error': 'Invalid request'}, status=400)

def get_sac_data(request):
    if request.method == 'POST' and request.is_ajax():
        cust_id = request.POST.get('cust_id')
        # Fetch MOM data associated with p_data_id
        try:
            customer_data = list(CustomerTable.objects.filter(npa_status=True,cust_id=cust_id).values('psc_rec_id','cust_id','borrower_name','branch_code_id__branch_code','total_exposure','sac_rec_id','sac_details'))
            sac_data = list(SACTable.objects.filter(psc_rec_id__cust_id=cust_id).values(*sac_all_data))
            current_branch_code = request.session['branch_code']
            region_name = BranchMaster.objects.filter(branch_code=current_branch_code).values('zone_name')[0]['zone_name']
            if current_branch_code == '001':
                head_office = '001'
            else:
                head_office = ''
            # print('branch_code',current_branch_code,region_name,head_office)
            # print('sac_data',customer_data)
            context = {
            'sac_data': sac_data,
            'customer_data': customer_data,
            'branch_code': current_branch_code,
            'region_name': region_name,
            'head_office': head_office,
            'roles': request.session['new_roles'].split("_")
            }
            return JsonResponse({'data':(context)})
        except MOMTable.DoesNotExist:
            return JsonResponse({'error': 'PSC data not found'}, status=404)
    return JsonResponse({'error': 'Invalid request'}, status=400)

def convertToYYYYMMDD(date_str):
    """converts date ddmmyyyy to yyyymmdd"""
    return datetime.strptime(date_str, "%d-%m-%Y").strftime("%Y-%m-%d")

def date_slash_2_hyphen(dateStr):
    # return dateStr.replace("/", "-")
    if dateStr == "NULL":
        return "01-01-1990"
    else:
        dateObj = datetime.strptime(dateStr, "%d/%m/%Y")
        if dateObj:
            return dateObj.strftime("%d-%m-%Y")

def api_datatype_check(data):
    if data == "NULL" or data == "null":
        return "01-01-1990"
    else:
        return data

def api_dataType_num_check(data):
    if data == "NULL":
        return 0
    else:
        return data


def modify_cust_asst_data(api_res):
    try:
        ca_api_data = {
            "RequestUUID": api_res.get("RequestUUID"),
            "HStatus": api_res.get("HStatus"),
            "basic_details":{
                "borrower_name" : api_res.get("Name_of_the_Properiter_1", "NA"),
                "borrower_address" : api_res.get("Borrower_Address_1", "NA"),
                "constitution" : api_res.get("Constitution_1", "NA"),
                "partners" : api_res.get("Name_of_the_Properiter_1", "NA"),
                "establishment_date" : api_res.get("Estb_Date_1",convertToYYYYMMDD("1-1-1990")),
                "networth" : api_dataType_num_check(api_res.get("Networth_of_the_Borrower_1", 0)),
                "dealing_since" : convertToYYYYMMDD(api_datatype_check(api_res.get("Dealing_with_us_Since_1", "NA"))),
                "business_nature" : api_res.get("Nature_of_Business_1", "NA"),
                "guarantors_name" : api_res.get("Names_of_the_Co_Obligant_1", "NA") 
            },
            "credit_facility":[],

            "securities_values":[]
        }

        i=1
        while f"Constitution_{i}" in api_res:
            credit_facility = {
                "credit_feci_slno": i,
                "reference_num": api_res.get(f"Sanction_Ref_Number_{i}", "NA"),
                "sanction_date": api_datatype_check(api_res.get(f"Sanction_Date_{i}", "NA")),
                "account_nature": api_res.get(f"Nature_of_Account_{i}", "NA"),
                "advance_nature": api_res.get(f"Count_of_Securities_{i}", "NA"),
                "lan": api_res.get(f"Loan_Account_No_{i}", "NA"),
                "sanctioned_limit": api_dataType_num_check(api_res.get(f"SanctionLimitAmt_{i}", 0)),
                "due_date": api_datatype_check(api_res.get(f"DueDate_{i}", "NA")),
                "npa_date": api_datatype_check(api_res.get(f"DATE_OF_NPA_{i}", "NA")),
                "npa_balance": api_dataType_num_check(api_res.get(f"BalanceAsOnNPADate_{i}", 0)),
                "balance": api_dataType_num_check(api_res.get(f"BalanceAsOnNPADate_{i}", 0)),
                "advance_purpose": api_res.get(f"Purpose_of_Advance_{i}", "NA"),
                "asset_classification": api_res.get(f"ASSET_CLASSIFICATION_{i}", "NA"),
                "doc_date": api_datatype_check(api_res.get(f"AodDate_{i}", "NA"))
            }

            securities_values = {
                "security_nature": api_res.get(f"Nature_of_Security_{i}", "NA"),
                "lan": api_res.get(f"Loan_Account_No_{i}", "NA"),
                "security_type": api_res.get(f"Type_of_Security_{i}", "NA"),
                "sanction_valuation": api_dataType_num_check(api_res.get(f"SanctionLimitAmt_{i}", 0)),
                "sanction_valuation_date": date_slash_2_hyphen(api_res.get(f"Date_of_Valuation_Sanction_{i}", "NA")),
                "latest_valuation": api_dataType_num_check(api_res.get(f"Present_Valuation_{i}", 0)),
                "latest_valuation_date": date_slash_2_hyphen(api_res.get(f"Date_of_Valuation_{i}", "NA")),
                "insurance_valid_upto": api_datatype_check(api_res.get(f"InsuranceVaidUpToDate_{i}", "NA")),
                "insurance_value": api_dataType_num_check(api_res.get(f"InsuranceValue_{i}", 0)),
                "cersai_num": api_res.get(f"CERSAI_Number_{i}", "NA")
            }

            ca_api_data['credit_facility'].append(credit_facility)
            ca_api_data['securities_values'].append(securities_values)
            
            i+=1
        return ca_api_data

    except Exception as e:
        # print(e)
        sc_log.error(e)
        print("User Id: {}, Designation: {},  Action: {}, Message: {}".format(request.session['emp_id'], request.session['designation'], "Customer Assets API Error", e))
        return None


@my_login_required
def psc_review(request,pk):
    """
    welcome
    :param request:
    :return:
    """
    config_data = Box(request.session['config_data'])
    tenant = config_data.tenant
    title = config_data.module.PSC001.psc_display_name
    tenant_image = config_data.logo_image.image_path
    ynstatus = config_data.module.PSC001.ynstatus
    roles= request.session['new_roles'].split("_")
    session_role = DesignationMatrix.objects.filter(role_code=request.session['new_roles']).values('role_name')[0]['role_name']
    psc_brcode = PSCTable.objects.filter(id=pk).values('branch_code')[0]['branch_code']
    branch_data = BranchMaster.objects.filter(branch_code=psc_brcode).values('branch_name', 'zone_name')
    datadisable = 'maker'
    try:
        if request.is_ajax() and request.method == 'POST':
            pk = request.POST['pk']
            json_basicdetails = json.loads(request.POST['json_basicdetails'])
            json_creditsanction = json.loads(request.POST['json_creditsanction'])
            json_securitiesvalues = json.loads(request.POST['json_securitiesvalues'])
            psc_cust_id = request.POST['psc_cust_id']
            past_performance = request.POST['past_performance']
            npa_reasons = request.POST['npa_reasons']
            recovery_steps = request.POST['recovery_steps']
            json_pre_sanction = json.loads(request.POST['json_pre_sanction'])
            json_pre_sanction_sa = json.loads(request.POST['json_pre_sanction_sa'])
            json_post_sanction = json.loads(request.POST['json_post_sanction'])
            json_post_sanction_sa = json.loads(request.POST['json_post_sanction_sa'])
            json_post_sanction_ma = json.loads(request.POST['json_post_sanction_ma'])
            json_sanction_lapses_po = json.loads(request.POST['json_sanction_lapses_po'])
            json_non_fulfillment_tc = json.loads(request.POST['json_non_fulfillment_tc'])
            json_pow_exceeding_insts = json.loads(request.POST['json_pow_exceeding_insts'])
            json_cersai = json.loads(request.POST['json_cersai'])
            json_valua_remarks_varia = json.loads(request.POST['json_valua_remarks_varia'])
            json_sec_availability = json.loads(request.POST['json_sec_availability'])
            json_loan_pro_woc = json.loads(request.POST['json_loan_pro_woc'])
            json_loan_pro_np = json.loads(request.POST['json_loan_pro_np'])
            json_securities_div = json.loads(request.POST['json_securities_div'])
            json_loan_sec_irregularities = json.loads(request.POST['json_loan_sec_irregularities'])
            json_fraud_cases = json.loads(request.POST['json_fraud_cases'])
            json_other_info = json.loads(request.POST['json_other_info'])
            json_aof = json.loads(request.POST['json_aof'])
            json_post_sanc_doc_irregularities = json.loads(request.POST['json_post_sanc_doc_irregularities'])
            json_cgtmse_loan = json.loads(request.POST['json_cgtmse_loan'])
            json_mortgage_notice = json.loads(request.POST['json_mortgage_notice'])
            json_housing_soc_conf = json.loads(request.POST['json_housing_soc_conf'])
            json_post_mort_ec = json.loads(request.POST['json_post_mort_ec'])
            json_all_aod = json.loads(request.POST['json_all_aod'])
            #print('json_all_aod',json_all_aod)
            json_insepction_num = json.loads(request.POST['json_insepction_num'])
            json_staff_data = json.loads(request.POST['json_staff_data'])
            json_ad_sanc_bo = json.loads(request.POST['json_ad_sanc_bo'])
            json_bo_names = json.loads(request.POST['json_bo_names'])
            json_so_sa_name = json.loads(request.POST['json_so_sa_name'])
            json_reject_remarks_data = json.loads(request.POST['json_reject_remarks_data'])
            json_reject_remarks_div = None
            ob_branch_head = None
            ob_regional_head = None
            ob_dept_head = None
            files = request.POST['file_values']
            status = request.POST.get('status')
            # if status == 'Draft':
            #     role_value = 'BO Maker'
            # elif status == 'Submitted':
            #     role_value = 'BO Checker'
            psc_review_data = [{"basic_details":json_basicdetails},{"credit_sanction":json_creditsanction},{"securities_values":json_securitiesvalues},{"past_performance":past_performance},{"npa_reasons":npa_reasons},{"recovery_steps":recovery_steps},{"pre_sanction":json_pre_sanction},{"pre_sanction_lapses_sa":json_pre_sanction_sa},{"post_sanction":json_post_sanction},{"post_sanction_sa":json_post_sanction_sa},{"post_sanction_ma":json_post_sanction_ma},{"sanction_lapses_po":json_sanction_lapses_po},{"non_fulfillment_tc":json_non_fulfillment_tc},{"pow_exceeding_insts":json_pow_exceeding_insts},{"cersai":json_cersai},{"valua_remarks_varia":json_valua_remarks_varia},{"sec_availability":json_sec_availability},{"loan_pro_woc":json_loan_pro_woc},{"loan_pro_np":json_loan_pro_np},{"securities_div":json_securities_div},{"loan_sec_irregularities":json_loan_sec_irregularities},{"fraud_cases":json_fraud_cases},{"other_info":json_other_info},{"aof":json_aof},{"post_sanc_doc_irregularities":json_post_sanc_doc_irregularities},{"cgtmse_loan":json_cgtmse_loan},{"mortgage_notice":json_mortgage_notice},{"housing_soc_conf":json_housing_soc_conf},{"post_mort_ec":json_post_mort_ec},{"all_aod":json_all_aod},{"insepction_num":json_insepction_num},{"staff_data":json_staff_data},{"ad_sanc_bo":json_ad_sanc_bo},{"bo_names":json_bo_names},{"so_sa_name":json_so_sa_name},{"ob_branch_head":ob_branch_head},{"ob_regional_head":ob_regional_head},{"ob_dept_head":ob_dept_head},{"status":status},{"reject_remarks":json_reject_remarks_data},{"reject_remarks_div":json_reject_remarks_div},{'pk':pk},{'files':files},{'role_value':'edit1'},{'psc_cust_id':psc_cust_id}]
            # print(psc_review_data)
            ss = SavetoDB.psc_db_store(request,psc_review_data)
            #print('data',ss)
            if ss.status_code == 200:
                
                
                if status == 'Draft':
                    print("User Id: {}, Designation: {}, Role: {}, Action: {}, Message: {}".format(request.session['emp_id'], request.session['designation'], session_role, "PSC Review Form", "PSC review form saved as draft ID-"+json_basicdetails['psc_num']))
                    messages.success(request, "PSC form with PSC No %s saved as draft." %json_basicdetails['psc_num'])
                elif status == 'Submitted':
                    print("User Id: {}, Designation: {}, Role: {}, Action: {}, Message: {}".format(request.session['emp_id'], request.session['designation'], session_role, "PSC Review Form", "PSC review form Submitted ID-"+json_basicdetails['psc_num']))
                    messages.success(request, "PSC form with PSC No %s submitted successfully" %json_basicdetails['psc_num'])
                elif status == 'Rejected':
                    print("User Id: {}, Designation: {}, Role: {}, Action: {}, Message: {}".format(request.session['emp_id'], request.session['designation'], session_role, "PSC Review Form", "PSC review form Rejected ID-"+json_basicdetails['psc_num']))
                    messages.success(request,'PSC form with PSC No %s rejected successfully' %json_basicdetails['psc_num'])
                elif status == 'Approved':
                    print("User Id: {}, Designation: {}, Role: {}, Action: {}, Message: {}".format(request.session['emp_id'], request.session['designation'], session_role, "PSC Review Form", "PSC review form Approved ID-"+json_basicdetails['psc_num']))
                    messages.success(request,'PSC form with PSC No %s approved successfully' %json_basicdetails['psc_num'])
                return HttpResponse("success")
            else:
                messages.error(request,'Error encountered with status code  %s' %ss.status_code)
                sc_log.error('Error encountered with status code  %s' %ss.status_code)
                print("User Id: {}, Designation: {}, Role: {}, Action: {}, Message: {}".format(request.session['emp_id'], request.session['designation'], session_role, "PSC Review Form", "Error in PSC review form submission"))
                print('Error encountered with status code  %s' %ss.status_code)

                return HttpResponse("error")
                

        # else:
        #     # get_apidata(request)
        #     psc_data = list(PSCTable.objects.filter(npa_status=True,id=pk).values(*psc_all_data))
        #     context = {'title': title, 'tenant_image': tenant_image,'psc_data':psc_data,
        #                 "tenant": tenant, "branch_data": branch_data,"ynstatus":ynstatus,'datadisable':datadisable}
        #     return render(request, 'preliminaryscreeningcommittee_review/psc_review.html', context=context)
        else:
            is_api_data = config_data.module.PSC001.is_api_data
    
            cust_id = PSCTable.objects.filter(id=pk).values('cust_id')[0]['cust_id']
            if is_api_data == True:
                customerapi_data = KBLAPIWrapper.CustomerAssetsAPI(cust_id)
                # print('customerapi_data', (customerapi_data))
                if len(customerapi_data) == 1:
                    messages.error(request,'Customer Assets API error : ')
                    return redirect('dashboard')
                elif len(customerapi_data) <= 2:
                    messages.error(request,'Customer Assets API error : returned empty data for basic details, credit sanction & securities table')
                    return redirect('dashboard')
                elif len(customerapi_data) <= 30:
                    messages.error(request,'Customer Assets API error : Data for some tags not returned')
                    return redirect('dashboard')
                elif customerapi_data['HStatus'] == 'FAILURE':
                    messages.error(request,'Customer Assets API error : HStatus failure')
                    return redirect('dashboard')
                else:
                    modifiedData = modify_cust_asst_data(customerapi_data)
                    # print("modifiedData",modifiedData)
                    basic_config = modifiedData['basic_details']
                    credit_config = modifiedData['credit_facility']
                    securities_config = modifiedData['securities_values']
                    psc_data = list(PSCTable.objects.filter(npa_status=True,id=pk).values(*psc_all_data))
                    # return
                    context = {'title': title, 'tenant_image': tenant_image,'psc_data':psc_data,"basic_config":basic_config,"credit_config":credit_config,"securities_config":securities_config,
                                "tenant": tenant, "branch_data": branch_data,"ynstatus":ynstatus,'datadisable':datadisable}
                    return render(request, 'preliminaryscreeningcommittee_review/psc_review.html', context=context)
            else:
                with open("sample_data/basic_details.json", "r") as file:
                    basic_config = json.load(file)
                with open("sample_data/credit_factility.json", "r") as file:
                    credit_config = json.load(file)
                with open("sample_data/securites_values.json", "r") as file:
                    securities_config = json.load(file)
                # get_apidata(request)
                psc_data = list(PSCTable.objects.filter(npa_status=True,id=pk).values(*psc_all_data))
                context = {'title': title, 'tenant_image': tenant_image,'psc_data':psc_data,"basic_config":basic_config,"credit_config":credit_config,"securities_config":securities_config,
                            "tenant": tenant, "branch_data": branch_data,"ynstatus":ynstatus,'datadisable':datadisable}
                print("User Id: {}, Designation: {}, Role: {}, Action: {}, Message: {}".format(request.session['emp_id'], request.session['designation'], session_role, "PSC Review Form", "PSC review form opened"))
                return render(request, 'preliminaryscreeningcommittee_review/psc_review.html', context=context)
    except Exception as e:
        sc_log.error(e)
        messages.error(request, e)
        print("User Id: {}, Designation: {}, Role: {}, Action: {}, Message: {}".format(request.session['emp_id'], request.session['designation'], session_role, "PSC Review Form Error", e))
        # print('PSC review error: ' + str(e))
        return redirect('dashboard')
    
@my_login_required
def psc_update(request,pk,val):
    """
    welcome
    :param request:
    :return:
    """
    config_data = Box(request.session['config_data'])
    tenant = config_data.tenant
    title = config_data.module.PSC001.psc_display_name
    tenant_image = config_data.logo_image.image_path
    ynstatus = config_data.module.PSC001.ynstatus
    datadisable = 'true'
    roles= request.session['new_roles'].split("_")
    session_role = DesignationMatrix.objects.filter(role_code=request.session['new_roles']).values('role_name')[0]['role_name']
    des = DesignationMatrix.objects.filter(role_code=request.session['new_roles']).values('role_name')[0]['role_name']
    branch_data = BranchMaster.objects.filter(branch_code=request.session['branch_code']).values('branch_name', 'zone')
    msgDisplay = False
    try:
        if request.is_ajax() and request.method == 'POST':
            # json
            # psc_form_date = request.POST['psc_form_date']
            json_basicdetails = json.loads(request.POST['json_basicdetails'])
            json_creditsanction = json.loads(request.POST['json_creditsanction'])
            json_securitiesvalues = json.loads(request.POST['json_securitiesvalues'])
            psc_cust_id = request.POST['psc_cust_id']
            past_performance = request.POST['past_performance']
            npa_reasons = request.POST['npa_reasons']
            recovery_steps = request.POST['recovery_steps']
            json_pre_sanction = json.loads(request.POST['json_pre_sanction'])
            json_pre_sanction_sa = json.loads(request.POST['json_pre_sanction_sa'])
            json_post_sanction = json.loads(request.POST['json_post_sanction'])
            json_post_sanction_sa = json.loads(request.POST['json_post_sanction_sa'])
            json_post_sanction_ma = json.loads(request.POST['json_post_sanction_ma'])
            json_sanction_lapses_po = json.loads(request.POST['json_sanction_lapses_po'])
            json_non_fulfillment_tc = json.loads(request.POST['json_non_fulfillment_tc'])
            json_pow_exceeding_insts = json.loads(request.POST['json_pow_exceeding_insts'])
            json_cersai = json.loads(request.POST['json_cersai'])
            json_valua_remarks_varia = json.loads(request.POST['json_valua_remarks_varia'])
            json_sec_availability = json.loads(request.POST['json_sec_availability'])
            json_loan_pro_woc = json.loads(request.POST['json_loan_pro_woc'])
            json_loan_pro_np = json.loads(request.POST['json_loan_pro_np'])
            json_securities_div = json.loads(request.POST['json_securities_div'])
            json_loan_sec_irregularities = json.loads(request.POST['json_loan_sec_irregularities'])
            json_fraud_cases = json.loads(request.POST['json_fraud_cases'])
            json_other_info = json.loads(request.POST['json_other_info'])
            json_aof = json.loads(request.POST['json_aof'])
            json_post_sanc_doc_irregularities = json.loads(request.POST['json_post_sanc_doc_irregularities'])
            json_cgtmse_loan = json.loads(request.POST['json_cgtmse_loan'])
            json_mortgage_notice = json.loads(request.POST['json_mortgage_notice'])
            json_housing_soc_conf = json.loads(request.POST['json_housing_soc_conf'])
            json_post_mort_ec = json.loads(request.POST['json_post_mort_ec'])
            json_all_aod = json.loads(request.POST['json_all_aod'])  
            json_insepction_num = json.loads(request.POST['json_insepction_num'])
            json_staff_data = json.loads(request.POST['json_staff_data'])
            json_ad_sanc_bo = json.loads(request.POST['json_ad_sanc_bo'])
            json_bo_names = json.loads(request.POST['json_bo_names'])
            json_so_sa_name = json.loads(request.POST['json_so_sa_name'])
            json_reject_remarks_data = json.loads(request.POST['json_reject_remarks_data'])
            # print('json_reject_remarks_data',json_reject_remarks_data,len(json_reject_remarks_data))
            
            # json_file_document = json.loads(request.POST['json_file_document'])
            if val == 'approve1' or val == 'approve2' or val == 'approve3':
                json_reject_remarks_div = json.loads(request.POST['json_reject_remarks_div'])
            else:
                json_reject_remarks_div = None
            # print('json_reject_remarks_div',json_reject_remarks_div)
            if val == 'approve1':
                ob_branch_head = request.POST['ob_branch_head']
            else:
                ob_branch_head = PSCTable.objects.filter(id=pk).values('ob_branch_head')
                ob_branch_head = ob_branch_head
            if val == 'edit2':
                ob_regional_head = request.POST['ob_regional_head']
            else:
                ob_regional_head = PSCTable.objects.filter(id=pk).values('ob_regional_head')
                ob_regional_head = ob_regional_head
            if val == 'edit3':
                ob_dept_head = request.POST['ob_dept_head']
            else:
                ob_dept_head = PSCTable.objects.filter(id=pk).values('ob_dept_head')
                ob_dept_head = ob_dept_head
            status = request.POST.get('status')
            files = request.POST['file_values']
            psc_update_data = [{'basic_details':json_basicdetails},{'credit_sanction':json_creditsanction},{'securities_values':json_securitiesvalues},{'past_performance':past_performance},{'npa_reasons':npa_reasons},{'recovery_steps':recovery_steps},{'pre_sanction':json_pre_sanction},{'pre_sanction_lapses_sa':json_pre_sanction_sa},{'post_sanction':json_post_sanction},{'post_sanction_sa':json_post_sanction_sa},{'post_sanction_ma':json_post_sanction_ma},{'sanction_lapses_po':json_sanction_lapses_po},{'non_fulfillment_tc':json_non_fulfillment_tc},{'pow_exceeding_insts':json_pow_exceeding_insts},{'cersai':json_cersai},{'valua_remarks_varia':json_valua_remarks_varia},{'sec_availability':json_sec_availability},{'loan_pro_woc':json_loan_pro_woc},{'loan_pro_np':json_loan_pro_np},{'securities_div':json_securities_div},{'loan_sec_irregularities':json_loan_sec_irregularities},{'fraud_cases':json_fraud_cases},{'other_info':json_other_info},{'aof':json_aof},{'post_sanc_doc_irregularities':json_post_sanc_doc_irregularities},{'cgtmse_loan':json_cgtmse_loan},{'mortgage_notice':json_mortgage_notice},{'housing_soc_conf':json_housing_soc_conf},{'post_mort_ec':json_post_mort_ec},{'all_aod':json_all_aod},{'insepction_num':json_insepction_num},{'staff_data':json_staff_data},{"ad_sanc_bo":json_ad_sanc_bo},{"bo_names":json_bo_names},{"so_sa_name":json_so_sa_name},{'ob_branch_head':ob_branch_head},{'ob_regional_head':ob_regional_head},{'ob_dept_head':ob_dept_head},{'status':status},{'reject_remarks':json_reject_remarks_data},{'reject_remarks_div':json_reject_remarks_div},{'pk':pk},{'files':files},{'role_value':val},{'psc_cust_id':psc_cust_id}]
            # print('psc_update_data',psc_update_data)
            ss = SavetoDB.psc_db_store(request,psc_update_data)
            if val in ['approve1', 'approve2', 'approve3'] and len(json_reject_remarks_data) > 15:
                psc_cust_id = PSCTable.objects.filter(id=pk).values('cust_id')[0]['cust_id']
                # print('psc_cust_id',psc_cust_id)
                PSCTable.objects.filter(cust_id=psc_cust_id).update(npa_status=False,status='Terminated')
                CustomerTable.objects.filter(npa_status=True,cust_id=psc_cust_id).update(npa_status=False,status='Terminated')
                msgDisplay = True
            if ss.status_code == 200:
                if status == 'Draft':
                    print("User Id: {}, Designation: {}, Role: {}, Action: {}, Message: {}".format(request.session['emp_id'], request.session['designation'], session_role, "PSC Review update Form", "PSC review update Form Drafted ID-"+json_basicdetails['psc_num']))
                    messages.success(request, "PSC form with PSC No %s saved as draft." %json_basicdetails['psc_num'])
                elif status == 'Submitted':
                    print("User Id: {}, Designation: {}, Role: {}, Action: {}, Message: {}".format(request.session['emp_id'], request.session['designation'], session_role, "PSC Review update Form", "PSC review update Form Submitted ID-"+json_basicdetails['psc_num']))
                    messages.success(request, "PSC form with PSC No %s submitted successfully" %json_basicdetails['psc_num'])
                elif status == 'Re-submitted':
                    print("User Id: {}, Designation: {}, Role: {}, Action: {}, Message: {}".format(request.session['emp_id'], request.session['designation'], session_role, "PSC Review update Form", "PSC review update Form ReSubmitted ID-"+json_basicdetails['psc_num']))
                    messages.success(request, "PSC form with PSC No %s resubmitted successfully" %json_basicdetails['psc_num'])
                elif status == 'Rejected':
                    # NotifyMail.rejectionMailerFunction(request,json_basicdetails['psc_num'],'PSC',json_reject_remarks_div)
                    # print('msgDisplay',msgDisplay)
                    if msgDisplay == False:
                        print("User Id: {}, Designation: {}, Role: {}, Action: {}, Message: {}".format(request.session['emp_id'], request.session['designation'], session_role, "PSC Review update Form", "PSC review update Form Rejected ID-"+json_basicdetails['psc_num']))
                        messages.success(request,'PSC form with PSC No %s rejected successfully' %json_basicdetails['psc_num'])
                    elif msgDisplay == True:
                        print("User Id: {}, Designation: {}, Role: {}, Action: {}, Message: {}".format(request.session['emp_id'], request.session['designation'], session_role, "PSC Review update Form", "PSC review update Form exceeded maximum number of rejections and the account has been deleted ID-"+json_basicdetails['psc_num']))
                        messages.error(request, "PSC form with PSC No %s exceeded maximum number of rejections and the account has been deleted" %json_basicdetails['psc_num'])
                elif status == 'Approved':
                    print("User Id: {}, Designation: {}, Role: {}, Action: {}, Message: {}".format(request.session['emp_id'], request.session['designation'], session_role, "PSC Review update Form", "PSC review update Form Approved ID-"+json_basicdetails['psc_num']))
                    messages.success(request,'PSC form with PSC No %s approved successfully' %json_basicdetails['psc_num'])
                return HttpResponse("success")
            else:
                messages.error(request,'Error encountered with status code  %s' %ss.status_code)
                sc_log.error('Error encountered with status code  %s' %ss.status_code)
                print("User Id: {}, Designation: {}, Role: {}, Action: {}, Message: {}".format(request.session['emp_id'], request.session['designation'], session_role, "PSC Review Form", "Error in PSC review form submission"))
                print('Error encountered with status code  %s' %ss.status_code)
        else:
            #print('val',val)
            psc_form_data = PSCTable.objects.filter(npa_status=True,id=pk).values(*psc_all_data)
            psc__id = psc_form_data[0]['cust_id']
            psc_instance = CustomerTable.objects.filter(npa_status=True,cust_id=psc__id).values('id')[0]['id']
            psc_rec_id = psc_form_data[0]['psc_rec_id']
            psc_status = psc_form_data[0]['status']
            psc_reject_remarks = psc_form_data[0]['reject_remarks']
            # print('psc_reject_remarks',psc_reject_remarks)
            psc_remarks_count = len(psc_reject_remarks)
            creditsanctiontable_data = CreditFacilityTable.objects.filter(psc_id=psc_instance).values(*creditsanction_all_data)
            # Ensure JSON-serializable data in Python
            
            doc_date_list = [{"i": idx + 1, "doc_date": entry['doc_date'].strftime("%d-%m-%Y")} for idx, entry in enumerate(creditsanctiontable_data)]

            # Output
            # print('doc_date_list',doc_date_list)
            cf_aod_data = [item['cf_aod_data'] for item in creditsanctiontable_data]
            
            # for aod in cf_aod_data:
            #     aod['aodDates'] = aod['borrowerAODDates'].split(', ')
            # for aod in cf_aod_data:
            #     aod['aodDates'] = aod['borrowerAODDate'].split(', ')
            # print('csf_aod',cf_aod_data)
            securitiestable_data = SecuritiesTable.objects.filter(psc_id=psc_instance).values(*securities_all_data)
            # print(securitiestable_data)
            staff_accountability = psc_form_data[0]['staff_accountability']
            
            def process_accountability_data(key_dd, key):
                data = staff_accountability.get(key, [])
                condition = data[0].get(f"{key_dd}") if data else None
                if condition:
                    return data
                else:
                    return []
                
            pre_sanction = process_accountability_data('pre_sanction_lapses_dd', 'pre_sanction')
            pre_sanction_lapses_sa = process_accountability_data('pre_sanction_lapses_sa_dd', 'pre_sanction_lapses_sa')
            post_sanction = process_accountability_data('post_sanction_lapses_dd', 'post_sanction')
            post_sanction_sa = process_accountability_data('post_sanction_lapses_sa_dd', 'post_sanction_sa')
            post_sanction_ma = process_accountability_data('post_sanction_lapses_ma_dd', 'post_sanction_ma')
            sanction_lapses_po = process_accountability_data('sanction_lapses_po_dd', 'sanction_lapses_po')
            non_fulfillment_tc = process_accountability_data('non_fulfillment_tc_dd', 'non_fulfillment_tc')
            pow_exceeding_insts = process_accountability_data('pow_exceeding_insts_dd', 'pow_exceeding_insts')
            cersai = process_accountability_data('cersai_dd', 'cersai')
            valua_remarks_varia = process_accountability_data('valua_remarks_varia_dd', 'valua_remarks_varia')
            sec_availability = process_accountability_data('sec_availability_dd', 'sec_availability')
            loan_pro_woc = process_accountability_data('loan_pro_woc_dd', 'loan_pro_woc')
            loan_pro_np = process_accountability_data('loan_pro_np_dd', 'loan_pro_np')
            securities_div = process_accountability_data('securities_div_dd', 'securities_div')
            loan_sec_irregularities = process_accountability_data('loan_sec_irregularities_dd', 'loan_sec_irregularities')
            fraud_cases = process_accountability_data('fraud_cases_dd', 'fraud_cases')
            other_info = process_accountability_data('other_info_dd', 'other_info')
            aof = process_accountability_data('aof_dd', 'aof')
            post_sanc_doc_irregularities = process_accountability_data('post_sanc_doc_irregularities_dd', 'post_sanc_doc_irregularities')
            cgtmse_loan = process_accountability_data('cgtmse_loan_dd', 'cgtmse_loan')
            mortgage_notice = process_accountability_data('mortgage_notice_dd', 'mortgage_notice')
            housing_soc_conf = process_accountability_data('housing_soc_conf_dd', 'housing_soc_conf')
            post_mort_ec = process_accountability_data('post_mort_ec_dd', 'post_mort_ec')
            all_aod = staff_accountability['all_aod']

            #print(all_aod)
            for aod in all_aod:
                aod['aodDates'] = aod['borrowerAODDate'].split(', ')
            #print('all_aod',all_aod)
            all_aod1 = []
            for doc in doc_date_list:
                for aod in all_aod:
                    if str(doc['i']) == aod['borrowerAODNo']:  # Match 'i' with 'borrowerAODNo'
                        all_aod1.append({
                            'i': doc['i'],
                            'doc_date': doc['doc_date'],
                            'borrowerAODNo': aod['borrowerAODNo'],
                            'borrowerAODDate': aod['borrowerAODDate'],
                            'aodDates': aod['aodDates']
                        })
            #print(all_aod1)
            # return
            insepction_num = staff_accountability['insepction_num']
            staff_data = staff_accountability['staff_data']
            ad_sanc_bo = staff_accountability['ad_sanc_bo']
            bo_names = staff_accountability['bo_names']
            so_sa_name = staff_accountability['so_sa_name']
            
            file_data = fileUpload.file_upload.get_all_documents(app_name, psc_rec_id)
            section_data = list(item['section'] for item in file_data)
            #print('psc_remarks_count',psc_remarks_count,type(psc_remarks_count))

                            # print(f"File Content: {file_content}")
            psc_data = {'title': title, 'tenant_image': tenant_image,"tenant": tenant, "branch_data": branch_data,'doc_date_list':doc_date_list,'psc_data':psc_form_data,'cf_aod_data':cf_aod_data,'creditsanctiontable_data':creditsanctiontable_data,'securitiestable_data':securitiestable_data,'file_data':file_data,'pre_sanction':pre_sanction,'ynstatus':ynstatus,'pre_sanction_lapses_sa':pre_sanction_lapses_sa,'post_sanction':post_sanction,'post_sanction_sa':post_sanction_sa,'post_sanction_ma':post_sanction_ma,'sanction_lapses_po':sanction_lapses_po,'non_fulfillment_tc':non_fulfillment_tc,'pow_exceeding_insts':pow_exceeding_insts,'cersai':cersai,'valua_remarks_varia':valua_remarks_varia,'sec_availability':sec_availability,'loan_pro_woc':loan_pro_woc,'loan_pro_np':loan_pro_np,'securities_div':securities_div,'loan_sec_irregularities':loan_sec_irregularities,'fraud_cases':fraud_cases,'other_info':other_info,'aof':aof,'post_sanc_doc_irregularities':post_sanc_doc_irregularities,'cgtmse_loan':cgtmse_loan,'mortgage_notice':mortgage_notice,'housing_soc_conf':housing_soc_conf,'post_mort_ec':post_mort_ec,'all_aod':all_aod1,'insepction_num':insepction_num,'staff_data':staff_data,'ad_sanc_bo':ad_sanc_bo,'bo_names':bo_names,'so_sa_name':so_sa_name,'section_data':section_data,'datadisable':datadisable,'maker_role':val,'psc_remarks_count':psc_remarks_count, 'des':des}
            print("User Id: {}, Designation: {}, Role: {}, Action: {}, Message: {}".format(request.session['emp_id'], request.session['designation'], session_role, "PSC Review update Form", "PSC review update form opened"))
                
            return render(request, 'preliminaryscreeningcommittee_review/psc_update.html', context=psc_data)
    except Exception as e:
        sc_log.error(e)
        messages.error(request, e)
        print("User Id: {}, Designation: {}, Role: {}, Action: {}, Message: {}".format(request.session['emp_id'], request.session['designation'], session_role, "PSC Review update Form Error", e))
        # print('PSC review error: ' + str(e))
        return redirect('dashboard')
    
#MOM's
@my_login_required
def mom_dashboard(request):
    """
    welcome
    :param request:
    :return:
    """
    config_data = Box(request.session['config_data'])
    tenant = config_data.tenant
    title = 'MOM Dashboard'
    tenant_image = config_data.logo_image.image_path
    branch_data = BranchMaster.objects.filter(branch_code=request.session['branch_code']).values('branch_name', 'zone')
    session_role = DesignationMatrix.objects.filter(role_code=request.session['new_roles']).values('role_name')[0]['role_name']
    try:
        today = datetime.now().date()
        if request.method == 'POST':
            mom_data = MOMTable.objects.values(*mom_all_data).order_by('-active','-last_modified_date')
            PSCmom_data = MOMTable.objects.filter(review_type__in=['PSC1','PSC2']).values(*mom_all_data).order_by('-active','-last_modified_date')
            SACmom_data = MOMTable.objects.filter(review_type='sac').values(*mom_all_data).order_by('-active','-last_modified_date')
            psc_data = list(PSCTable.objects.filter(npa_status=True,current_role='Convener').values('psc_rec_id'))
            sac_data = list(SACTable.objects.filter(psc_rec_id__npa_status=True).values('sac_rec_id'))
            pscmom_search = request.POST.get('pscsearch_mom')
            sacmom_search = request.POST.get('sacsearch_mom')
            #print('_mom_data',pscmom_search,sacmom_search)
            if pscmom_search:
                print("User Id: {}, Designation: {}, Role: {}, Action: {}, Message: {}".format(request.session['emp_id'], request.session['designation'], session_role, "MOM Dashboard", "PSC MOM search option clicked"))
                PSCmom_data = SearchData.search_mom_data(PSCmom_data,pscmom_search)
            elif sacmom_search:
                print("User Id: {}, Designation: {}, Role: {}, Action: {}, Message: {}".format(request.session['emp_id'], request.session['designation'], session_role, "MOM Dashboard", "SAC MOM search option clicked"))
                SACmom_data = SearchData.search_mom_data(SACmom_data,sacmom_search)
            #print('searched data psc/sac')
            PSCmom_paginator = Paginator(PSCmom_data, 10)
            PSCmom_page_number = request.GET.get('page')
            PSCmom_page_obj = PSCmom_paginator.get_page(PSCmom_page_number)
            SACmom_paginator = Paginator(SACmom_data, 10)
            SACmom_page_number = request.GET.get('page')
            SACmom_page_obj = SACmom_paginator.get_page(SACmom_page_number)
            context = {'title': title, 'tenant_image': tenant_image,
                    "tenant": tenant, "branch_data": branch_data,'PSCmom_data':PSCmom_page_obj,'mom_data':mom_data,'SACmom_data':SACmom_page_obj,'psc_data':psc_data,'sac_data':sac_data,'today':today}
            return render(request, 'preliminaryscreeningcommittee_review/mom_dashboard.html', context=context)
        else:
            mom_data = list(MOMTable.objects.values(*mom_all_data).order_by('-active','last_modified_date'))
            PSCmom_data = MOMTable.objects.filter(review_type__in=['PSC1','PSC2']).values(*mom_all_data).order_by('-active','-last_modified_date')
            SACmom_data = MOMTable.objects.filter(review_type='sac').values(*mom_all_data).order_by('-active','-last_modified_date')
            psc_data = list(PSCTable.objects.filter(npa_status=True,current_role='Convener').values('psc_rec_id'))
            sac_data = list(SACTable.objects.filter(psc_rec_id__npa_status=True,current_role="Convener").values('sac_rec_id'))
            #print('not searched data')
            PSCmom_paginator = Paginator(PSCmom_data, 10)
            PSCmom_page_number = request.GET.get('page')
            PSCmom_page_obj = PSCmom_paginator.get_page(PSCmom_page_number)
            SACmom_paginator = Paginator(SACmom_data, 10)
            SACmom_page_number = request.GET.get('page')
            SACmom_page_obj = SACmom_paginator.get_page(SACmom_page_number)
            # print(today)
        # print('other data')
        
            # print('mom_page_obj',mom_page_obj)
            print("User Id: {}, Designation: {}, Role: {}, Action: {}, Message: {}".format(request.session['emp_id'], request.session['designation'], session_role, "MOM Dashboard", "MOM dashboard has been opened"))
            context = {'title': title, 'tenant_image': tenant_image,
                        "tenant": tenant, "branch_data": branch_data,'PSCmom_data':PSCmom_page_obj,'mom_data':mom_data,'SACmom_data':SACmom_page_obj,'psc_data':psc_data,'sac_data':sac_data,'today':today}
            return render(request, 'preliminaryscreeningcommittee_review/mom_dashboard.html', context=context)
    except Exception as e:
        sc_log.error(e)
        print("User Id: {}, Designation: {}, Role: {}, Action: {}, Message: {}".format(request.session['emp_id'], request.session['designation'], session_role, "MOM Dashboard error", e))
        messages.error(request, e)
        return redirect('mom_dashboard')

def get_mom_data(request):
    if request.method == 'POST' and request.is_ajax():
        p_data_id = request.POST.get('p_data_id')
        # Fetch MOM data associated with p_data_id
        try:
            mom_data = list(MOMTable.objects.filter(id=p_data_id).values('id','meeting_id','mom_creation_date__date','mom_date__date','audience'))
            # print('****',list(mom_data))
            return JsonResponse({'mom_edit': (mom_data)})
        except MOMTable.DoesNotExist:
            return JsonResponse({'error': 'MOM data not found'}, status=404)
    return JsonResponse({'error': 'Invalid request'}, status=400)

@my_login_required
def mom_generate(request,review):
    """
    welcome
    :param request:
    :return:
    """
    try:
        if request.is_ajax() and request.method == 'POST':
            # meetingId = request.POST['meetingId']
            momGenerationDate = request.POST['momGenerationDate']
            momDate = request.POST['momDate']
            mom_type = request.POST['mom_type']
            mom_recipients = json.loads(request.POST['mom_recipients'])
            #print(mom_recipients,mom_type)
            mom_data = [{'momGenerationDate':momGenerationDate},{'momDate':momDate},{'audience':mom_recipients}]
            # if not momDate == 'NaN-NaN-NaN' and not mom_recipients == [] and not mom_type == '':
            SavetoDB.mom_db_store(request,mom_data,review)
            # else:
                # messages.error(request,'Enter all details to create MOM')

            # messages.success(request, "MOM template for %s has been generated successfully" %review)
                
            return HttpResponse("success")
        
    except Exception as e:
        # print(e)
        sc_log.error(e)
        messages.error(request,e)
        # print('MOM generate error: ' + str(e))
        return redirect('mom_dashboard')

@my_login_required
def mom_edit(request,pk):
    """
    welcome
    :param request:
    :return:
    """
    try:
        if request.is_ajax() and request.method == 'POST':
            meetingId = request.POST['meetingId']
            momGenerationDate = request.POST['momGenerationDate']
            momDate = request.POST['momDate']
            mom_recipients = json.loads(request.POST['mom_recipients'])
            sessionKey = request.session['ses_key']
            MOMuser_log = {
                    'user': request.session['emp_id'],  
                    'ses_key': sessionKey,
                    'designation': request.session['designation'],
                    'status': 'edited'
                }
            # print(meetingId,
            #      momGenerationDate,
            #      momDate,
            #      mom_recipients)
            # mom_data = [{'meetingId':meetingId},{'momGenerationDate':momGenerationDate},{'momDate':momDate},{'audience':mom_recipients}]
            if not momDate == 'NaN-NaN-NaN' and not mom_recipients == []:
                MOMTable.objects.filter(id=pk).update(
                meeting_id = meetingId,
                mom_creation_date = momGenerationDate,
                mom_date = momDate,
                audience = mom_recipients,
                last_modified_date = datetime.now(), 
                last_modified_user=f"{request.session['emp_name']}({request.session['emp_id']})"
                

            )
                mom_instancelog = MOMTable.objects.get(id=pk)
                update_PSC_SAC_MOM_logs(mom_instancelog, 'createEdit', MOMuser_log,'MOM')
                messages.success(request, "MOM template for has been modified successfully")
            else:
                messages.error(request,'Enter all details to update MOM')
            
                
            return HttpResponse("success")
        # else:
        #     return render(request, 'preliminaryscreeningcommittee_review/mom_dashboard.html')

        
    except Exception as e:
        sc_log.error(e)
        messages.error(request,e)
        # print('MOM generate error: ' + str(e))
        return redirect('mom_dashboard')

@my_login_required
def mom_date_fetch(request, pk):
    """
    Fetch the MOM dates for the given pk.
    """
    mom_to_date = MOMTable.objects.filter(id=pk).values('mom_date')[0]['mom_date']
    active_mom_prior = MOMTable.objects.filter(active=True, mom_date__lt=mom_to_date).order_by('-mom_date').first()
    non_active_mom_prior = datetime(2024, 1, 1)
    if active_mom_prior:
        mom_from_date = active_mom_prior.mom_date
    else:
        mom_from_date = non_active_mom_prior
    return mom_from_date, mom_to_date

@my_login_required
def mom_total_count(request, pk, rev_type):
    config_data = Box(request.session['config_data'])
    psc_mom_limit = config_data.module.PSC001.psc_mom_limit
    mom_from_date, mom_to_date = mom_date_fetch(request, pk)
    
    cust_ids = PSCTable.objects.filter(
                    Q(npa_status=True, current_role='Convener', last_modified_date__range=(mom_from_date, mom_to_date)) | 
                    Q(npa_status=True, mom_id=pk)
                ).values_list('cust_id', flat=True).distinct()
    total_loan_count = 0
    
    if rev_type == 'PSC1':
        for cust_id in cust_ids:
            total_exposure = CustomerTable.objects.filter(npa_status=True,cust_id=cust_id).values_list('total_exposure', flat=True).first()
            if total_exposure and float(total_exposure) < psc_mom_limit:
                total_loan_count += PSCTable.objects.filter(
                    (Q(npa_status=True, current_role='Convener', last_modified_date__range=(mom_from_date, mom_to_date))) | 
                    (Q(npa_status=True, mom_id=pk)),
                    cust_id=cust_id
                ).count()
    
    elif rev_type == 'PSC2':
        for cust_id in cust_ids:
            total_exposure = CustomerTable.objects.filter(npa_status=True,cust_id=cust_id).values_list('total_exposure', flat=True).first()
            if total_exposure and float(total_exposure) >= psc_mom_limit:
                total_loan_count += PSCTable.objects.filter(
                    (Q(npa_status=True, current_role='Convener', last_modified_date__range=(mom_from_date, mom_to_date))) | 
                    (Q(npa_status=True, mom_id=pk)),
                    cust_id=cust_id
                ).count()
    
    elif rev_type == 'sac':
        total_loan_count = SACTable.objects.filter(
            (Q(psc_rec_id__npa_status=True, current_role='Convener', last_modified_date__range=(mom_from_date, mom_to_date))) | 
            (Q(psc_rec_id__npa_status=True, mom_id=pk))
        ).count()
    mom_loan_count = MOMTable.objects.filter(id=pk).values('loan_count')[0]['loan_count']
    if not mom_loan_count:
        loan_count = [{"no_count": 0, "yes_count": 0, "total_count": total_loan_count}]
    elif mom_loan_count:
        loan_yes_count = mom_loan_count[0]['yes_count']
        loan_no_count = mom_loan_count[0]['no_count']
        loan_total_count = mom_loan_count[0]['total_count']
        loan_count = [{"no_count": loan_no_count, "yes_count": loan_yes_count, "total_count": total_loan_count}]
    MOMTable.objects.filter(id=pk).update(loan_count=loan_count)

@my_login_required
def mom_lapses(request, review, pk):
    config_data = Box(request.session['config_data'])
    tenant = config_data.tenant
    title = 'PSC MOM' if review in ['PSC1', 'PSC2'] else 'SAC MOM'
    tenant_image = config_data.logo_image.image_path
    ynstatus = config_data.module.PSC001.ynstatus
    psc_mom_limit = config_data.module.PSC001.psc_mom_limit
    session_role = DesignationMatrix.objects.filter(role_code=request.session['new_roles']).values('role_name')[0]['role_name']

    try:
        if request.is_ajax() and request.method == 'POST':
            pass
        else:
            mom_from_date, mom_to_date = mom_date_fetch(request, pk)
            mom_total_count(request, pk, review)
            mom_data = MOMTable.objects.filter(id=pk, active=True).values(*mom_all_data)
            
            cust_ids = PSCTable.objects.filter(
                Q(npa_status=True, current_role='Convener', last_modified_date__range=(mom_from_date, mom_to_date)) | 
                Q(npa_status=True, mom_id=pk)
            ).values_list('cust_id', flat=True).distinct()
            #print('cust_ids',cust_ids)
            context = {'title': title, 'tenant_image': tenant_image, "tenant": tenant, 'mom_data': mom_data, 'ynstatus': ynstatus, 'review_type': review, 'pk': pk}
            
            if review == 'PSC1':
                psc_data = []
                for cust_id in cust_ids:
                    total_exposure = CustomerTable.objects.filter(npa_status=True,cust_id=cust_id).values_list('total_exposure', flat=True).first()
                    if total_exposure and float(total_exposure) < psc_mom_limit:
                        psc_data += list(
                            PSCTable.objects.filter(
                                (Q(npa_status=True, current_role='Convener', last_modified_date__range=(mom_from_date, mom_to_date))) | 
                                (Q(npa_status=True, mom_id=pk)),
                                cust_id=cust_id
                            ).values(*psc_all_data).order_by('last_modified_date')
                        )
                context['psc_data'] = psc_data
                print("User Id: {}, Designation: {}, Role: {}, Action: {}, Message: {}".format(request.session['emp_id'], request.session['designation'], session_role, "MOM Lapses", "PSC1 MOM Lapses pages has been opened"))
            elif review == 'PSC2':
                psc_data = []
                for cust_id in cust_ids:
                    #print(cust_id)
                    total_exposure = CustomerTable.objects.filter(npa_status=True,cust_id=cust_id).values('total_exposure').first()
                    #print('total_exposure',total_exposure['total_exposure'])
                    if total_exposure and float(total_exposure['total_exposure']) >= psc_mom_limit:
                        #print('in psc2 if',psc_data)
                        psc_data += list(
                            PSCTable.objects.filter(
                                (Q(npa_status=True, current_role='Convener', last_modified_date__range=(mom_from_date, mom_to_date))) | 
                                (Q(npa_status=True, mom_id=pk)),
                                cust_id=cust_id
                            ).values(*psc_all_data).order_by('last_modified_date')
                        )
                    #print('psc2',psc_data)
                context['psc_data'] = psc_data
                print("User Id: {}, Designation: {}, Role: {}, Action: {}, Message: {}".format(request.session['emp_id'], request.session['designation'], session_role, "MOM lapses", "PSC2 MOM lapses has been opened"))
            elif review == 'sac':
                sac_data = list(
                    SACTable.objects.filter(
                        (Q(psc_rec_id__npa_status=True, current_role='Convener', last_modified_date__range=(mom_from_date, mom_to_date))) | 
                        (Q(psc_rec_id__npa_status=True, mom_id=pk))
                    ).values(*sac_all_data).order_by('last_modified_date')
                )
                context['sac_data'] = sac_data
                print("User Id: {}, Designation: {}, Role: {}, Action: {}, Message: {}".format(request.session['emp_id'], request.session['designation'], session_role, "MOM lapses", "SAC MOM lapses has been opened"))
            return render(request, 'preliminaryscreeningcommittee_review/mom_lapses.html', context=context)
    
    except Exception as e:
        sc_log.error(e)
        messages.error(request,e)
        print("User Id: {}, Designation: {}, Role: {}, Action: {}, Message: {}".format(request.session['emp_id'], request.session['designation'], session_role, "MOM lapses error",e))
        return redirect('mom_dashboard')

@my_login_required
def mom_review(request,mom_id,review,pk):
    """
    welcome
    :param request:
    :return:
    """
    config_data = Box(request.session['config_data'])
    tenant = config_data.tenant
    if review == 'PSC1' or review == 'PSC2':
        title = 'PSC MOM Review'
    elif review == 'sac':
        title = 'SAC MOM Review'
    tenant_image = config_data.logo_image.image_path
    psc_mom_limit = config_data.module.PSC001.psc_mom_limit
    session_role = DesignationMatrix.objects.filter(role_code=request.session['new_roles']).values('role_name')[0]['role_name']
    try:
        
        mom_data = (MOMTable.objects.filter(id=mom_id).values(*mom_all_data))
        sessionKey = request.session['ses_key']
        
        if request.is_ajax() and request.method == 'POST':
            mom_loan_count = MOMTable.objects.filter(id=mom_id).values('loan_count')[0]['loan_count']
            loan_yes_count = mom_loan_count[0]['yes_count']
            loan_no_count = mom_loan_count[0]['no_count']
            loan_total_count = mom_loan_count[0]['total_count']
            dd_select = request.POST['dd_select']
            #print(dd_select)
            # return
            pk = request.POST['pk']                      
            review_type = request.POST['review_type']
            mom_id = request.POST['mom_id']
            json_lapses_heads = json.loads(request.POST['json_lapses_heads'])
            json_present_head = json.loads(request.POST['json_present_head'])
            lapses_no_remarks = request.POST['lapses_no_remarks']
            
            if dd_select == 'no':
                loan_no_count += 1
                loan_count1 = [{"no_count": loan_no_count, "yes_count": loan_yes_count, "total_count": loan_total_count}]
                #print('loan_count',loan_count1,mom_id)
                MOMTable.objects.filter(id=mom_id).update(
                    loan_count = loan_count1,
                    last_modified_date = datetime.now(),
                    last_modified_user=f"{request.session['emp_name']}({request.session['emp_id']})"
                )
                
                
                if review_type == 'PSC1' or review_type == 'PSC2':
                    PSCTable.objects.filter(id=pk).update(
                        mom_lapse = dd_select,
                        mom_lapse_desc = lapses_no_remarks,
                        mom_id = mom_id,
                        status = 'Convened',
                        current_role = '',
                        last_modified_date = datetime.now(),
                        last_modified_user=f"{request.session['emp_name']}({request.session['emp_id']})"
                    )
                    psc_rec_id_ = PSCTable.objects.filter(id=pk).values('psc_rec_id')[0]['psc_rec_id']
                    psc_acc_total = PSCTable.objects.filter(psc_rec_id = psc_rec_id_).count()    
                    psc_mom_count = PSCTable.objects.filter(psc_rec_id = psc_rec_id_,mom_lapse__isnull=False).count()  
                    psc_cust_id = PSCTable.objects.filter(id=pk).values('cust_id')[0]['cust_id']
                    psc_mom_lapse_exists = PSCTable.objects.filter(psc_rec_id=psc_rec_id_, mom_lapse='yes').exists() 
                    #print('psc mom',psc_rec_id_,psc_acc_total,psc_mom_count,psc_cust_id,psc_mom_lapse_exists)
                    # return
                    if  psc_acc_total == psc_mom_count and psc_mom_lapse_exists:
                        #print('acc',psc_acc_total,psc_mom_count)
                        psc_yes = PSCTable.objects.filter(psc_rec_id = psc_rec_id_,mom_lapse = 'yes').values('id','creation_date')
                        total_accounts = PSCTable.objects.filter(psc_rec_id = psc_rec_id_,mom_lapse = 'yes').count()
                        
                        today_date = datetime.now().strftime("%d%m%Y")
                        sac_rec_id = f'SAC{psc_cust_id}{today_date}'
                        psc_sanc_list = []
                        for p_id in psc_yes:
                            #print(p_id['id'], p_id['creation_date'])
                            psc_instance = PSCTable.objects.get(id=p_id['id'])
                            psc_sanc_limit = PSCTable.objects.filter(id=p_id['id']).values('sanc_limit')
                            psc_sanc_list.append(psc_sanc_limit)
                            #print(psc_instance,psc_sanc_limit)
                            SACTable(
                                creation_date = datetime.now(),
                                created_user = request.session['emp_id'],
                                psc_rec_id = psc_instance,
                                sac_rec_id = sac_rec_id,
                                psc_date = p_id['creation_date'],
                                mom_lapse = None,
                                mom_lapse_desc = None,
                                mom_br_head = None,
                                mom_id = None,
                                last_modified_date = datetime.now(),
                                last_modified_user=f"{request.session['emp_name']}({request.session['emp_id']})",
                                sac_users_log = {"ro_maker": [], "ro_checker": [],"ho_maker": [], "ho_checker": [], "convener":[]}
                            ).save()
                        total_sanc_limit = sum(item['sanc_limit'] for qs in psc_sanc_list for item in qs)
                         
                        CustomerTable.objects.filter(npa_status=True,cust_id=psc_cust_id).update(sac_details={
                         "acc_count" : total_accounts,"total_exposure" : total_sanc_limit,"current_role" : None,"status" :None,
                        },sac_rec_id=sac_rec_id,status='Convened',current_role='',last_modified_date = datetime.now(),last_modified_user=f"{request.session['emp_name']}({request.session['emp_id']})")
                    
                    else:
                        PSCTable.objects.filter(id=pk).update(
                        mom_lapse = dd_select,
                        mom_lapse_desc = lapses_no_remarks,
                        mom_id = mom_id,
                        status = 'Convened',
                        current_role = '',
                        last_modified_date = datetime.now(),
                        last_modified_user=f"{request.session['emp_name']}({request.session['emp_id']})"
                    )
                    PSCuser_log = {
                    'user': request.session['emp_id'],  
                    'ses_key': sessionKey,
                    'designation': request.session['designation'],
                    'status': 'Not Convened'
                    }
                    print("User Id: {}, Designation: {}, Role: {}, Action: {}, Message: {}".format(request.session['emp_id'], request.session['designation'], session_role, "PSC MOM Review","MOM lapses has been selected as No for the PSC MOM with id "+psc_rec_id_))
                    psc_instancelog = PSCTable.objects.get(id=pk)
                    update_PSC_SAC_MOM_logs(psc_instancelog, 'convener', PSCuser_log,'PSC')
                    # pass
                elif review_type == 'sac':
                    #print('here')
                    SACTable.objects.filter(id=pk).update(
                            mom_lapse = dd_select,
                            mom_lapse_desc = lapses_no_remarks,
                            mom_id = mom_id,
                            status = 'Convened',
                            current_role = '',
                            last_modified_date = datetime.now(),
                            last_modified_user=f"{request.session['emp_name']}({request.session['emp_id']})"
                        )
                    sac_rec_id_ = SACTable.objects.filter(id=pk).values('sac_rec_id')[0]['sac_rec_id']
                    sac_acc_total = SACTable.objects.filter(sac_rec_id = sac_rec_id_).count()    
                    sac_mom_count = SACTable.objects.filter(sac_rec_id = sac_rec_id_,mom_lapse__isnull=False).count()  
                    sac_cust_id = SACTable.objects.filter(id=pk).values('psc_rec_id__cust_id')[0]['psc_rec_id__cust_id'] 
                    #print(sac_rec_id_,sac_acc_total,sac_mom_count,sac_cust_id)
                    # return
                    if  sac_acc_total == sac_mom_count:
                        
                        psc_cust_id = SACTable.objects.filter(id=pk).values('psc_rec_id__cust_id')[0]['psc_rec_id__cust_id'] 
                        customer = CustomerTable.objects.get(cust_id=sac_cust_id)

                        # Update the JSON field
                        if customer.sac_details:
                            sac_details = customer.sac_details
                        else:
                            sac_details = {}

                        sac_details.update({
                            "current_role": '',
                            "status": 'Convened'
                        })

                        # Save the changes
                        customer.sac_details = sac_details
                        customer.last_modified_date = datetime.now()
                        customer.last_modified_user=f"{request.session['emp_name']}({request.session['emp_id']})"
                        customer.sac_review_id = pk
                        customer.save()
                    SACuser_log = {
                    'user': request.session['emp_id'],  
                    'ses_key': sessionKey,
                    'designation': request.session['designation'],
                    'status': 'Not Convened'
                    }
                    print("User Id: {}, Designation: {}, Role: {}, Action: {}, Message: {}".format(request.session['emp_id'], request.session['designation'], session_role, "SAC MOM Review","MOM lapses has been selected as No for the SAC MOM with id "+sac_rec_id_))
                    sac_instancelog = SACTable.objects.get(id=pk)
                    update_PSC_SAC_MOM_logs(sac_instancelog, 'convener', SACuser_log,'SAC')
                    

                    

                messages.success(request, "%s account's lapses have been marked as lapse not found successfully" %review)
            elif dd_select == 'yes':
                #print('in dd yes')
                loan_yes_count += 1
                loan_count = [{"no_count": loan_no_count, "yes_count": loan_yes_count, "total_count": loan_total_count}]
                MOMTable.objects.filter(id=mom_id).update(
                    loan_count = loan_count,
                    last_modified_date = datetime.now(),
                    last_modified_user=f"{request.session['emp_name']}({request.session['emp_id']})"
                )
                MOMuser_log = {
                    'user': request.session['emp_id'],  
                    'ses_key': sessionKey,
                    'designation': request.session['designation'],
                    'status': 'Convened'
                }
                mom_instancelog = MOMTable.objects.get(id=mom_id)
                # update_PSC_SAC_MOM_logs(mom_instancelog, 'convener', MOMuser_log,'MOM')
                if review_type == 'PSC1' or review_type == 'PSC2':
                    PSCTable.objects.filter(id=pk).update(
                        mom_lapse = dd_select,
                        mom_lapse_desc = json_lapses_heads,
                        mom_br_head = json_present_head,
                        mom_id = mom_id,
                        status = 'Convened',
                        current_role = '',
                        last_modified_date = datetime.now(),
                        last_modified_user=f"{request.session['emp_name']}({request.session['emp_id']})"
                    )
                    psc_rec_id_ = PSCTable.objects.filter(id=pk).values('psc_rec_id')[0]['psc_rec_id']
                    psc_acc_total = PSCTable.objects.filter(psc_rec_id = psc_rec_id_).count()    
                    psc_mom_count = PSCTable.objects.filter(psc_rec_id = psc_rec_id_,mom_lapse__isnull=False).count()  
                    psc_cust_id = PSCTable.objects.filter(id=pk).values('cust_id')[0]['cust_id'] 
                    #print(psc_rec_id_,psc_acc_total,psc_mom_count,psc_cust_id)
                    if  psc_acc_total == psc_mom_count:
                        #print('acc',psc_acc_total,psc_mom_count)
                        psc_yes = PSCTable.objects.filter(psc_rec_id = psc_rec_id_,mom_lapse = 'yes').values('id','creation_date')
                        total_accounts = PSCTable.objects.filter(psc_rec_id = psc_rec_id_,mom_lapse = 'yes').count()
                        today_date = datetime.now().strftime("%d%m%Y")
                        sac_rec_id = f'SAC{psc_cust_id}{today_date}'
                        psc_sanc_list = []
                        for p_id in psc_yes:
                            #print(p_id['id'], p_id['creation_date'])
                            psc_instance = PSCTable.objects.get(id=p_id['id'])
                            psc_sanc_limit = PSCTable.objects.filter(id=p_id['id']).values('sanc_limit')
                            psc_sanc_list.append(psc_sanc_limit)
                            #print(psc_instance,psc_sanc_limit)
                            SACTable(
                                creation_date = datetime.now(),
                                created_user = request.session['emp_id'],
                                psc_rec_id = psc_instance,
                                sac_rec_id = sac_rec_id,
                                psc_date = p_id['creation_date'],
                                mom_lapse = None,
                                mom_lapse_desc = None,
                                mom_br_head = None,
                                mom_id = None,
                                last_modified_date = datetime.now(),
                                last_modified_user=f"{request.session['emp_name']}({request.session['emp_id']})",
                                sac_users_log = {"ro_maker": [], "ro_checker": [],"ho_maker": [], "ho_checker": [], "convener":[]}
                            ).save()
                        total_sanc_limit = sum(item['sanc_limit'] for qs in psc_sanc_list for item in qs)
                        CustomerTable.objects.filter(npa_status=True,cust_id=psc_cust_id).update(sac_rec_id=sac_rec_id,sac_details={
                         "acc_count" : total_accounts,"total_exposure" : total_sanc_limit,"current_role" : None,"status" :None,
                        },last_modified_date = datetime.now(),status='Convened',current_role='',last_modified_user=f"{request.session['emp_name']}({request.session['emp_id']})")
                    else:
                        PSCTable.objects.filter(id=pk).update(
                        mom_lapse = dd_select,
                        mom_lapse_desc = json_lapses_heads,
                        mom_br_head = json_present_head,
                        mom_id = mom_id,
                        status = 'Convened',
                        current_role = '',
                        last_modified_date = datetime.now(),
                        last_modified_user=f"{request.session['emp_name']}({request.session['emp_id']})" 
                    )
                    PSCuser_log = {
                    'user': request.session['emp_id'],  
                    'ses_key': sessionKey,
                    'designation': request.session['designation'],
                    'status': 'Convened'
                    }
                    print("User Id: {}, Designation: {}, Role: {}, Action: {}, Message: {}".format(request.session['emp_id'], request.session['designation'], session_role, "PSC MOM Review","MOM lapses has been selected as Yes for the PSC MOM with id "+psc_rec_id_))
                    psc_instancelog = PSCTable.objects.get(id=pk)
                    update_PSC_SAC_MOM_logs(psc_instancelog, 'convener', PSCuser_log,'PSC') 
                    
                elif review_type == 'sac':
                    #print('in sac mom review')
                    SACTable.objects.filter(id=pk).update(
                        mom_lapse = dd_select,
                        mom_lapse_desc = json_lapses_heads,
                        mom_br_head = json_present_head,
                        mom_id = mom_id,
                        status = 'Convened',
                        current_role = '',
                        last_modified_date = datetime.now(),
                        last_modified_user=f"{request.session['emp_name']}({request.session['emp_id']})"
                    )
                    sac_rec_id_ = SACTable.objects.filter(id=pk).values('sac_rec_id')[0]['sac_rec_id']
                    sac_acc_total = SACTable.objects.filter(sac_rec_id = sac_rec_id_).count()    
                    sac_mom_count = SACTable.objects.filter(sac_rec_id = sac_rec_id_,mom_lapse__isnull=False).count()  
                    sac_cust_id = SACTable.objects.filter(id=pk).values('psc_rec_id__cust_id')[0]['psc_rec_id__cust_id'] 
                    #print(sac_rec_id_,sac_acc_total,sac_mom_count,sac_cust_id)
                    # return
                    if  sac_acc_total == sac_mom_count:
                        
                        psc_cust_id = SACTable.objects.filter(id=pk).values('psc_rec_id__cust_id')[0]['psc_rec_id__cust_id'] 
                        customer = CustomerTable.objects.get(cust_id=sac_cust_id)

                        # Update the JSON field
                        if customer.sac_details:
                            sac_details = customer.sac_details
                        else:
                            sac_details = {}

                        sac_details.update({
                            "current_role": '',
                            "status": 'Convened'
                        })

                        # Save the changes
                        customer.sac_details = sac_details
                        customer.last_modified_date = datetime.now()
                        customer.last_modified_user=f"{request.session['emp_name']}({request.session['emp_id']})"
                        customer.sac_review_id = pk
                        customer.save()
                    SACuser_log = {
                    'user': request.session['emp_id'],  
                    'ses_key': sessionKey,
                    'designation': request.session['designation'],
                    'status': 'Convened'
                    }
                    print("User Id: {}, Designation: {}, Role: {}, Action: {}, Message: {}".format(request.session['emp_id'], request.session['designation'], session_role, "SAC MOM Review","MOM lapses has been selected as Yes for the SAC MOM with id "+sac_rec_id_))
                    sac_instancelog = SACTable.objects.get(id=pk)
                    update_PSC_SAC_MOM_logs(sac_instancelog, 'convener', SACuser_log,'SAC')
                    
               
                messages.success(request, "%s account's lapses have been identified successfully" %review)

            
            context = {'title': title, 'tenant_image': tenant_image,
                       "tenant": tenant}
            return render(request, 'preliminaryscreeningcommittee_review/mom_review.html', context=context)
        else:
            if review == 'PSC1' or review == 'PSC2':
                psc_data = (PSCTable.objects.filter(id=pk).values(*psc_all_data))
                psc_no = PSCTable.objects.filter(id=pk).values('cust_id')[0]['cust_id'] 
                psc_instance = CustomerTable.objects.filter(npa_status=True,cust_id=psc_no).values('id')[0]['id']
                creditsanctiontable_data = CreditFacilityTable.objects.filter(psc_id=psc_instance).values(*creditsanction_all_data)
                securitiestable_data = SecuritiesTable.objects.filter(psc_id=psc_instance).values(*securities_all_data)
                staff_accountability = PSCTable.objects.filter(id=pk).values('staff_accountability')[0]['staff_accountability']
                psc_rec_id = PSCTable.objects.filter(id=pk).values('psc_rec_id')[0]['psc_rec_id']
                all_aod = staff_accountability['all_aod']
                file_data = fileUpload.file_upload.get_all_documents(app_name, psc_rec_id)
                section_data = list(item['section'] for item in file_data)
                print("User Id: {}, Designation: {}, Role: {}, Action: {}, Message: {}".format(request.session['emp_id'], request.session['designation'], session_role, "PSC MOM Review","PSC MOM Review form opened"))
                context = {'title': title, 'tenant_image': tenant_image,
                        "tenant": tenant,'psc_data':psc_data,'mom_data':mom_data,'review_type':review,'creditsanctiontable_data':creditsanctiontable_data,'securitiestable_data':securitiestable_data,'all_aod':all_aod,'section_data':section_data,'file_data':file_data}
                return render(request, 'preliminaryscreeningcommittee_review/mom_review.html', context=context)
            elif review == 'sac':
                cust_id = SACTable.objects.filter(id=pk).values('psc_rec_id__cust_id')[0]['psc_rec_id__cust_id']
                psc_instance = CustomerTable.objects.filter(npa_status=True,cust_id=cust_id).values('id')[0]['id']
                creditsanctiontable_data = CreditFacilityTable.objects.filter(psc_id=psc_instance).values(*creditsanction_all_data)
                securitiestable_data = SecuritiesTable.objects.filter(psc_id=psc_instance).values(*securities_all_data)
                sac_data = (SACTable.objects.filter(id=pk).values(*sac_all_data))
                psc_id_ = SACTable.objects.filter(id=pk).values('psc_rec_id')[0]['psc_rec_id']
                staff_accountability = PSCTable.objects.filter(id=psc_id_).values('staff_accountability')[0]['staff_accountability']
                psc_rec_id = PSCTable.objects.filter(id=psc_id_).values('psc_rec_id')[0]['psc_rec_id']
                mom_lapse = PSCTable.objects.filter(id=psc_id_).values('mom_lapse')[0]['mom_lapse']
                mom_lapse_desc = PSCTable.objects.filter(id=psc_id_).values('mom_lapse_desc')[0]['mom_lapse_desc']
                mom_br_head = PSCTable.objects.filter(id=psc_id_).values('mom_br_head')[0]['mom_br_head']
                all_aod = staff_accountability['all_aod']
                file_data = fileUpload.file_upload.get_all_documents(app_name, psc_rec_id)
                section_data = list(item['section'] for item in file_data)
                print("User Id: {}, Designation: {}, Role: {}, Action: {}, Message: {}".format(request.session['emp_id'], request.session['designation'], session_role, "SAC MOM Review","SAC MOM Review form opened"))
                context = {'title': title, 'tenant_image': tenant_image,
                        "tenant": tenant,'sac_data':sac_data,'mom_data':mom_data,'review_type':review,'psc_rec_id':psc_rec_id,'creditsanctiontable_data':creditsanctiontable_data,'securitiestable_data':securitiestable_data,'all_aod':all_aod,'section_data':section_data,'file_data':file_data,'mom_lapse': mom_lapse,'mom_lapse_desc': mom_lapse_desc,'mom_br_head':mom_br_head}
                return render(request, 'preliminaryscreeningcommittee_review/mom_review.html', context=context)
            
    except Exception as e:
        sc_log.error(e)
        # messages.error(request,e)
        print("User Id: {}, Designation: {}, Role: {}, Action: {}, Message: {}".format(request.session['emp_id'], request.session['designation'], session_role, "PSC MOM Review Error",e))
        return redirect('mom_lapses')

@my_login_required
def mom_close(request):
    """
    welcome
    :param request:
    :return:
    """
    try:
        session_role = DesignationMatrix.objects.filter(role_code=request.session['new_roles']).values('role_name')[0]['role_name']

        # config_data = Box(request.session['config_data'])
        if request.is_ajax() and request.method == 'POST':
            
            pk = request.POST['pk']
            mom_closure_date = datetime.now()
            mom_from_date, mom_to_date = mom_date_fetch(request, pk)
            review = MOMTable.objects.filter(id=pk, active=True).values('review_type')[0]['review_type']
            sessionKey = request.session['ses_key']
            config_data = Box(request.session['config_data'])
            psc_mom_limit = config_data.module.PSC001.psc_mom_limit
            cust_ids = list(PSCTable.objects.filter(
                            Q(npa_status=True, current_role='Convener', last_modified_date__range=(mom_from_date, mom_to_date)) | 
                            Q(npa_status=True, mom_id=pk)
                            ).values_list('cust_id', flat=True).distinct())
            if review == 'PSC1':
                cust_ids_data1 = []
                for cust_id in cust_ids:
                    total_exposure = CustomerTable.objects.filter(npa_status=True,cust_id=cust_id).values_list('total_exposure', flat=True).first()
                    if total_exposure and float(total_exposure) < psc_mom_limit:
                        cust_ids_data1 += list(
                            PSCTable.objects.filter(
                                (Q(npa_status=True, current_role='Convener', last_modified_date__range=(mom_from_date, mom_to_date))) | 
                                (Q(npa_status=True, mom_id=pk)),
                                cust_id=cust_id
                            ).values_list('cust_id', flat=True).distinct())

                        for cust_id in cust_ids_data1:
                            if PSCTable.objects.filter(cust_id=cust_id, mom_lapse__isnull=True).exists():
                                messages.error(request, f"Cannot close MOM. Account linked to cust_id {cust_ids_data1} has pending MOM review.")
                                return HttpResponse("failure")
                        MOMTable.objects.filter(id=pk,review_type='PSC1').update(
                            mom_closure_date=mom_closure_date,
                            active=False
                            
                        )
                        MOMuser_log = {
                            'user': request.session['emp_id'],  
                            'ses_key': sessionKey,
                            'designation': request.session['designation'],
                            'status': 'Closed'
                        }
                        print("User Id: {}, Designation: {}, Role: {}, Action: {}, Message: {}".format(request.session['emp_id'], request.session['designation'], session_role, "PSC MOM Close","PSC MOM has beeb closed with ids "+cust_ids))
                        mom_instancelog = MOMTable.objects.get(id=pk)
                        update_PSC_SAC_MOM_logs(mom_instancelog, 'close', MOMuser_log,'MOM')
            elif review == 'PSC2':
                #print('here')
                cust_ids_data2 = []
                for cust_id in cust_ids:
                    #print(cust_id)
                    total_exposure = CustomerTable.objects.filter(npa_status=True,cust_id=cust_id).values('total_exposure').first()
                    #print('total_exposure',total_exposure['total_exposure'])
                    if total_exposure and float(total_exposure['total_exposure']) >= psc_mom_limit:
                        #print('in psc2 if',psc_data)
                        cust_ids_data2 += list(
                            PSCTable.objects.filter(
                                (Q(npa_status=True, current_role='Convener', last_modified_date__range=(mom_from_date, mom_to_date))) | 
                                (Q(npa_status=True, mom_id=pk)),
                                cust_id=cust_id
                            ).values_list('cust_id', flat=True).distinct())

                        for cust_id in cust_ids_data2:
                            if PSCTable.objects.filter(cust_id=cust_id, mom_lapse__isnull=True).exists():
                                messages.error(request, f"Cannot close MOM. Account linked to cust_id {cust_ids_data2} has pending MOM review.")
                                return HttpResponse("failure")
                        MOMTable.objects.filter(id=pk,review_type='PSC2').update(
                            mom_closure_date=mom_closure_date,
                            active=False
                        )
                        MOMuser_log = {
                            'user': request.session['emp_id'],  
                            'ses_key': sessionKey,
                            'designation': request.session['designation'],
                            'status': 'Closed'
                        }
                        print("User Id: {}, Designation: {}, Role: {}, Action: {}, Message: {}".format(request.session['emp_id'], request.session['designation'], session_role, "PSC MOM Close","PSC MOM has beeb closed with ids "+cust_ids))
                        mom_instancelog = MOMTable.objects.get(id=pk)
                        update_PSC_SAC_MOM_logs(mom_instancelog, 'close', MOMuser_log,'MOM')
                    


            elif review == 'sac':
                #print(review)
                cust_ids = list(SACTable.objects.filter(
                Q(psc_rec_id__npa_status=True, current_role='Convener', last_modified_date__range=(mom_from_date, mom_to_date)) | 
                Q(psc_rec_id__npa_status=True, mom_id=pk)
                ).values_list('psc_rec_id__cust_id', flat=True).distinct())
                #print('cust_ids',cust_ids)
                # return
                for cust_id in cust_ids:
                    if SACTable.objects.filter(psc_rec_id__cust_id=cust_id, mom_lapse__isnull=True).exists():
                        messages.error(request, f"Cannot close MOM. Account linked to cust_id {cust_ids} has pending MOM review.")
                        return HttpResponse("failure")
                MOMTable.objects.filter(id=pk).update(
                    mom_closure_date=mom_closure_date,
                    active=False
                )
                MOMuser_log = {
                    'user': request.session['emp_id'],  
                    'ses_key': sessionKey,
                    'designation': request.session['designation'],
                    'status': 'Closed'
                }
                print("User Id: {}, Designation: {}, Role: {}, Action: {}, Message: {}".format(request.session['emp_id'], request.session['designation'], session_role, "SAC MOM Close","SAC MOM has beeb closed with ids "+cust_ids))
                mom_instancelog = MOMTable.objects.get(id=pk)
                update_PSC_SAC_MOM_logs(mom_instancelog, 'close', MOMuser_log,'MOM')
            
            messages.success(request, "MOM template has been closed successfully")
            return HttpResponse("success")
        
    except Exception as e:
        sc_log.error(e)
        messages.error(request,e)
        print("User Id: {}, Designation: {}, Role: {}, Action: {}, Message: {}".format(request.session['emp_id'], request.session['designation'], session_role, "MOM Close error",e))
        return redirect('mom_dashboard')


#Mail Triggers
class NotifyMail:
    def rejectionMailerFunction(request, id, account_type, reject_json):
        try:
            session_role = DesignationMatrix.objects.filter(role_code=request.session['new_roles']).values('role_name')[0]['role_name']
            config_data = Box(request.session['config_data'])
            mail_configuration = config_data.module.PSC001.mail_configuration
            rej_lvl = reject_json[0]['rej_lvl']
            rej_date = reject_json[0]['rej_date']
            rej_remarks = reject_json[0]['rej_remarks']
            # Get email details from the config
            cc = mail_configuration["MAIL_CC"]
            to_address = mail_configuration["TO_MAIL"]
            if account_type == 'PSC':
                rejected_by = PSCTable.objects.filter(psc_rec_id=id).values('last_modified_user')[0]['last_modified_user']
            elif account_type == 'SAC':
                rejected_by = SACTable.objects.filter(sac_rec_id=id).values('last_modified_user')[0]['last_modified_user']
            else:
                rejected_by = ''
            
            # Format the subject and body with dynamic values
            subject = mail_configuration["SUBJECT"].format(type=account_type, id=id)
            body = mail_configuration["BODY_line1"].format(type=account_type, id=id, rejected_by=rejected_by, rejection_date=rej_date) + mail_configuration["BODY_line2"].format(reject_remarks=rej_remarks, reject_level=rej_lvl)
            
            # Set up SMTP server
            server = smtplib.SMTP(mail_configuration['Smtp_Server'], int(mail_configuration['Smtp_Port']))
            server.starttls()
            server.login(mail_configuration["Email_User"], mail_configuration["Email_Password"])
            
            # Create email
            msg = MIMEMultipart()
            msg['From'] = mail_configuration["Email_User"]
            msg['To'] = to_address
            msg['Subject'] = subject
            msg['Cc'] = ', '.join(cc)
            msg.attach(MIMEText(body, 'plain')) 
            
            # Send email
            server.sendmail(mail_configuration["Email_User"], [to_address] + cc, msg.as_string())
            
            print("User Id: {}, Designation: {}, Role: {}, Action: {}, Message: {}".format(request.session['emp_id'], request.session['designation'], session_role, "Mail Trigger","Email sent successfully to"+to_address))
            
        except Exception as e:
            print("User Id: {}, Designation: {}, Role: {}, Action: {}, Message: {}".format(request.session['emp_id'], request.session['designation'], session_role, "Mail Trigger error",e))
        
        finally:
            server.quit()