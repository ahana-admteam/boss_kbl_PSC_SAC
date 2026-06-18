"""
dbutil
"""
from datetime import datetime
import random
import socket
from .models import Session, Log
from ldap3 import Server, Connection, SUBTREE, ALL
import json
from boss_admin.models import BranchMaster, EmployeeMaster, EmployeeRegisterRoleMaster
import re
from django.http import HttpResponse
import time

def ad_login_test(_domain_id, _password):
    ldap_url = 'ktktest.com'
    username = _domain_id + '@ktktest.com'
    # print('b try')
    try:
        server = Server(ldap_url, port=389, get_info=ALL)
        conn = Connection(server, user=username, password=_password)
        start_time = time.time()
        conn_status = conn.bind()
        # print(conn_status)
        if conn_status == True:
            # print('in if')
            ldap_base_dn = 'DC=ktktest,DC=COM'
            search_filter = '(&(objectClass=user)(samaccountname='+_domain_id+'))'
            attributes = ['employeeID','givenname', 'mail', 'samaccountname', 'sn', 'physicalDeliveryOfficeName', 'title', 'Department', 'description']
            conn.search(search_base = ldap_base_dn, search_scope = SUBTREE, search_filter = search_filter, attributes = attributes)
            print('after search')
            data = json.loads(conn.response_to_json())
            print(data)
            conn_status = conn.unbind()
            end_time = time.time()
            print(f"****login api response time -- {end_time-start_time}")
            return data
        else:
            return False

        
    except Exception as ex:
        return ex


#generate token
def generate_session_ses_key(_domain_id):
    """
    generate_session_ses_key
    :param _domain_id:
    :return:
    """
    try:
        token = ''.join(random.SystemRandom()
                  .choice([chr(i) for i in range(97,123)]
                  +[chr(i) for i in range(65,90)]
                  +[str(i) for i in range(10)]
                  +[str(_domain_id)]) for _ in range(20))
        session_key = Session(ses_key=token)
        session_key.save()
        return token
    except:
        return False

def get_ip_address():
    """
    get_ip_address
    :return:
    """
    hostname = socket.gethostname()
    ipaddr = socket.gethostbyname(hostname)
    return ipaddr

#title

def inward_title():
    """
    inward_title
    :return:
    """
    title = 'Inward'
    return title

def outward_title():
    """
    outward_title
    :return:
    """
    title = 'Outward'
    return title

def key_title():
    """
    key_title
    :return:
    """
    title = 'Key Movement'
    return title

def branch_title():
    """
    branch_title
    :return:
    """
    title = 'Branch Document'
    return title

def issuance_title():
    """
    issuance_title
    :return:
    """
    title = 'Security Issuance'
    return title

def security_title():
    """
    security_title
    :return:
    """
    title = 'Security Form'
    return title

def suspense_title():
    """
    suspense_title
    :return:
    """
    title = 'Suspense Cash'
    return title

#title
def audit_title():
    """
    audit_title
    :return:
    """
    title = 'Audit'
    return title

def security_equipment_title():
    """
    security_title
    :return:
    """
    title = 'Security Equipment'
    return title

def petty_cash_title():
    """
    security_title
    :return:
    """
    title = 'Teller Cash'
    return title

def complaints_title():
    """
    complaints_title
    :return:
    """
    title = 'Complaint Book'
    return title

def manual_title():
    """
    complaints_title
    :return:
    """
    title = 'Manual Receipt'
    return title

def fixed_asset_title():
    """
    fixed_asset_title
    :return:
    """
    title = 'Fixed Asset'
    return title

def gold_loan_title():
    """
    fixed_asset_title
    :return:
    """
    title = 'Gold Loan'
    return title

def locker_access_title():
    """
    fixed_asset_title
    :return:
    """
    title = 'Locker Access'
    return title

def it_asset_title():
    """
    fixed_asset_title
    :return:
    """
    title = 'IT Assets'
    return title

def asset_management_title():
    """
    fixed_asset_title
    :return:
    """
    title = 'Assets Management'
    return title


