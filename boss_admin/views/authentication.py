
import base64, os, time, json, re
import pathlib
from tracemalloc import start
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from datetime import datetime
from django.conf import settings
from boss_v1 import settings
from boss_v1.settings import base
#from JSFBDigitalRegistersDev import settings
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from boss_admin.dbutil import complaints_title, generate_session_ses_key, get_ip_address,ad_login_test, gold_loan_title, inward_title, petty_cash_title, security_equipment_title
from boss_admin.models import  EmployeeMaster, EmployeeRegisterRoleMaster, AuditorConnectionMaster, Session
from notifications_app.models import Notification
from django.db.models import Count
from box import Box



def my_login_required(function=None):
    """
    my_login_required
    :param request:
    :return:
    """
    def wrapper(request, *args, **kw):
        if 'ses_key' in request.session:
            ses_key = request.session['ses_key']
            try:
                user = Session.objects.get(ses_key=ses_key)
                if user:
                    return function(request, *args, **kw)
                else:
                    messages.error(request, 'User Doesnt Exist'
                    'Please Check The Login Credentials and Try Again...')
                    return redirect('login_page')
            except Exception as e:
                return error_404(request, e)
        else:
            messages.error(request,
            'You dont have an Active Session..! Please Login Again')
            return redirect('login_page')
    return wrapper


def error_404(request, exception):
    data = {"error": exception}

    return render(request,'boss_admin/error_404.html', data)



# @csrf_exempt
# def login(request):
#     """
#     login
#     :param request:
#     :return:
#     """
#     global user
#     global config_data
#     tenant = get_hostname(request)
#     print(tenant)
#     # try:
#     #     if os.path.isdir(os.path.join(str(settings.BASE_DIR), "/BackUpOldLaptop/Ahana/banking_proj/new_pyVersion/boss_v1/boss_v1/configurations/{}".format(tenant))):
#     #         print('here')
#     #         with open(os.path.join(settings.BASE_DIR, "/boss_v1/boss_v1/configurations/{}/{}.config.json".format(tenant,tenant))) as f:
#     #             config_data = Box(json.load(f))
#     #     else:
#     #         print(os.path.join(settings.BASE_DIR, "/boss_v1/boss_v1/configurations/{}/{}.config.json".format('ahana','ahana')))
#     #         print(settings.BASE_DIR)
#     #         with open(os.path.join("/boss_v1/boss_v1/configurations/{}/{}.config.json".format('ahana','ahana'))) as f:
#     #             config_data = Box(json.load(f))
#     # except Exception as e:
#     #     print(e)
#     #     messages.error(request, 'The config file does not exist' + str(e))
#     #     return JsonResponse({"msg": str(e)}, status=200)
#     print(settings.BASE_DIR)
#     if os.path.isdir(os.path.join(str(settings.BASE_DIR), "/boss_v1/boss_v1/configurations/{}".format(tenant))):
#         with open(os.path.join(str(settings.BASE_DIR), "/boss_v1/boss_v1/configurations/{}/{}.config.json".format(tenant,tenant))) as f:
#             config_data = Box(json.load(f))
#             print(os.path.join(str(settings.BASE_DIR), "/boss_v1/boss_v1/configurations/{}/{}.config.json".format(tenant,tenant)))
#     else:
#         with open(os.path.join(str(settings.BASE_DIR), "/boss_v1/boss_v1/configurations/{}/{}.config.json".format('ahana','ahana'))) as f:
#             config_data = Box(json.load(f))
#             print(os.path.join(str(settings.BASE_DIR), "/boss_v1/boss_v1/configurations/{}/{}.config.json".format('ahana','ahana')))
#     tenant_image_path = config_data.logo_image.image_path
#     tenant_css_path = config_data.global_styles 
#     try:
#         if request.is_ajax() and request.method == 'POST':             
#             _domain_id = request.POST.get('userId')
#             _password = request.POST.get('pwd')#check user
#             dtstmp = request.POST.get('dtstmp')
#             private_key_file_name = "private_key_" + str(_domain_id) + "_" + str(dtstmp) + ".pem"
#             public_key_file_name = "public_key_" + str(_domain_id) + "_" + str(dtstmp) + ".pem"
#             key = RSA.importKey(file_decrpyt_contents(settings.BASE_DIR + "/boss_admin/keys/" + private_key_file_name))
#             cipher = PKCS1_OAEP.new(key, hashAlgo=SHA256)
#             em2 = cipher.decrypt(base64.b64decode(_password))
#             em1 = em2.decode('utf-8')
#             print(base.AD_LOGIN, 'base.AD_LOGIN')
#             if base.AD_LOGIN == False:
#                 user = EmployeeMaster.objects.get(domain_id__iexact=_domain_id, pwd=em1)
#             else:
#                 user = ad_login_test(_domain_id, em1)
#             if user:
                
