import base64, os, time, json, re
import pathlib
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from django.conf import settings
from boss_v1 import settings
from boss_v1.settings import base
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from boss_admin.dbutil import generate_session_ses_key, get_ip_address,ad_login_test
from boss_admin.models import  EmployeeMaster, BranchMaster, DesignationMatrix
from box import Box
from .authentication import get_hostname, file_decrpyt_contents, my_login_required


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
    # print(tenant)
    # print(settings.BASE_DIR)
    if os.path.isdir(os.path.join(str(settings.BASE_DIR), "boss_v1/configurations/{}".format('ahana'))):
        with open(os.path.join(str(settings.BASE_DIR), "boss_v1/configurations/{}/{}.config.json".format('ahana','ahana'))) as f:
            config_data = Box(json.load(f))
            # print(os.path.join(str(settings.BASE_DIR), "boss_v1/configurations/{}/{}.config.json".format('ahana','ahana')))
    tenant_image_path = config_data.logo_image.image_path
    tenant_css_path = config_data.global_styles
    title = config_data.module.PSC001.app_name
    try:
        if request.is_ajax() and request.method == 'POST':             
            login_start = time.time()
            _domain_id = request.POST.get('userId')
            _password = request.POST.get('pwd')#check user
            dtstmp = request.POST.get('dtstmp')
           
            # print(base.AD_LOGIN, 'base.AD_LOGIN')
            user = login_verification(_domain_id,_password,dtstmp)
            # print(user)
            if user['msg'] == 'pass':
                # print('login if')
                _ses_key = generate_session_ses_key(_domain_id)
                if _ses_key is False:
                    messages.error(request, 'Please Login Again')
                    return JsonResponse({"msg": 'failure'}, status=200)
                # else:
                #     request.session['ses_key'] = _ses_key
                # print('-----> loading session')
                session_status = load_session(user,request,tenant,_ses_key)
                # print(session_status)
                if session_status == 'success':
                    # print('success')
                    suc_time = time.time()
                    print('****login success time -- ',suc_time-login_start)    
                    return JsonResponse({"msg": 'success'}, status=200)
                elif session_status['msg'] =='title na':
                    # print('failure1')
                    suc_time = time.time()
                    print('****login failed -- time: ',suc_time-login_start)    
                    messages.error(request, 'Matching designation not available')
                    return JsonResponse({"msg": 'failure'}, status=200)
                elif session_status['msg'] =='failure':
                    # print('failure2')
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
            # print(tenant)
            context={"tenant": tenant, "title":title, "tenant_image":tenant_image_path, "tenant_css_path":tenant_css_path}
            return render(request, 'boss_admin/assign_role_page/login.html', context)
    except Exception as e:
        # print(e)
        messages.error(request, 'Incorrect Domain_id Or Password')
        return JsonResponse({"msg": 'failure'}, status=200)
    
        
def load_session(data,request,tenant,_ses_key):
    
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

    
def login_verification(_domain_id,_password,dtstmp):
    # print('here')
    ver_st_time = time.time()
    private_key_file_name = "private_key_" + str(_domain_id) + "_" + str(dtstmp) + ".pem"
    public_key_file_name = "public_key_" + str(_domain_id) + "_" + str(dtstmp) + ".pem"
    key = RSA.importKey(file_decrpyt_contents(settings.BASE_DIR + "/boss_admin/keys/" + private_key_file_name))
    cipher = PKCS1_OAEP.new(key, hashAlgo=SHA256)
    em2 = cipher.decrypt(base64.b64decode(_password))
    em1 = em2.decode('utf-8')
    # print(em2,em1)
    if base.AD_LOGIN == False:
        try:
            user = EmployeeMaster.objects.get(domain_id__iexact=_domain_id, pwd=em1)
            if user:
                emp = EmployeeMaster.objects.filter(domain_id__iexact=_domain_id)\
                        .values("emp_id")#concurrent user login check
                # print(emp[0]['emp_id'])
                if not emp: #get emp_id
                    ii_time = time.time()
                    print(f"****emp verify not found time -- {ii_time-ver_st_time}")
                    #messages.error(request, 'Incorrect Domain_id Or Password')
                    return JsonResponse({"msg": 'fail'}, status=400)
                else:
                    ie_time = time.time()
                    print(f"****emp verify time -- {ie_time-ver_st_time}")
                    data = {"msg": 'success', 'emp_id': emp[0]['emp_id']}
                    return JsonResponse(data, status=200)
            else:
                ee_time = time.time()
                print(f"****emp verify else : time -- {ee_time-ver_st_time}")
                return JsonResponse({"msg": 'fail'}, status=400)
        except Exception as e:
            # print(e)
            exp_time = time.time()
            print(f"****emp verify exp time -- {exp_time-ver_st_time}")
            return JsonResponse({"msg": 'fail'}, status=400)
    else:
        # print(_domain_id,em1)
        user = ad_login_test(_domain_id, em1)
        # print(user, 'j')
        if user != False:
            evt_time = time.time()
            print(f"****emp verify true time -- {evt_time-ver_st_time}")
            # print('not false')
            user['msg'] = 'pass'
            return user
        else:
            evf_time = time.time()
            print(f"****emp verify false time -- {evf_time-ver_st_time}")
            return JsonResponse({"msg": 'fail'}, status=400)

@my_login_required
def home_page(request):
    """
    home_page
    :param request:
    :return:
    """
   
    try:
        h_start_time = time.time()
        # print('Home')
        path = settings.BASE_DIR + "/boss_admin/keys/"
        ['role_name']
        now = time.time()
        tenant = config_data.tenant
        tenant_image_path = config_data.logo_image.image_path
        display_name = config_data.module
        tenant_css_path = config_data.global_styles
        notification_feature = config_data.notification_configurations.required
        directory = config_data.file_folder.file_path
        p = pathlib.Path(directory)
        p.mkdir(parents=True, exist_ok=True)
        # print('Home1')
        if notification_feature == "True":
            notification_count = list(Notification.objects.filter(is_read=False).values('register_role__role_desc').annotate(total=Count('register_role__role_desc')).order_by('total'))
            # print(notification_count)
        else:
            # print('False')
            notification_count = []
            # print(notification_count)
        current_role = DesignationMatrix.objects.filter(role_code=request.session['new_roles']).values('role_name')[0]['role_name']
        h_end_time = time.time()
        print(f"****home page load time -- {h_end_time-h_start_time}")
        print("User Id: {}, Designation: {}, Role: {}, Action: {}, Message: Login Successful".format(request.session['emp_id'], request.session['designation'], current_role, "Login"))
        for f in os.listdir(path):
            if os.stat(os.path.join(path, f)).st_mtime < now - 600:
                os.remove(os.path.join(path, f))
        context={"tenant": tenant, "tenant_image":tenant_image_path, "tenant_css_path":tenant_css_path, 'display_name':display_name, 'notification_count':notification_count, 'notification_feature':notification_feature}
        return render(request, 'boss_admin/assign_role_page/home.html', context)
    except Exception as e:
        # print("------->",e)
        messages.error(request, 'Please Login Again...')
        return redirect('login_page')