#con current login check method
def con_current_login(____emp_id, _status = 'Login'):
    """
    con_current_login
    :param ____emp_id:
    :param _status:
    :return:
    """
    con_user_obj = Log.objects.filter(emp_id=____emp_id, status=_status)\
        .values('ses_key')
    if con_user_obj:
        con_user = con_user_obj[0]
        _ses_key = con_user['ses_key']
        # update Login status to logout
        Log.objects.filter(emp_id=____emp_id, ses_key=_ses_key)\
            .update(in_out=datetime.now(), status='Logout')
        session_del = Session.objects.filter(ses_key=_ses_key)
        if session_del:
            session_del.delete()
            return True
        else:
            return True
    else:
        return False

def emp_validation(domain_id,emp_id,branch_code,email_id,phone,i,request):
    global err_logs
    err_logs=[]
    emp_data=[]
    ph_num="yes"
    
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    if EmployeeMaster.objects.filter(domain_id=domain_id,active=True).exists():
        dm_id = "no"
        err_logs.append("In line "+str(i+1)+" The given domain id "+str(domain_id)+" already exists")
    else:
        dm_id="yes" 
    if BranchMaster.objects.filter(branch_code=branch_code):
        branch_id="yes"
    else:
        branch_id="no"
        err_logs.append("In line "+str(i+1)+" Branch code "+str(branch_code)+" does not exists")
    if EmployeeMaster.objects.filter(emp_id=emp_id).exists():
        em_id="no"
        err_logs.append("In line "+str(i+1)+" The given employee id  "+str(emp_id)+" already exists")
    else:
        em_id="yes"
    try:
        if re.search(regex,email_id):
            email="yes"
    except Exception as e:
        email="no"
        err_logs.append("In line "+str(i+1)+" Invalid email id format "+str(email_id))
    
    try:
        if str(phone)=='nan' or str(phone)=='':
            ph_num="no"
            err_logs.append("In line "+str(i+1)+" Phone number should be between 10 to 12 "+str(phone))
        elif len(str(phone))>=10 and len(str(phone))<=12:
            ph_num="yes"
    except Exception as e:
        ph_num="no"
        err_logs.append("In line "+str(i+1)+" Phone number should be between 10 to 12 "+str(phone))
    if len(err_logs) != 0:
        data = {'err_logs':err_logs,'dm_id':dm_id,'branch_id':branch_id,'email':email,'ph_num':ph_num,'em_id':em_id}
        dump= json.dumps(data)
        return HttpResponse(dump, content_type ="application/json")
    else:
        data = {'err_logs':'success','dm_id':dm_id,'branch_id':branch_id,'email':email,'ph_num':ph_num,'em_id':em_id}
        dump= json.dumps(data)
        return HttpResponse(dump, content_type ="application/json")

def move_employee(id,employee_id,new_branch):
    if EmployeeMaster.objects.filter(sl_no=id,emp_id=employee_id,branch_code=new_branch).exists():
        new_branch ="no"
        print(new_branch)
        data = {'err_logs':'fail'}
        dump= json.dumps(data)
        print(dump)
        return HttpResponse(dump, content_type ="application/json")
    else:
        new_branch ="yes"
        print(new_branch)
        data = {'err_logs':'success'}
        dump= json.dumps(data)
        return HttpResponse(dump, content_type ="application/json")
        #.update(branch_code=new_branch)
        #EmployeeRegisterRoleMaster.objects.filter(emp_id=employee_id).delete()

def branch_validation(branch_code,branch_name,i):
    global err_logs
    branch_list=[]
    err_logs=[]
    try:
        branch_status= list(BranchMaster.objects.values_list('branch_name', flat='True'))
        for j in branch_status:
            branch_list.append(j.lower())
    except Exception as e:
        print(e)
    if BranchMaster.objects.filter(branch_code=branch_code):
        brnch_code = "no"
        err_logs.append("In line "+str(i+1)+" Branch Code "+branch_code+" already exists")    
    else:
        brnch_code ="yes"
    if str(branch_name).lower() in branch_list:   
        err_logs.append("In line "+str(i+1)+" Branch Name "+branch_name+" already exists")
        brnch_name = "no"
    else:
        brnch_name = "yes"

    if len(err_logs) != 0:
        data = {'err_logs':err_logs, 'brnch_code':brnch_code,'brnch_name':brnch_name}
        dump= json.dumps(data)
    else:
        data = {'err_logs':'success','brnch_code':brnch_code,'brnch_name':brnch_name}
        dump= json.dumps(data)
    return HttpResponse(dump, content_type ="application/json")