#                 emp = EmployeeMaster.objects.filter(domain_id__iexact=_domain_id)\
#                     .values("emp_id")#concurrent user login check
                
#                 if not emp: #get emp_id
#                     messages.error(request, 'Incorrect Domain_id Or Password')
#                     return JsonResponse({"msg": 'failure'}, status=200)
#                 __emp_id = emp[0]
#                 ____emp_id = __emp_id['emp_id']
                
#                 _ses_key = generate_session_ses_key(_domain_id)
#                 if _ses_key is False:
#                     messages.error(request, 'Please Login Again')
#                     return JsonResponse({"msg": 'failure'}, status=200)
#                 else:
#                     request.session['ses_key'] = _ses_key#end of generate token
                
#                 data = EmployeeMaster.objects.filter(domain_id__iexact=_domain_id)\
#                     .values("domain_id", "emp_id", "emp_name",
#                     "branch_code", "designation", "active","branch_code__branch_name")
#                 if data:
#                     list1 = data[0]
#                     domain_id = list1['domain_id']
#                     employee_id = list1['emp_id']
#                     emp_name = list1['emp_name']
#                     branch_code = list1['branch_code']
#                     emp_desig_role = list1['designation']
#                     active = list1['active']
#                     branch_name = list1['branch_code__branch_name']
#                     request.session['tenant'] = tenant
#                     request.session['config_data'] = config_data
#                     request.session['emp_id'] = employee_id#move to session
#                     request.session['emp_name'] = emp_name
#                     request.session['branch_code'] = branch_code
#                     request.session['domain_id'] = domain_id
#                     request.session['emp_desig_role'] = emp_desig_role
#                     request.session['active'] = active
#                     request.session['branch_name'] = branch_name
#                     ip_no = get_ip_address() # get ip address
#                     if not ip_no:
#                         return JsonResponse({"msg": 'failure'}, status=200)
                    
#                     emp_user = EmployeeMaster.objects.get(emp_id=employee_id)
                    
#                     new_role_names = EmployeeRegisterRoleMaster.objects.filter(emp_id=employee_id,
#                         is_active=True)\
#                         .values_list('role_id__role_desc' , flat=True)
                    
#                     audit_role_names = AuditorConnectionMaster.objects.filter(emp_id=employee_id,
#                         is_active=True).values_list('role_id__role_desc',flat=True)
#                     if new_role_names and audit_role_names :
#                         new_r = "_".join(new_role_names)
#                         audit_r = "_".join(audit_role_names)
#                         request.session['new_roles'] = new_r
#                         request.session['audit_roles'] = audit_r
#                         return JsonResponse({"msg": 'success'}, status=200)
#                     elif new_role_names:
#                         new_r = "_".join(new_role_names)
#                         request.session['new_roles'] = new_r
#                         request.session['audit_roles'] = ""
#                         return JsonResponse({"msg": 'success'}, status=200)
#                     elif audit_role_names:
#                         audit_r = "_".join(audit_role_names)
#                         request.session['audit_roles'] = audit_r
#                         request.session['new_roles'] = ""
#                         return JsonResponse({"msg": 'success'}, status=200)
#                     else:
#                         return JsonResponse({"msg": 'success'}, status=200)
#                 else:
#                     messages.error(request, 'Incorrect Domain_id Or Password')
#                     return JsonResponse({"msg": 'failure'}, status=200)
#             else:
#                 messages.error(request, 'Incorrect Domain_id Or Password')
#                 return JsonResponse({"msg": 'failure'}, status=200)
#         else:
#             tenant=config_data.tenant
#             print(tenant)
#             context={"tenant": tenant, "tenant_image":tenant_image_path, "tenant_css_path":tenant_css_path}
#             return render(request, 'boss_admin/assign_role_page/login.html', context)
#     except Exception as e:
#         print(e)
#         messages.error(request, 'Incorrect Domain_id Or Password')
#         return JsonResponse({"msg": 'failure'}, status=200)



def file_get_contents(filename):
    with open(settings.BASE_DIR + "/boss_admin/keys/" + filename) as f:
        return f.read()



@csrf_exempt
def file_encrypt(request):
    try:
        user_id = request.POST.get("myid")
        dtstmp = request.POST.get("dtstmp")
        directory = settings.BASE_DIR + "/boss_admin/keys"
        p = pathlib.Path(directory)
        p.mkdir(parents=True, exist_ok=True)
        private_key_file_name = "private_key_" + str(user_id) + "_" + str(dtstmp) + ".pem"
        public_key_file_name = "public_key_" + str(user_id) + "_" + str(dtstmp) + ".pem"
        key_pair = RSA.generate(1024)
        private_key = open(settings.BASE_DIR + f"//boss_admin//keys/" + private_key_file_name, "wb")
        private_key.write(key_pair.exportKey())
        private_key.close()
        public_key = open(settings.BASE_DIR + f"//boss_admin//keys/" + public_key_file_name, "wb")
        public_key.write(key_pair.publickey().exportKey())
        public_key.close()
        a = file_get_contents(public_key_file_name)
        return HttpResponse(str(a))
    except Exception as e:
        print("Exception at file encrypt",e)


def file_decrpyt_contents(filename):
    with open(filename) as f:
        return f.read()


def get_hostname(request):
    hostname = request.get_host().split(':')[0].lower()
    tenant_name = hostname.split('.')[0]
    return tenant_name



@my_login_required
def home_page(request):
    """
    home_page
    :param request:
    :return:
    """
   
    try:
        path = settings.BASE_DIR + "/boss_admin/keys/"
        now = time.time()
        tenant = config_data.tenant
        tenant_image_path = config_data.logo_image.image_path
        display_name = config_data.module
        tenant_css_path = config_data.global_styles
        notification_feature = config_data.notification_configurations.required
        directory = config_data.file_folder.file_path
        p = pathlib.Path(directory)
        p.mkdir(parents=True, exist_ok=True)
        if notification_feature == "True":
            notification_count = list(Notification.objects.filter(is_read=False).values('register_role__role_desc').annotate(total=Count('register_role__role_desc')).order_by('total'))
            # print(notification_count)
        else:
            notification_count = []
            # print(notification_count)

        for f in os.listdir(path):
            if os.stat(os.path.join(path, f)).st_mtime < now - 600:
                os.remove(os.path.join(path, f))
        context={"tenant": tenant, "tenant_image":tenant_image_path, "tenant_css_path":tenant_css_path, 'display_name':display_name, 'notification_count':notification_count, 'notification_feature':notification_feature}
        return render(request, 'boss_admin/assign_role_page/home.html', context)
    except Exception as e:
        print("------->",e)
        messages.error(request, 'Please Login Again...')
        return redirect('login_page')
    


@csrf_exempt
def login(request):
    """
    login
    :param request:
    :return:
    """
    global user
    global config_data
    tenant = get_hostname(request)
    #print(tenant)
    #print(settings.BASE_DIR)
    if os.path.isdir(os.path.join(str(settings.BASE_DIR), "boss_v1/configurations/{}".format(tenant))):
        with open(os.path.join(str(settings.BASE_DIR), "boss_v1/configurations/{}/{}.config.json".format(tenant,tenant))) as f:
            config_data = Box(json.load(f))
    else:
        with open(os.path.join(str(settings.BASE_DIR), "boss_v1/configurations/{}/{}.config.json".format('ahana','ahana'))) as f:
            config_data = Box(json.load(f))
    tenant_image_path = config_data.logo_image.image_path
    tenant_css_path = config_data.global_styles 
    title = config_data.module.PSC001.app_name
    #print('title',title)
    try:
        if request.is_ajax() and request.method == 'POST':
            login_start = time.time()
            _domain_id = request.POST.get('userId')
            _password = request.POST.get('pwd')#check user
            dtstmp = request.POST.get('dtstmp')
            is_api_data = config_data.module.PSC001.is_api_data
            
            user = login_verification(_domain_id,_password,dtstmp, is_api_data)
            
            if is_api_data == False:
                json_data = json.loads(user.content)
                if json_data['msg'] =='success':
                    _ses_key = generate_session_ses_key(_domain_id)
                    if _ses_key is False:
                        messages.error(request, 'Please Login Again')
                        return JsonResponse({"msg": 'failure'}, status=200)
                    session_status = load_session(_domain_id,request,tenant,_ses_key)
                    if session_status =="success":
                        emp_user = EmployeeMaster.objects.get(emp_id=request.session['emp_id'])
                        roles = fetch_roles(request.session['emp_id'],request.session['branch_code'],'loggedin_user_roles')
                        roles_data = json.loads(roles.content)
                        if roles_data['msg'] =='success':
                            request.session['audit_roles'] = roles_data['audit_roles']
                            request.session['new_roles'] = roles_data['user_roles']
                            return JsonResponse({"msg": 'success'}, status=200)
                        else: 
                            messages.error(request, 'Incorrect Domain_id Or Password')
                            return JsonResponse({"msg": 'failure'}, status=200)
                    else:
                        messages.error(request, 'Incorrect Domain_id Or Password')
                        return JsonResponse({"msg": 'failure'}, status=200)
                else:
                    messages.error(request, 'Incorrect Domain_id Or Password')
                    return JsonResponse({"msg": 'failure'}, status=200)
            else:
                if user['msg'] == 'pass':
                    _ses_key = generate_session_ses_key(_domain_id)
                    if _ses_key is False:
                        messages.error(request, 'Please Login Again')
                        return JsonResponse({"msg": 'failure'}, status=200)
                    session_status = load_session_ad(user,request,tenant,_ses_key)
                    if session_status == 'success':
                        suc_time = time.time()
                        print('****login success time -- ',suc_time-login_start)    
                        return JsonResponse({"msg": 'success'}, status=200)
                    elif session_status['msg'] =='title na':
                        suc_time = time.time()
                        print('****login failed -- time: ',suc_time-login_start)    
                        messages.error(request, 'Matching designation not available')
                        return JsonResponse({"msg": 'failure'}, status=200)
                    elif session_status['msg'] =='failure':
                        suc_time = time.time()
                        print('****login fail -- time: ',suc_time-login_start)    
                        messages.error(request, 'Please Login Again')
                        return JsonResponse({"msg": 'failure'}, status=200)
                elif user['msg'] == 'fail':
                    suc_time = time.time()
                    print('****login fail -- time: ',suc_time-login_start)    
                    messages.error(request, 'Incorrect Domain_id Or Password')
                    return JsonResponse({"msg": 'failure'}, status=200)
        else:
            tenant=config_data.tenant
            print(tenant)
            context={"tenant": tenant, "title":title, "tenant_image":tenant_image_path, "tenant_css_path":tenant_css_path}
            return render(request, 'boss_admin/assign_role_page/login.html', context)
    except Exception as e:
        print(e)
        messages.error(request, 'Incorrect Domain_id Or Password')
        return JsonResponse({"msg": 'failure'}, status=200)

def fetch_roles(employee_id,branch,user):
    
    new_r = ""
    audit_r = ""
    if user =='loggedin_user_roles':
        new_role_names = EmployeeRegisterRoleMaster.objects.filter(emp_id=employee_id,
            is_active=True)\
            .values_list('role_id__role_desc' , flat=True)
        audit_role_names = AuditorConnectionMaster.objects.filter(emp_id=employee_id,
        is_active=True).values_list('role_id__role_desc',flat=True)
        if new_role_names and audit_role_names :
            new_r = "_".join(new_role_names)
            audit_r = "_".join(audit_role_names)
            # request.session['new_roles'] = new_r
            # request.session['audit_roles'] = audit_r
            data = {"msg": 'success', 'user_roles': new_r, 'audit_roles':audit_r}
            return JsonResponse(data, status=200)
        elif new_role_names:
            new_r = "_".join(new_role_names)
            audit_r = "_".join(audit_role_names)
            # request.session['new_roles'] = new_r
            # request.session['audit_roles'] = ""
            data = {"msg": 'success', 'user_roles': new_r, 'audit_roles':audit_r}
            return JsonResponse(data, status=200)
        elif audit_role_names:
            new_r = "_".join(new_role_names)
            audit_r = "_".join(audit_role_names)
            # request.session['audit_roles'] = audit_r
            # request.session['new_roles'] = ""
            data = {"msg": 'success', 'user_roles': new_r, 'audit_roles':audit_r}
            return JsonResponse(data, status=200)
        else:
            data = {"msg": 'success', 'user_roles': new_r, 'audit_roles':audit_r}
            return JsonResponse(data, status=200)
    else:
        new_role_names = EmployeeRegisterRoleMaster.objects.filter(emp_id=employee_id,
            is_active=True, branch_code=branch)\
            .values_list('role_id__role_desc' , flat=True)
        audit_role_names = AuditorConnectionMaster.objects.filter(emp_id=employee_id,
        is_active=True).values_list('role_id__role_desc',flat=True)
        new_r = "_".join(new_role_names)
        print(user)
        role_status = check_role(user, new_r)
        roles_data = json.loads(role_status.content)
        if roles_data['msg'] == 'success':
            data = {"msg": 'success'}
            return JsonResponse(data, status=200)
        else:
            data = {"msg": 'failure'}
            return JsonResponse(data, status=400)

        
def check_role(role, user_roles):
    roles= user_roles.split("_")
    print(role)
    print(role, user_roles, roles)
    if role in roles:
        print('success')
        data = {"msg": 'success'}
        return JsonResponse(data, status=200)
    else:
        data = {"msg": 'failure'}
        return JsonResponse(data, status=400)
        
def load_session(_domain_id,request,tenant,_ses_key):
    data = EmployeeMaster.objects.filter(domain_id__iexact=_domain_id)\
                    .values("domain_id", "emp_id", "emp_name",
                    "branch_code", "designation", "active","branch_code__branch_name")
    if data:
        request.session['ses_key'] = _ses_key
        list1 = data[0]
        domain_id = list1['domain_id']
        employee_id = list1['emp_id']
        emp_name = list1['emp_name']
        branch_code = list1['branch_code']
        emp_desig_role = list1['designation']
        active = list1['active']
        branch_name = list1['branch_code__branch_name']
        request.session['tenant'] = tenant
        request.session['config_data'] = config_data
        request.session['emp_id'] = employee_id#move to session
        request.session['emp_name'] = emp_name
        request.session['branch_code'] = branch_code
        request.session['domain_id'] = domain_id
        request.session['emp_desig_role'] = emp_desig_role
        request.session['designation'] = emp_desig_role
        request.session['active'] = active
        request.session['branch_name'] = branch_name
        ip_no = get_ip_address() # get ip address
        print(ip_no,'ip_no')
        if not ip_no:
            return JsonResponse({"msg": 'failure'}, status=200)
        else:
            return "success"
    else:
        # messages.error(request, 'Incorrect Domain_id Or Password')
        return JsonResponse({"msg": 'failure'}, status=200)
    

def load_session_ad(data,request,tenant,_ses_key):
    
    try:
        request.session['ses_key'] = _ses_key
        domain_id = data['entries'][0]['attributes']['sAMAccountName']
        # print(domain_id)
        employee_id = data['entries'][0]['attributes']['employeeID']
        emp_name = data['entries'][0]['attributes']['givenName']
        
        n = int(len(str(emp_name)))
        if emp_name[(n-1)]=='.':
            emp_name = emp_name[:-1]
            emp_name = emp_name.strip()

        branch_code = data['entries'][0]['attributes']['physicalDeliveryOfficeName']
        b_name = BranchMaster.objects.filter(branch_code = branch_code).values('branch_name')
        branch_name = str(b_name[0]['branch_name']).strip()
        if data['entries'][0]['attributes']['title'] != '':
            emp_desig_role = data['entries'][0]['attributes']['title']
            #print(emp_desig_role)
        else:
            return JsonResponse({'msg':'title na'}, status=200)
        
        region_list = BranchMaster.objects.order_by().values_list('zone',flat=True).distinct().exclude(branch_code='001')
        # print(region_list)
        ho_list = ['001']
        if branch_code in ho_list:
            # print('HO')
            role_type = 'Head'
        elif branch_code in region_list:
            # print('RO')
            role_type = 'Region'
        else:
            # print('BO')
            role_type = 'Branch'
        
        if role_type == 'Head':
            department = data['entries'][0]['attributes']['department']
            # print("------> Department",department)
            if department == '':
                return JsonResponse({'msg':'department na'}, status=200)
            else:
                temp = DesignationMatrix.objects.filter(role_type=role_type)
                for i in temp:
                    # print('inside head temp',i.role_dept)
                    dept_sim = sim_check(department,i.role_dept)
                    desig_sim = sim_check(emp_desig_role,i.designations)
                    if dept_sim == True and desig_sim == True:
                        # print('True, True')
                        role = i.role_code
        else:
            temp = DesignationMatrix.objects.filter(role_type=role_type)
            for i in temp:
                desig_sim = sim_check(emp_desig_role,i.designations)
                if desig_sim == True:
                    role = i.role_code
            # temp = DesignationMatrix.objects.filter(role_type=role_type,designations__contains=emp_desig_role).values('role_code')
            # role = temp[0]['role_code']
        # print(temp,role)

        # branch_name = BranchMaster.objects.filter(branch_code=branch_code)[0]['branch_name']
        request.session['tenant'] = tenant
        request.session['config_data'] = config_data
        request.session['emp_id'] = employee_id#move to session
        # print(emp_name)
        request.session['emp_name'] = emp_name
        request.session['branch_code'] = branch_code
        request.session['domain_id'] = domain_id
        request.session['designation'] = emp_desig_role
        request.session['new_roles'] = role
        request.session['branch_name'] = branch_name
        ip_no = get_ip_address() # get ip address
        # print(ip_no,'ip_no')
        if not ip_no:
            # print('no ip available')
            return JsonResponse({"msg": 'failure'}, status=200)
        else:
            # print('ip available')
            return 'success'
    except Exception as e:
        # messages.error(request, 'Incorrect Domain_id Or Password')
        print('session',e)
        messages.error(request, 'Incorrect Domain_id Or Password')
        return JsonResponse({"msg": 'failure'}, status=200)


def sim_check(ad_data,db_data):
    
    if type(db_data) == str:
        # print('str dept sim check')
        if re.sub(r'[^a-zA-Z0-9]','',db_data).lower() == re.sub(r'[^a-zA-Z0-9]','',ad_data).lower():
            # print('str dept sim check true')
            return True
        else:
            # print('str dept sim check false')
            return False
    else:
        # print('str desig sim check')
        # print(db_data)
        for i in db_data:
            # print('designations --->',i)
            if re.sub(r'[^a-zA-Z0-9]','',i).lower() == re.sub(r'[^a-zA-Z0-9]','',ad_data).lower():
                # print('str desig sim check true')
                return True
        return False

    


def login_verification(_domain_id,_password,dtstmp, is_api_data):
    print('here')
    ver_st_time = time.time()
    private_key_file_name = "private_key_" + str(_domain_id) + "_" + str(dtstmp) + ".pem"
    public_key_file_name = "public_key_" + str(_domain_id) + "_" + str(dtstmp) + ".pem"
    key = RSA.importKey(file_decrpyt_contents(settings.BASE_DIR + "/boss_admin/keys/" + private_key_file_name))
    cipher = PKCS1_OAEP.new(key, hashAlgo=SHA256)
    em2 = cipher.decrypt(base64.b64decode(_password))
    em1 = em2.decode('utf-8')
    if is_api_data == False:
        try:
            user = EmployeeMaster.objects.get(domain_id__iexact=_domain_id, pwd=em1)
            if user:
                emp = EmployeeMaster.objects.filter(domain_id__iexact=_domain_id)\
                        .values("emp_id")#concurrent user login check
                print(emp[0]['emp_id'])
                if not emp: #get emp_id
                    #messages.error(request, 'Incorrect Domain_id Or Password')
                    return JsonResponse({"msg": 'fail'}, status=400)
                else:
                    data = {"msg": 'success', 'emp_id': emp[0]['emp_id']}
                    return JsonResponse(data, status=200)
            else:
                return JsonResponse({"msg": 'fail'}, status=400)
        except Exception as e:
            print(e)
            return JsonResponse({"msg": 'fail'}, status=400)
    else:
        user = ad_login_test(_domain_id, em1)
        if user != False:
            evt_time = time.time()
            print(f"****emp verify true time -- {evt_time-ver_st_time}")
            user['msg'] = 'pass'
            return user
        else:
            evf_time = time.time()
            print(f"****emp verify false time -- {evf_time-ver_st_time}")
            return JsonResponse({"msg": 'fail'}, status=400)
