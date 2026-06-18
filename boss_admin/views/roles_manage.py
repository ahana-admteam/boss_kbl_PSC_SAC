from datetime import datetime
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from .authentication import my_login_required
from boss_admin.models import RegistersMaster, EmployeeMaster, RegistersRoleMaster, \
    EmployeeRegisterRoleMaster, BranchMaster, AuditorConnectionMaster,LocationMaster,DesignationMatrix
from box import Box
from django.db.models import Q
import csv
import re
import pandas as pd
import tablib
import json
from tablib import Dataset 
from boss_admin.dbutil import emp_validation, move_employee, branch_validation

    # config_data = Box(request.session['config_data'])
    # tenant = config_data.tenant
    # title = config_data.module.IN001.display_name
    # tenant_image = config_data.logo_image.image_path

@my_login_required
def get_registers_list(request):
    """
    get_registers_list
    """
    config_data = Box(request.session['config_data'])
    tenant = config_data.tenant
    tenant_image = config_data.logo_image.image_path
    title = config_data.module.AD001.display_name.admin
    register_roles = config_data.module.AD001.properties.register_role_master
    registers = config_data.module.AD001.properties.register_master
    try:
        registers_list = RegistersMaster.objects.\
            exclude(registers_code__in=['AD001', 'KEY001', 'MR001', 'LAR001'])
        registers_role_list = RegistersRoleMaster.objects\
            .exclude(registers_code="AD001")
        branch_code = request.session['branch_code']
        employee_list = EmployeeMaster.objects.filter(branch_code=branch_code,
                active=True).values("emp_id", "emp_name",
         "designation","branch_code","designation").order_by('emp_name')\
            .exclude(designation='IT-Admin')#get emp from db
        list2 = EmployeeRegisterRoleMaster.objects\
            .filter(branch_code=request.session['branch_code'],
             is_active=True).values('is_active', 'emp_reg_role_id', 'registers_code',
                                    'role_id', 'emp_id', 'registers_code__registers_type',
                                    'role_id__role_name','role_id__role_desc','emp_id__emp_name')\
            .exclude(registers_code="AD001")
        context = {'registers_list': registers_list, 'employee_list': employee_list,
                   'registers_role_list': registers_role_list,'emp_reg_role_list': list2, 'tenant_image': tenant_image, "tenant":tenant, 
                   "title":title, 'register_roles':register_roles, "registers":registers}
        return render(request, 'boss_admin/assign_role_page/branch_admin_page.html', context)
    except Exception as e:
        # raise
        messages.error(request, 'error: internal server error')
        return redirect('role_assign_page')


@csrf_exempt
@my_login_required
def add_role(request):
    """
    add_role
    """
    try:
        if request.method == "POST":
            _registers_code = request.POST.get('register_dropdown')
            if not _registers_code:
                messages.error(request, 'register not selected from the dropdown')
            _registers_role_desc = request.POST.get('registers_role_dropdown')
            if not _registers_role_desc:
                messages.error(request, 'role not selected from the dropdown')
            _employee_id = request.POST.get('employee_dropdown')
            if not _employee_id:
                messages.error(request, 'employee not selected from the dropdown')
            _assigner_id = request.session['emp_id']
            _assigner_role = request.session['emp_desig_role']
            _branch_code = request.session['branch_code']
            branch=BranchMaster.objects.filter(branch_code=_branch_code).values_list('sl_no', flat=True)
            if (((_registers_role_desc == "in001receiver" or "in001approver") and _registers_code == "IN001") 
                or ((_registers_role_desc == "out001sender" or "out001approver") and _registers_code == "OUT001")  
                or ((_registers_role_desc == "ss001maintainer" or "ss001verifier") and _registers_code == "SS001") 
                or ((_registers_role_desc == "is001issuer" or "is001verifier") and _registers_code == "IS001") 
                or ((_registers_role_desc == "seq001checker" or "seq001maker") and _registers_code == "SEQ001")
                or ((_registers_role_desc == "pc001maker" or "pc001approver") and _registers_code == "PC001")
                or ((_registers_role_desc == "gl001maker" or "gl001approver") and _registers_code == "GL001")
	        or ((_registers_role_desc == "lar001oic" or "lar001jc") and _registers_code == "LAR001")
                or ((_registers_role_desc == "cr001maker" or "cr001approver") and _registers_code == "CR001")):
                count = EmployeeRegisterRoleMaster.objects.filter(emp_id=_employee_id, registers_code__registers_code=_registers_code,
                            is_active=True,branch_code=_branch_code).count()
                if count == 0:
                    if not EmployeeRegisterRoleMaster.objects.filter(emp_id=_employee_id,
                                role_id__role_desc=_registers_role_desc,is_active=True).exists():
                        emp_user = EmployeeMaster.objects.get(emp_id=_employee_id)
                        reg_user = RegistersMaster.objects.get(registers_code=_registers_code)
                        registers_role_user = RegistersRoleMaster.objects\
                            .get(role_desc=_registers_role_desc)
                        branch_user = BranchMaster.objects.get(branch_code=_branch_code)
                        saved_data = EmployeeRegisterRoleMaster(emp_id=emp_user,
                        registers_code=reg_user,role_id=registers_role_user,
                        created_user_id=_assigner_id,designation=_assigner_role,
                        branch_code=branch_user,modified_user_id=request.session['emp_id'], modified_date=datetime.now(), branch_id_id=branch[0])
                        saved_data.save()
                        messages.success(request, 'Role assigned successfully')
                        return redirect('role_assign_page')
                else:
                    messages.error(request, 'Role already exists for this user')
                    return redirect('role_assign_page')

            if (_registers_role_desc == 'doc001custodian' and _registers_code == "DOC001"):
                count = EmployeeRegisterRoleMaster.objects.filter(role_id__role_desc=_registers_role_desc,
                            is_active=True,branch_code=_branch_code).count()
                if count <= 1:
                    if not EmployeeRegisterRoleMaster.objects.filter(emp_id=_employee_id,
                                role_id__role_desc=_registers_role_desc,is_active=True).exists():
                        emp_user = EmployeeMaster.objects.get(emp_id=_employee_id)
                        reg_user = RegistersMaster.objects.get(registers_code=_registers_code)
                        registers_role_user = RegistersRoleMaster.objects\
                            .get(role_desc=_registers_role_desc)
                        branch_user = BranchMaster.objects.get(branch_code=_branch_code)
                        saved_data = EmployeeRegisterRoleMaster(emp_id=emp_user,
                        registers_code=reg_user,role_id=registers_role_user,
                        created_user_id=_assigner_id,designation=_assigner_role,
                        branch_code=branch_user, modified_user_id=request.session['emp_id'], modified_date=datetime.now(), branch_id_id=branch[0])
                        saved_data.save()
                        messages.success(request, 'Role assigned successfully')
                        return redirect('role_assign_page')
                    messages.error(request, 'Role already exists for this user')
                    return redirect('role_assign_page')
                else:
                    messages.error(request, 'Role already exists with two users')
                    return redirect('role_assign_page')

            if _registers_role_desc == 'far001verifier' and _registers_code == "FAR001":
                if not EmployeeRegisterRoleMaster.objects.filter(emp_id=_employee_id,role_id__role_desc=_registers_role_desc,is_active=True).exists():
                    emp_user = EmployeeMaster.objects.get(emp_id=_employee_id)
                    reg_user = RegistersMaster.objects.get(registers_code=_registers_code)
                    registers_role_user = RegistersRoleMaster.objects.get(role_desc=_registers_role_desc)
                    branch_user = BranchMaster.objects.get(branch_code=_branch_code)
                    saved_data = EmployeeRegisterRoleMaster(emp_id=emp_user,
                                                            registers_code=reg_user, role_id=registers_role_user,
                                                            created_user_id=_assigner_id, designation=_assigner_role,
                                                            branch_code=branch_user, modified_user_id=request.session['emp_id'], modified_date=datetime.now(), branch_id_id=branch[0])
                    saved_data.save()
                    messages.success(request, 'Role assigned successfully')
                    return redirect('role_assign_page')
                else:
                    messages.error(request, 'Role already exists for this user')
                    return redirect('role_assign_page')

            if _registers_role_desc == 'ita001verifier' and _registers_code == "ITR001":
                if not EmployeeRegisterRoleMaster.objects.filter(emp_id=_employee_id,role_id__role_desc=_registers_role_desc,is_active=True).exists():
                    emp_user = EmployeeMaster.objects.get(emp_id=_employee_id)
                    reg_user = RegistersMaster.objects.get(registers_code=_registers_code)
                    registers_role_user = RegistersRoleMaster.objects.get(role_desc=_registers_role_desc)
                    branch_user = BranchMaster.objects.get(branch_code=_branch_code)
                    saved_data = EmployeeRegisterRoleMaster(emp_id=emp_user,
                                                            registers_code=reg_user, role_id=registers_role_user,
                                                            created_user_id=_assigner_id, designation=_assigner_role,
                                                            branch_code=branch_user, modified_user_id=request.session['emp_id'], modified_date=datetime.now(), branch_id_id=branch[0])
                    saved_data.save()
                    messages.success(request, 'Role assigned successfully')
                    return redirect('role_assign_page')
                else:
                    messages.error(request, 'Role already exists for this user')
                    return redirect('role_assign_page')
            count = EmployeeRegisterRoleMaster.objects.filter(emp_id=_employee_id,
                                                            registers_code__registers_code=_registers_code,
                            is_active=True,branch_code=_branch_code).count()
            
            if count != 0:
                
                if _registers_role_desc in ('sc001cashier','sc001ah'):
                    
                    if not EmployeeRegisterRoleMaster.objects.filter(emp_id=_employee_id,role_id__role_desc__in=('sc001jcic', 'sc001jch')).exists():
                        if not EmployeeRegisterRoleMaster.objects.filter(emp_id=_employee_id,
                                                                        role_id__role_desc=_registers_role_desc,
                                                                        is_active=True).exists():
                            emp_user = EmployeeMaster.objects.get(emp_id=_employee_id)
                            reg_user = RegistersMaster.objects.get(registers_code=_registers_code)
                            registers_role_user = RegistersRoleMaster.objects \
                                .get(role_desc=_registers_role_desc)
                            branch_user = BranchMaster.objects.get(branch_code=_branch_code)
                            saved_data = EmployeeRegisterRoleMaster(emp_id=emp_user,
                                                                    registers_code=reg_user, role_id=registers_role_user,
                                                                    created_user_id=_assigner_id, designation=_assigner_role,
                                                                    branch_code=branch_user, modified_user_id=request.session['emp_id'], modified_date=datetime.now(), branch_id_id=branch[0])
                            saved_data.save()
                            messages.success(request, 'Role assigned successfully')
                            return redirect('role_assign_page')
                        else:
                            messages.error(request, 'Role already exists for this user')
                            return redirect('role_assign_page')
                    else:
                        messages.error(request, 'Role already exists for this user')
                        return redirect('role_assign_page')
                elif _registers_role_desc in ('sc001jcic', 'sc001jch'):
                    
                    if not EmployeeRegisterRoleMaster.objects.filter(emp_id=_employee_id,role_id__role_desc__in=('sc001cashier','sc001ah')).exists():
                        if not EmployeeRegisterRoleMaster.objects.filter(emp_id=_employee_id,
                                                                        role_id__role_desc=_registers_role_desc,
                                                                        is_active=True).exists():
                            emp_user = EmployeeMaster.objects.get(emp_id=_employee_id)
                            reg_user = RegistersMaster.objects.get(registers_code=_registers_code)
                            registers_role_user = RegistersRoleMaster.objects \
                                .get(role_desc=_registers_role_desc)
                            branch_user = BranchMaster.objects.get(branch_code=_branch_code)
                            saved_data = EmployeeRegisterRoleMaster(emp_id=emp_user,
                                                                    registers_code=reg_user,
                                                                    role_id=registers_role_user,
                                                                    created_user_id=_assigner_id,
                                                                    designation=_assigner_role,
                                                                    branch_code=branch_user,modified_user_id=request.session['emp_id'], modified_date=datetime.now(), branch_id_id=branch[0])
                            saved_data.save()
                            messages.success(request, 'Role assigned successfully')
                            return redirect('role_assign_page')
                        else:
                            messages.error(request, 'Role already exists for this user')
                            return redirect('role_assign_page')
                    else:
                        messages.error(request, 'Role already exists for this user')
                        return redirect('role_assign_page')
                else:
                    
                    if not EmployeeRegisterRoleMaster.objects.filter(emp_id=_employee_id,
                                                                    role_id__role_desc=_registers_role_desc,
                                                                    is_active=True).exists():
                        emp_user = EmployeeMaster.objects.get(emp_id=_employee_id)
                        reg_user = RegistersMaster.objects.get(registers_code=_registers_code)
                        registers_role_user = RegistersRoleMaster.objects \
                            .get(role_desc=_registers_role_desc)
                        branch_user = BranchMaster.objects.get(branch_code=_branch_code)
                        saved_data = EmployeeRegisterRoleMaster(emp_id=emp_user,
                                                                registers_code=reg_user, role_id=registers_role_user,
                                                                created_user_id=_assigner_id,
                                                                designation=_assigner_role,
                                                                branch_code=branch_user,modified_user_id=request.session['emp_id'], modified_date=datetime.now(), branch_id_id=branch[0])
                        saved_data.save()
                        messages.success(request, 'Role assigned successfully')
                        return redirect('role_assign_page')
                    else:
                        messages.error(request, 'Role already exists for this user')
                        return redirect('role_assign_page')
            elif count == 0:
                
                if not EmployeeRegisterRoleMaster.objects.filter(emp_id=_employee_id,
                                                                role_id__role_desc=_registers_role_desc,
                                                                is_active=True).exists():
                    emp_user = EmployeeMaster.objects.get(emp_id=_employee_id)
                    reg_user = RegistersMaster.objects.get(registers_code=_registers_code)
                    registers_role_user = RegistersRoleMaster.objects \
                        .get(role_desc=_registers_role_desc)
                    branch_user = BranchMaster.objects.get(branch_code=_branch_code)
                    saved_data = EmployeeRegisterRoleMaster(emp_id=emp_user,
                                                            registers_code=reg_user, role_id=registers_role_user,
                                                            created_user_id=_assigner_id, designation=_assigner_role,
                                                            branch_code=branch_user,modified_user_id=request.session['emp_id'], modified_date=datetime.now(), branch_id_id=branch[0])
                    saved_data.save()
                    messages.success(request, 'Role assigned successfully')
                    return redirect('role_assign_page')
                else:
                    messages.error(request, 'Role already exists for this user')
                    return redirect('role_assign_page')
            else:
                messages.error(request, 'Role already exists for this user')
                return redirect('role_assign_page')

    except Exception as e :
        messages.error(request, 'Failed to assign the role')
        return redirect('role_assign_page')


@csrf_exempt
@my_login_required
def delete_roles(request):
    """
    delete_roles
    :param request:
    :return:
    """
    try:
        id_no = request.POST.get('value')
        EmployeeRegisterRoleMaster.objects.filter(emp_reg_role_id=id_no).delete()
        messages.success(request, 'deleted successfully')
        return HttpResponse('deleted')
    except:
        # raise
        messages.error(request, 'failed to delete')
        return HttpResponse('error')


# @my_login_required
def app_admin(request):
    """
    app_admin
    :param request:
    :return:
    """
    config_data = Box(request.session['config_data'])
    tenant = config_data.tenant
    tenant_image = config_data.logo_image.image_path
    title = config_data.module.AD001.display_name.admin
    admin_roles = config_data.module.AD001.properties.register_role_master

    try:#filter on admin
        registers_list = RegistersMaster.objects.filter(registers_code='AD001')
        registers_role_list = RegistersRoleMaster.objects.filter(registers_code='AD001')\
            .exclude(role_desc__in=['ad001appadmin'])
        branch_list = BranchMaster.objects.filter(active=True)#get branch list
        employee_list = EmployeeMaster.objects.filter(active=True)\
            .values("emp_id", "emp_name", "designation",
            "branch_code").order_by('emp_name').exclude(
            designation__in=['IT-Admin', 'Internal Audit'])  # get employess from db
        list3 = EmployeeRegisterRoleMaster.objects.filter(registers_code='AD001',
                is_active=True).values('is_active','emp_reg_role_id','registers_code',
                'role_id','emp_id','registers_code__registers_type','role_id__role_name','role_id__role_desc',
                'emp_id__emp_name','branch_code__branch_name').exclude(emp_reg_role_id=1)
        list4 = AuditorConnectionMaster.objects.filter(registers_code='AD001', is_active=True)\
            .values('is_active','emp_reg_role_id','registers_code','role_id','emp_id',
                    'registers_code__registers_type','role_id__role_name','role_id__role_desc',
            'emp_id__emp_name','branch_code__branch_name').exclude(emp_reg_role_id=1)#.order_by('id')
        context={'registers_list': registers_list,'registers_role_list': registers_role_list,
                 'branch_list': branch_list,'emp_reg_role_list4': list4,
                   'employee_list': employee_list,'emp_reg_role_list': list3, 'tenant_image': tenant_image, "tenant":tenant, "title":title, "admin_roles":admin_roles}
        return render(request, 'boss_admin/assign_role_page/app_admin_page.html', context)
    except:
        # raise
        messages.error(request, 'error: internal server error')
        return redirect('app_admin')


@csrf_exempt
@my_login_required
def add_branch_admin(request):
    """
    add_branch_admin
    :param request:
    :return:
    """
    try:
        if request.method == "POST":
            _registers_code = request.POST['register_dropdown']
            _registers_role_id = request.POST['registers_role_dropdown']
            if not _registers_role_id:
                messages.error(request, 'role not selected from the dropdown')
            _branch_code = request.POST['branch_dropdown']
            if not _branch_code:
                messages.error(request, 'please select Branch from the dropdown')
            _employee_id = request.POST['employee_dropdown']
            #print(_employee_id)
            if not _employee_id:
                    messages.error(request, 'please select an employee from the dropdown')
            _assigner_id = request.session['emp_id']
            _assigner_role = request.session['emp_desig_role']
            branch=BranchMaster.objects.filter(branch_code=_branch_code).values_list('sl_no', flat=True)
            if _registers_role_id =="34" or _registers_role_id=="7" or _registers_role_id=="61":
                
                if not EmployeeRegisterRoleMaster.objects.filter(emp_id=_employee_id,
                                    role_id=_registers_role_id,is_active=True).exists():
                    emp_user = EmployeeMaster.objects.get(emp_id=_employee_id)
                    reg_user = RegistersMaster.objects.get(registers_code=_registers_code)
                    reg_role_user = RegistersRoleMaster.objects.get(role_id=_registers_role_id)
                    branch_user = BranchMaster.objects.get(branch_code=_branch_code)
                    saved_data=EmployeeRegisterRoleMaster(emp_id=emp_user,registers_code=reg_user,
                    role_id=reg_role_user,created_user_id=_assigner_id,designation=_assigner_role,
                                                        branch_code=branch_user,modified_user_id=request.session['emp_id'], modified_date=datetime.now(), branch_id_id=branch[0])
                    saved_data.save()
                    messages.success(request, 'Role assigned successfully')
                    return redirect('app_admin')
                messages.error(request, 'Role already exists for this user')
                return redirect('app_admin')
            else:
                _assigner_id = request.session['emp_id']
                _assigner_role = request.session['emp_desig_role']
                _assigner_branch_code = request.session['branch_code']

                emp_exists = AuditorConnectionMaster.objects.filter(emp_id = _employee_id,
                    is_active = True).values('role_id','role_id__role_name')
                if emp_exists:
                    xyz = emp_exists[0]
                    result1 = xyz['role_id']
                    result2 = xyz['role_id__role_name']
                    if str(result1) != _registers_role_id:
                        messages.error(request, 'You have an active role as ' + str(result2))
                        return redirect('app_admin')

                    assigned_emp=AuditorConnectionMaster.objects.filter(role_id=_registers_role_id,
                            branch_code=_branch_code,is_active=True).values('emp_id__emp_name')
                    if assigned_emp:
                        xyz = assigned_emp[0]
                        result1 = xyz['emp_id__emp_name']
                        messages.error(request, 'Role you are assigning has already exists with '
                                    + str(result1))
                        return redirect('app_admin')
                    else:
                        role_iddd = AuditorConnectionMaster.objects.filter(emp_id=_employee_id,
                                    is_active=True,branch_code=_branch_code)\
                            .values('role_id','role_id__role_name',
                            'branch_code__branch_name')
                        if role_iddd:
                            xyz = role_iddd[0]
                            result1 = xyz['role_id']
                            role_name = xyz['role_id__role_name']
                            branch_name = xyz['branch_code__branch_name']
                            result = str(result1)
                            if result == _registers_role_id:
                                if not AuditorConnectionMaster.objects.filter(emp_id=_employee_id,
                                    role_id=_registers_role_id,branch_code = _branch_code,
                                                is_active=True).exists():
                                    emp_user = EmployeeMaster.objects.get(emp_id=_employee_id)
                                    reg_user = RegistersMaster.objects\
                                        .get(registers_code=_registers_code)
                                    registers_role_user = RegistersRoleMaster.objects\
                                        .get(role_id=_registers_role_id)
                                    branch_user = BranchMaster.objects.get(branch_code=_branch_code)

                                    saved_data = AuditorConnectionMaster(emp_id=emp_user,
                                    registers_code=reg_user,role_id=registers_role_user,
                                    created_user_id=_assigner_id,designation=_assigner_role,
                                    branch_code=branch_user,assigner_branch_code_id=_assigner_branch_code,modified_user_id=request.session['emp_id'], modified_date=datetime.now(),branch_id_id=branch[0])
                                    saved_data.save()
                                    messages.success(request, 'Role assigned successfully')
                                    return redirect('app_admin')
                                messages.error(request,
                                'Role for this branch has already exists for this user')
                                return redirect('app_admin')
                            else:
                                messages.error(request, 'You have an Active role as: '+ str(role_name)+
                                            ' for '+ str(branch_name)+' branch')
                                return redirect('app_admin')
                        else:
                            if not AuditorConnectionMaster.objects.filter(emp_id=_employee_id,
                                role_id=_registers_role_id,branch_code=_branch_code,is_active=True)\
                                    .exists():
                                emp_user = EmployeeMaster.objects.get(emp_id=_employee_id)
                                reg_user = RegistersMaster.objects.get(registers_code=_registers_code)
                                registers_role_user = RegistersRoleMaster.objects\
                                    .get(role_id=_registers_role_id)
                                branch_user = BranchMaster.objects.get(branch_code=_branch_code)

                                saved_data = AuditorConnectionMaster(emp_id=emp_user,
                                registers_code=reg_user, role_id=registers_role_user,
                                created_user_id=_assigner_id,designation=_assigner_role,
                                branch_code=branch_user,assigner_branch_code_id=_assigner_branch_code,modified_user_id=request.session['emp_id'], modified_date=datetime.now(),branch_id_id=branch[0])
                                saved_data.save()
                                messages.success(request, 'Role assigned successfully')
                                return redirect('app_admin')
                            messages.error(request,
                            'Role for this branch has already exists for this user')
                            return redirect('app_admin')
                else:
                    if not AuditorConnectionMaster.objects.filter(emp_id=_employee_id,
                        role_id=_registers_role_id,branch_code=_branch_code,is_active=True).exists():
                        emp_user = EmployeeMaster.objects.get(emp_id=_employee_id)
                        reg_user = RegistersMaster.objects.get(registers_code=_registers_code)
                        registers_role_user = RegistersRoleMaster.objects\
                            .get(role_id=_registers_role_id)
                        branch_user = BranchMaster.objects.get(branch_code=_branch_code)

                        saved_data=AuditorConnectionMaster(emp_id=emp_user,
                        registers_code=reg_user, role_id=registers_role_user,
                        created_user_id=_assigner_id,designation=_assigner_role,
                        branch_code=branch_user,assigner_branch_code_id=_assigner_branch_code,modified_user_id=request.session['emp_id'], modified_date=datetime.now(),branch_id_id=branch[0])
                        saved_data.save()
                        messages.success(request, 'Role assigned successfully')
                        return redirect('app_admin')
                    messages.error(request, 'Role for this branch has already exists for this user')
                    return redirect('app_admin')
        else:
            return redirect('app_admin')
    except Exception as e:
        print(e)
        # raise
        messages.error(request, 'failed to assign the role')
        return redirect('app_admin')

#@my_login_required
def select_auditor(request):
    """
    select_auditor
    :param request:
    :return:
    """
    config_data = Box(request.session['config_data'])
    tenant = config_data.tenant
    tenant_image = config_data.logo_image.image_path
    title = config_data.module.AD001.display_name.admin
    try:
        registers_list = RegistersMaster.objects.filter(registers_code='AD001')
        registers_role_list = RegistersRoleMaster.objects.filter(registers_code='AD001')\
            .exclude(role_desc__in=['ad001appadmin', 'ad001branchadmin', 'it001admin', 'ad001finance'])
        branch_list = BranchMaster.objects.filter(active=True)
        employee_list = EmployeeMaster.objects.filter(active=True).values("emp_id", "emp_name",
            "designation","branch_code", "designation").order_by('emp_name')\
            .exclude(designation='IT-Admin')  # get employess from db
        list4 = AuditorConnectionMaster.objects.filter(registers_code='AD001', is_active=True)\
            .values('is_active','emp_reg_role_id','registers_code','role_id','emp_id',
                    'registers_code__registers_type','role_id__role_name',
            'emp_id__emp_name','branch_code__branch_name').exclude(emp_reg_role_id=1)#.order_by('id')
        context ={'registers_list':registers_list,'registers_role_list': registers_role_list,
                  'branch_list': branch_list,'employee_list': employee_list,
                  'emp_reg_role_list': list4, 'tenant_image': tenant_image, "tenant":tenant, 'title':title}
        return render(request, 'boss_admin/assign_role_page/auditor_selection_page.html', context)
    except Exception as e:
        print(str(e))
        messages.error(request, str(e))
        #return render(request, 'boss_admin/assign_role_page/auditor_selection_page.html', context)
        return redirect('select_auditor')

@csrf_exempt
@my_login_required
def add_auditor(request):
    """
    add_auditor
    :param request:
    :return:
    """
    try:
        if request.method == "POST":
            _registers_code = request.POST.get('register_dropdown')
            _registers_role_id = request.POST.get('registers_role_dropdown')
            if not _registers_role_id:
                messages.error(request, 'role not selected from the dropdown')
            _branch_code = request.POST.get('branch_dropdown')
            if not _branch_code:
                messages.error(request, 'branch not selected from the dropdown')
            _employee_id = request.POST.get('employee_dropdown')
            if not _employee_id:
                messages.error(request, 'employee not selected from the dropdown')
            _assigner_id = request.session['emp_id']
            _assigner_role = request.session['emp_desig_role']
            _assigner_branch_code = request.session['branch_code']

            emp_exists = AuditorConnectionMaster.objects.filter(emp_id = _employee_id,
                is_active = True).values('role_id','role_id__role_name')
            if emp_exists:
                xyz = emp_exists[0]
                result1 = xyz['role_id']
                result2 = xyz['role_id__role_name']
                if str(result1) != _registers_role_id:
                    messages.error(request, 'You have an active role as ' + str(result2))
                    return redirect('select_auditor')

                assigned_emp=AuditorConnectionMaster.objects.filter(role_id=_registers_role_id,
                        branch_code=_branch_code,is_active=True).values('emp_id__emp_name')
                if assigned_emp:
                    xyz = assigned_emp[0]
                    result1 = xyz['emp_id__emp_name']
                    messages.error(request, 'Role you are assigning has already exists with '
                                   + str(result1))
                    return redirect('select_auditor')
                else:
                    role_iddd = AuditorConnectionMaster.objects.filter(emp_id=_employee_id,
                                is_active=True,branch_code=_branch_code)\
                        .values('role_id','role_id__role_name',
                        'branch_code__branch_name')
                    if role_iddd:
                        xyz = role_iddd[0]
                        result1 = xyz['role_id']
                        role_name = xyz['role_id__role_name']
                        branch_name = xyz['branch_code__branch_name']
                        result = str(result1)
                        if result == _registers_role_id:
                            if not AuditorConnectionMaster.objects.filter(emp_id=_employee_id,
                                role_id=_registers_role_id,branch_code = _branch_code,
                                            is_active=True).exists():
                                emp_user = EmployeeMaster.objects.get(emp_id=_employee_id)
                                reg_user = RegistersMaster.objects\
                                    .get(registers_code=_registers_code)
                                registers_role_user = RegistersRoleMaster.objects\
                                    .get(role_id=_registers_role_id)
                                branch_user = BranchMaster.objects.get(branch_code=_branch_code)

                                saved_data = AuditorConnectionMaster(emp_id=emp_user,
                                registers_code=reg_user,role_id=registers_role_user,
                                created_user_id=_assigner_id,designation=_assigner_role,
                                branch_code=branch_user,assigner_branch_code_id=_assigner_branch_code, modified_user_id=request.session['emp_id'], modified_date=datetime.now())
                                saved_data.save()
                                messages.success(request, 'Role assigned successfully')
                                return redirect('select_auditor')
                            messages.error(request,
                            'Role for this branch has already exists for this user')
                            return redirect('select_auditor')
                        else:
                            messages.error(request, 'You have an Active role as: '+ str(role_name)+
                                           ' for '+ str(branch_name)+' branch')
                            return redirect('select_auditor')
                    else:
                        if not AuditorConnectionMaster.objects.filter(emp_id=_employee_id,
                            role_id=_registers_role_id,branch_code=_branch_code,is_active=True)\
                                .exists():
                            emp_user = EmployeeMaster.objects.get(emp_id=_employee_id)
                            reg_user = RegistersMaster.objects.get(registers_code=_registers_code)
                            registers_role_user = RegistersRoleMaster.objects\
                                .get(role_id=_registers_role_id)
                            branch_user = BranchMaster.objects.get(branch_code=_branch_code)

                            saved_data = AuditorConnectionMaster(emp_id=emp_user,
                             registers_code=reg_user, role_id=registers_role_user,
                             created_user_id=_assigner_id,designation=_assigner_role,
                             branch_code=branch_user,assigner_branch_code_id=_assigner_branch_code,modified_user_id=request.session['emp_id'], modified_date=datetime.now())
                            saved_data.save()
                            messages.success(request, 'Role assigned successfully')
                            return redirect('select_auditor')
                        messages.error(request,
                          'Role for this branch has already exists for this user')
                        return redirect('select_auditor')
            else:
                if not AuditorConnectionMaster.objects.filter(emp_id=_employee_id,
                    role_id=_registers_role_id,branch_code=_branch_code,is_active=True).exists():
                    emp_user = EmployeeMaster.objects.get(emp_id=_employee_id)
                    reg_user = RegistersMaster.objects.get(registers_code=_registers_code)
                    registers_role_user = RegistersRoleMaster.objects\
                        .get(role_id=_registers_role_id)
                    branch_user = BranchMaster.objects.get(branch_code=_branch_code)

                    saved_data=AuditorConnectionMaster(emp_id=emp_user,
                    registers_code=reg_user, role_id=registers_role_user,
                    created_user_id=_assigner_id,designation=_assigner_role,
                    branch_code=branch_user,assigner_branch_code_id=_assigner_branch_code,modified_user_id=request.session['emp_id'], modified_date=datetime.now())
                    saved_data.save()
                    messages.success(request, 'Role assigned successfully')
                    return redirect('select_auditor')
                messages.error(request, 'Role for this branch has already exists for this user')
                return redirect('select_auditor')
        else:
            return redirect('select_auditor')
    except:
        # raise
        messages.error(request, 'failed to assign the role')
        return redirect('select_auditor')

@csrf_exempt
@my_login_required
def delete_auditor_role(request):
    """
    delete_auditor_role
    :param request:
    :return:
    """
    try:
        id_no_ = request.POST.get('value')
        AuditorConnectionMaster.objects.filter(emp_reg_role_id=id_no_).delete()
        messages.success(request, 'deleted successfully')
        return HttpResponse('deleted')
    except:
        # raise
        messages.error(request, 'failed to delete')
        return HttpResponse('error')

@csrf_exempt
@my_login_required
def add_branch(request):
    """
    select_auditor
    :param request:
    :return:
    """
    global branch_data
    config_data = Box(request.session['config_data'])
    tenant = config_data.tenant
    tenant_image = config_data.logo_image.image_path
    title = 'Branch Management'
    branch_data= BranchMaster.objects.values('sl_no','branch_name','branch_code','zone','locationmaster__id','locationmaster__location_code','locationmaster__address','locationmaster__pin_code','locationmaster__city','locationmaster__building','locationmaster__floor','locationmaster__room','created_user','created_date','modified_user','modified_date','active')
    loc_data = LocationMaster.objects.values('location_code__branch_name', 'location_code__branch_code','location_code__zone','address','building', 'city', 'floor','room')
    paginator = Paginator(branch_data, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context ={'tenant_image': tenant_image, "tenant":tenant, 'title':title, 'data':loc_data, 'data1':page_obj}
    return render(request, 'boss_admin/assign_role_page/add_branch.html', context)

@csrf_exempt
@my_login_required
def branch_data_search(request):
    """
    filtering the data from FIR transaction table based on search value
    """
    global branch_data
    config_data = Box(request.session['config_data'])
    tenant = config_data.tenant
    title = 'Branch Management'
    tenant_image = config_data.logo_image.image_path
    search = request.POST.get("search")
    if search is not None:
        branch_data = BranchMaster.objects.filter(
                Q(branch_name__contains=search)|
                Q(branch_code__contains=search)|
                Q(zone__contains=search)|
                Q(locationmaster__address__contains=search)|
                Q(locationmaster__city__contains=search)|
                Q(locationmaster__building__contains=search)|
                Q(locationmaster__pin_code__contains=search)|
                Q(locationmaster__floor__contains=search)|
                Q(locationmaster__room__contains=search)|
                Q(created_user__contains=search)).values('sl_no','branch_name','branch_code','zone','locationmaster__id','locationmaster__location_code','locationmaster__address','locationmaster__pin_code','locationmaster__city','locationmaster__building','locationmaster__floor','locationmaster__room','created_user','created_date','modified_user','modified_date','active')
        paginator = Paginator(branch_data, 50)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context ={'tenant_image': tenant_image, "tenant":tenant, 'title':title,'data1':page_obj}
        return render(request, 'boss_admin/assign_role_page/add_branch.html', context)
    return redirect('add_branch')


@csrf_exempt
@my_login_required
def add_branch_ajax(request):
    branch_list=[]
    try:
        if request.is_ajax() and request.method == "POST":
            req_id = request.POST['req_id']
            loc_id = request.POST['loc_id']
            #print(loc_id)
            branch_code = request.POST['branch_code']
            branch_name = request.POST['branch_name']
            zone = request.POST['zone']
            building = request.POST['building']
            address = request.POST['address']
            floor = request.POST['floor']
            city = request.POST['city']
            pin_code = request.POST['pincode']
            room = request.POST['room']
            created_by = request.session['emp_id']
            # print(req_id,branch_code,branch_name,zone,building,address,city,floor,room)
            # branch_list=[]
            # branch_status= list(BranchMaster.objects.values_list('branch_name', flat='True'))
            # for i in branch_status:
            #     branch_list.append(i.lower())
            i=1
            if not req_id:
                err_logs=json.loads(branch_validation(branch_code,branch_name,i).content)    
                print(err_logs)
                if err_logs['brnch_code'] =='no':
                    messages.error(request, "The give branch code already exist")
                elif err_logs['brnch_name'] =='no':
                    messages.error(request, "The give branch name already exist")
                elif not req_id and  err_logs['brnch_code'] =='yes' and err_logs['brnch_name'] == 'yes':
                    BranchMaster(branch_code=branch_code, branch_name=branch_name,zone=zone,created_user=created_by,created_date=datetime.now(),modified_user=created_by,modified_date=datetime.now()).save()
                    #if loc_id:
                    LocationMaster(location_code_id=branch_code, address=address,city=city, pin_code=pin_code,building=building, floor=floor, room=room).save()
                    messages.success(request, "Added succesfully")
            elif req_id:
                try:
                    branch_status= list(BranchMaster.objects.exclude(sl_no=req_id).values_list('branch_name', flat='True'))
                    for j in branch_status:
                        branch_list.append(j.lower())
                except Exception as e:
                    print(e)
                if str(branch_name).lower() in branch_list:
                    messages.error(request, "The given branch name already exist")
                else:
                    BranchMaster.objects.filter(sl_no=req_id).update(branch_code=branch_code, branch_name=branch_name,zone=zone,modified_user=created_by,modified_date=datetime.now())
                    # if loc_id:
                    LocationMaster.objects.filter(location_code_id=branch_code).update(location_code_id=branch_code, address=address,city=city, pin_code=pin_code,building=building, floor=floor, room=room)
                    messages.success(request, "Edited succesfully")
            # if not req_id:
            #     BranchMaster(branch_code=branch_code, branch_name=branch_name,zone=zone,created_by=created_by,created_date=datetime.now(),modified_by=created_by,modified_date=datetime.now()).save()
            #     #if loc_id:
            #     LocationMaster(location_code_id=branch_code, address=address,city=city, pin_code=pin_code,building=building, floor=floor, room=room).save()
            #     messages.success(request, "Added succesfully")
            # else:
            #     BranchMaster.objects.filter(sl_no=req_id).update(branch_code=branch_code, branch_name=branch_name,zone=zone,modified_by=created_by,modified_date=datetime.now())
            #     #if loc_id:
            #     LocationMaster.objects.filter(id=loc_id).update(location_code_id=branch_code, address=address,city=city, pin_code=pin_code,building=building, floor=floor, room=room)
            #     messages.success(request, "Edited succesfully")
            return HttpResponse("success")
    except Exception as e:
        print(e)
        return HttpResponse("Fail")


# @csrf_exempt
# @my_login_required
# def add_employee(request):
#     """
#     select_auditor
#     :param request:
#     :return:
#     """
#     global emp_data
#     config_data = Box(request.session['config_data'])
#     tenant = config_data.tenant
#     tenant_image = config_data.logo_image.image_path
#     title = config_data.module.AD001.display_name.admin
#     emp_data= EmployeeMaster.objects.filter(active=True).values('sl_no','domain_id','emp_id','emp_name','designation','branch_code__branch_code','branch_code__branch_name',
#                                                 'email_id','function','sub_function','job_role','phone_number', 'created_by', 'created_date', 'modified_by','dtstmp')
#     branch_list = BranchMaster.objects.values('branch_name','branch_code')
#     paginator = Paginator(emp_data, 50)
#     page_number = request.GET.get('page')
#     page_obj = paginator.get_page(page_number)
#     context ={'tenant_image': tenant_image, "tenant":tenant, 'title':title, 'emp_data':page_obj, 'branch_list':branch_list}
#     return render(request, 'boss_admin/assign_role_page/add_employee.html', context)

# @csrf_exempt
# @my_login_required
# def employee_data_search(request):
#     """
#     filtering the data from FIR transaction table based on search value
#     """
#     global emp_data
#     config_data = Box(request.session['config_data'])
#     tenant = config_data.tenant
#     title = config_data.module.AD001.display_name.admin
#     tenant_image = config_data.logo_image.image_path
#     search = request.POST.get("search")
#     branch_list = BranchMaster.objects.values('branch_name','branch_code')
#     if search is not None:
#         emp_data = EmployeeMaster.objects.filter(
#                 Q(domain_id__contains=search)|
#                 Q(emp_id__contains=search)|
#                 Q(emp_name__contains=search)|
#                 Q(designation__contains=search)|
#                 Q(branch_code__branch_name__contains=search)|
#                 Q(email_id__contains=search)|
#                 Q(function__contains=search)|
#                 Q(sub_function__contains=search)|
#                 Q(job_role__contains=search)|
#                 Q(created_by__contains=search),active=True).values('sl_no','domain_id','emp_id','emp_name','designation','branch_code__branch_code','branch_code__branch_name',
#                                                 'email_id','function','sub_function','job_role','phone_number', 'created_by', 'created_date', 'modified_by','dtstmp')
#         paginator = Paginator(emp_data, 50)
#         page_number = request.GET.get('page')
#         page_obj = paginator.get_page(page_number)
#         context ={'tenant_image': tenant_image, "tenant":tenant, 'title':title,'emp_data':page_obj, 'branch_list':branch_list}
#         return render(request, 'boss_admin/assign_role_page/add_employee.html', context)
#     return redirect('add_employee')


# @csrf_exempt
# @my_login_required
# def add_employee_ajax(request):
#     print('********************')
#     regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
#     try:
#         if request.is_ajax() and request.method == "POST":
#             print('hjhjhjk')
#             id = request.POST['id']
#             domain_id = request.POST['domain']
#             emp_id = request.POST['emp_id']
#             emp_name = request.POST['emp_name']
#             password = request.POST['password']
#             designation = request.POST['designation']
#             branch_code = request.POST['branch_code']
#             email_id = request.POST['email_id']
#             function = request.POST['function']
#             sub_function = request.POST['sub_function']
#             job_role = request.POST['job_role']
#             created_by = request.session['emp_id']
#             print(domain_id,emp_id,emp_name,job_role,password,designation,branch_code,email_id,function,sub_function,created_by)
#             if not id:
#                 if EmployeeMaster.objects.filter(domain_id=domain_id, active=True).exists():
#                     domain = "Yes"
#                     print(domain)
#                     messages.error(request, "Employee with same domain id already exist")
#                 if not (re.search(regex,email_id)):
#                     email='No'
#                     print(email)
#                     messages.error(request, "Invalid Email Id")
#                 else:
                
#                     EmployeeMaster(domain_id=domain_id,emp_id=emp_id,emp_name=emp_name,branch_code_id=branch_code,pwd=password,designation=designation,email_id=email_id,function=function,sub_function=sub_function,job_role=job_role,created_by=created_by,modified_by=created_by,modified_date=datetime.now()).save()
#                     messages.success(request, "Added succesfully")
#             else:
#                 EmployeeMaster.objects.filter(sl_no=id).update(domain_id=domain_id,emp_id=emp_id,emp_name=emp_name,designation=designation,email_id=email_id,function=function,sub_function=sub_function,job_role=job_role,modified_by=created_by,modified_date=datetime.now())
#                 messages.success(request, "Edited succesfully")
#             return HttpResponse("success")
#     except Exception as e:
#         print(str(e))
#         return HttpResponse("error")

@my_login_required
def branch_data_export(request):
    global branch_data
    if branch_data:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="Branch_data.csv"'
        writer = csv.writer(response)
        writer.writerow(['Branch Code','Branch Name','Zone','Room No','Floor',
                                       'Building','Address','City','Pincode',
                                       'Created By', 'Created Date', 'Modified By', 'Modified Date'])
 
        for i in branch_data:
            writer.writerow((i["branch_code"],i["branch_name"],i["zone"],i["locationmaster__room"],
                         i["locationmaster__floor"],i["locationmaster__building"],i["locationmaster__address"],
                         i["locationmaster__city"],i["locationmaster__pin_code"],i["created_user"],i["created_date"].strftime('%d-%m-%Y'), i["modified_user"], i["modified_date"]))
        return response
    return redirect('add_branch')

# @my_login_required
# def emp_data_export(request):
#     global emp_data
#     if emp_data:
#         response = HttpResponse(content_type='text/csv')
#         response['Content-Disposition'] = 'attachment; filename="Employee_data.csv"'
#         writer = csv.writer(response)
#         writer.writerow(['Domain Id','Employee Id','Employee Name','Designation','Branch Name','Branch Code',
#                                         'Email Id','Function','Sub Function','Job Role','Phone Number'
#                                         'Created By', 'Created Date','Modified By', 'Modified Date'])
    
#         for i in emp_data:
#             writer.writerow((i["domain_id"],i["emp_id"],i["emp_name"],i["designation"],
#                             i["branch_code__branch_name"],i["branch_code__branch_code"],i["email_id"],i["function"],
#                             i["sub_function"],i["job_role"],i["phone_number"],i["created_by"],i["created_date"].strftime('%d-%m-%Y'), i["modified_by"], i["dtstmp"]))
#         return response
#     return redirect('add_employee')

# @my_login_required
# def delete_branch(request):
#     if request.is_ajax() and request.method == "POST":
#         id = request.POST['value']
#         print(id)
#         BranchMaster.objects.filter(sl_no=id).update(active=False)
#         #LocationMaster(location_code_id=branch_code, address=address,city=city, pin_code=pin_code,building=building, floor=floor, room=room).save()
#         messages.success(request, "Deleted succesfully")
#         return HttpResponse("success")

# @my_login_required
# def delete_employee(request):
#     if request.is_ajax() and request.method == "POST":
#         id = request.POST['value']
#         print(id)
#         EmployeeMaster.objects.filter(sl_no=id).update(active=False)
#         messages.success(request, "Deleted succesfully")
#         return HttpResponse("success")
    
# @my_login_required
# def transfer_employee(request):
#     if request.is_ajax() and request.method == "POST":
#         id = request.POST['value']
#         _branch_code = request.POST['branch_code']
#         print(id)
#         EmployeeMaster.objects.filter(sl_no=id).update(branch_code=_branch_code)
#         messages.success(request, "Transferred succesfully")
#         return HttpResponse("success")

@my_login_required
def emp_data_export(request):
    global emp_data
    if emp_data:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="Employee_data.csv"'
        writer = csv.writer(response)
        writer.writerow(['Domain Id','Employee Id','Employee Name','Designation','Branch Name','Branch Code',
                                       'Email Id','Function','Sub Function','Job Role','Phone Number'
                                       'Created By', 'Created Date','Modified By', 'Modified Date'])
 
        for i in emp_data:
            writer.writerow((i["domain_id"],i["emp_id"],i["emp_name"],i["designation"],
                         i["branch_code_id__branch_name"],i["branch_code_id__branch_code"],i["email_id"],i["function"],
                         i["sub_function"],i["job_role"],i["phone_number"],i["created_user"],i["created_date"].strftime('%d-%m-%Y'),i["modified_user"],i["modified_date"].strftime('%d-%m-%Y')))
        return response
    return redirect('add_employee')

@my_login_required
def delete_branch(request):
    if request.is_ajax() and request.method == "POST":
        id = request.POST['value']
        #print(id)
        BranchMaster.objects.filter(sl_no=id).update(active=False, modified_user=request.session['emp_id'], modified_date=datetime.now())
        #LocationMaster(location_code_id=branch_code, address=address,city=city, pin_code=pin_code,building=building, floor=floor, room=room).save()
        messages.success(request, "Deleted succesfully")
        return HttpResponse("success")

@my_login_required
def delete_employee(request):
    if request.is_ajax() and request.method == "POST":
        id = request.POST['value']
        #print(id)
        EmployeeMaster.objects.filter(sl_no=id).update(active=False, modified_user=request.session['emp_id'], modified_date=datetime.now())
        messages.success(request, "Deleted succesfully")
        return HttpResponse("success")
    
@my_login_required
def transfer_employee(request):
    if request.is_ajax() and request.method == "POST":
        id = request.POST['value']
        _branch_code = request.POST['branch_code']
        #check if employee's old and new branch are same
        emp=request.POST['emp']
        #print(id,emp)
        result = json.loads(move_employee(id,emp,_branch_code).content)
        #print(result)
        if result['err_logs'] =='success':
            EmployeeMaster.objects.filter(sl_no=id).update(branch_code=_branch_code, modified_user=request.session['emp_id'], modified_date=datetime.now())
            EmployeeRegisterRoleMaster.objects.filter(emp_id=emp).delete()
            messages.success(request, "Transferred succesfully")
        elif result['err_logs'] =='fail':
            messages.error(request, "Destination and source branch cannot be same")
        return HttpResponse("success")

# employee upload 

@csrf_exempt
def employee_upload_new(request):
    global err_logs,logs
    err_logs = []
    if request.method == 'POST':
        dataset = Dataset()
        try:
            new_b = request.FILES['myfile']
            pass
        except Exception as e:
            messages.error(request, 'No file selected, Please choose the file..!')
            return render(request, 'boss_admin/assign_role_page/add_employee.html')

        if not new_b.name.endswith('xlsx'):
            messages.error(request, 'wrong file format, please choose a .xlsx file')
            return render(request, 'boss_admin/assign_role_page/add_employee.html')
        df = pd.read_excel(new_b)
        #print(df)
        existing_count =0
        new_count=0
        emp_data=[]
        logs = []
        sl_num = EmployeeMaster.objects.values('sl_no').latest('sl_no')
        sl_no = sl_num['sl_no']
        branch=BranchMaster.objects.filter(branch_code=request.session['branch_code']).values_list('sl_no', flat=True)
        for i in df.index:

            existing_count+=1
            domain_id=df['Domain Id'][i]
            emp_id=df['Employee Id'][i]
            emp_name=df['Emp Name'][i]
            designation=df['Designation'][i]
            branch_code=df['Branch Code'][i]
            email_id=df['Email Id'][i]
            phone = df['Phone Number'][i]
            function = df['Function'][i]
            subfun = df['Sub Function'][i]
            jobrole = df['Job Role'][i]
            
            err_logs=json.loads(emp_validation(domain_id,emp_id,branch_code,email_id,phone,i,request).content)
            
            if err_logs['err_logs']=='success' and emp_id in [a_dict['Employee Id'] for a_dict in emp_data] and domain_id in [a_dict['Domain Id'] for a_dict in emp_data]:
                logs.append("In line "+str(i+1)+" Duplicate employee id  "+str(emp_id)+" exists")
                logs.append("In line "+str(i+1)+" Duplicate domain id  "+str(domain_id)+" exists")
            elif err_logs['err_logs']=='success' and emp_id in [a_dict['Employee Id'] for a_dict in emp_data]:
                logs.append("In line "+str(i+1)+" Duplicate employee id  "+str(emp_id)+" exists")
            elif err_logs['err_logs']=='success' and domain_id in [a_dict['Domain Id'] for a_dict in emp_data]:
                logs.append("In line "+str(i+1)+" Duplicate domain id  "+str(domain_id)+" exists")  
            elif err_logs['err_logs']=='success':
                print('succcc')
            else:
                logs.append(err_logs['err_logs'])

            
            if err_logs['dm_id'] =='yes' and err_logs['branch_id'] == 'yes' and err_logs['em_id'] == 'yes' and err_logs['ph_num']=='yes' and err_logs['email']=='yes' and emp_id not in [a_dict['Employee Id'] for a_dict in emp_data] and domain_id not in [a_dict['Domain Id'] for a_dict in emp_data]:
                sl_no+=1
                emp_data.append({'Sl_No':sl_no,'Domain Id':domain_id,'Employee Id':emp_id,'Emp Name':emp_name,
                        'Designation':designation, 'Branch Code':branch_code,
                        'Email Id':email_id,'Phone Number':phone,'Function':function,'Sub Function':subfun,'Job Role':jobrole}) 
                new_count+=1       

        save_data = [EmployeeMaster(sl_no=i['Sl_No'],domain_id=i['Domain Id'],emp_id=i['Employee Id'],emp_name=i['Emp Name'],
                pwd='admin', designation=i['Designation'], branch_code_id=i['Branch Code'],
                created_user=request.session['emp_id'], email_id=i['Email Id'],phone_number=i['Phone Number'],function=i['Function'],sub_function=i['Sub Function'],job_role=i['Job Role'], bramch_id_id=branch[0]) for i in emp_data]
        EmployeeMaster.objects.bulk_create(save_data)
        if logs:
            messages.error(request, 'Uploaded '+ str(new_count) +' out of '+ str(existing_count))
            return redirect('add_employee')   
        else:
            messages.success(request, 'Uploaded '+ str(new_count) +' out of '+ str(existing_count))
        return redirect('add_employee')       
    return render(request, 'boss_admin/assign_role_page/add_employee.html')

def upload_err_logs_export(request):
    global logs
    data = tablib.Dataset(headers=["Error Logs"])
    for i in logs:
        data.append((str(i),))
    response = HttpResponse(data.export('xlsx'), content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="emp_err_logs.xlsx"'
    return response


@csrf_exempt
@my_login_required
def add_employee(request):
    """
    select_auditor
    :param request:
    :return:
    """
    global emp_data
    config_data = Box(request.session['config_data'])
    tenant = config_data.tenant
    title = 'User Management'
    tenant_image = config_data.logo_image.image_path    
    emp_data= EmployeeMaster.objects.values('sl_no', 'emp_id', 'emp_name', 'designation', 'email_id', 'phone_number', 'function', 'sub_function', 'job_role', 'created_user', 'created_date','branch_code_id__branch_code', 'branch_code_id__branch_name','active', 'domain_id','modified_user','modified_date')
    branch_list = BranchMaster.objects.values('branch_name','branch_code')
    paginator = Paginator(emp_data, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context ={'emp_data':page_obj, 'branch_list':branch_list, 'tenant':tenant,'title':title,'tenant_image':tenant_image}
    return render(request, 'boss_admin/assign_role_page/add_employee.html', context)

@csrf_exempt
@my_login_required
def employee_data_search(request):
    """
    filtering the data from FIR transaction table based on search value
    """
    global emp_data
    config_data = Box(request.session['config_data'])
    tenant = config_data.tenant
    title = 'User Managemenet'
    tenant_image = config_data.logo_image.image_path    
    search = request.POST.get("search")
    #print(search)
    branch_list = BranchMaster.objects.values('branch_name','branch_code')
    try:
        if search == 'active':
            emp_data= EmployeeMaster.objects.filter(active=True).values('sl_no', 'emp_id', 'emp_name', 'designation', 'email_id', 'phone_number', 'function', 'sub_function', 'job_role', 'created_user', 'created_date','branch_code_id__branch_code', 'branch_code_id__branch_name','active', 'domain_id','modified_user','modified_date')
            paginator = Paginator(emp_data, 50)
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            context ={'emp_data':page_obj, 'branch_list':branch_list,'tenant':tenant,'title':title,'tenant_image':tenant_image}
            return render(request, 'boss_admin/assign_role_page/add_employee.html', context)
        if search == 'inactive':
            emp_data= EmployeeMaster.objects.filter(active=False).values('sl_no', 'emp_id', 'emp_name', 'designation', 'email_id', 'phone_number', 'function', 'sub_function', 'job_role', 'created_user', 'created_date','branch_code_id__branch_code', 'branch_code_id__branch_name','active', 'domain_id','modified_user','modified_date')
            paginator = Paginator(emp_data, 50)
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            context ={'emp_data':page_obj, 'branch_list':branch_list,'tenant':tenant,'title':title,'tenant_image':tenant_image}
            return render(request, 'boss_admin/assign_role_page/add_employee.html', context)
        if search is not None:
            emp_data = EmployeeMaster.objects.filter(
                    Q(active__contains=search)|
                    Q(domain_id__contains=search)|
                    Q(emp_id__contains=search)|
                    Q(emp_name__contains=search)|
                    Q(designation__contains=search)|
                    Q(branch_code_id__branch_name__contains=search)|
                    Q(branch_code_id__branch_code__contains=search)|
                    Q(email_id__contains=search)|
                    Q(function__contains=search)|
                    Q(sub_function__contains=search)|
                    Q(job_role__contains=search)
                    ).values('sl_no', 'emp_id', 'emp_name', 'designation', 'email_id', 'phone_number', 'function', 'sub_function', 'job_role', 'created_user', 'created_date','branch_code_id__branch_code', 'branch_code_id__branch_name','active', 'domain_id','modified_user','modified_date')
            paginator = Paginator(emp_data, 50)
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            context ={'emp_data':page_obj, 'branch_list':branch_list,'tenant':tenant,'title':title,'tenant_image':tenant_image}
            return render(request, 'boss_admin/assign_role_page/add_employee.html', context)
        else:
            if emp_data is not None:
                paginator = Paginator(emp_data, 50)
                page_number = request.GET.get('page')
                page_obj = paginator.get_page(page_number)
            else:
                page_obj = None
            context ={'emp_data':page_obj, 'branch_list':branch_list,'tenant':tenant,'title':title,'tenant_image':tenant_image}
            return render(request, 'boss_admin/assign_role_page/add_employee.html', context)
        return redirect('add_employee')
    except Exception as e:
        print(e)    
        return redirect('add_employee')

# if search == 'active':
#         emp_data= EmployeeMaster.objects.filter(active=True).values('sl_no', 'emp_id', 'emp_name', 'designation', 'email_id', 'phone_number', 'function', 'sub_function', 'job_role', 'created_by', 'created_date','branch_code_id__branch_code', 'branch_code_id__branch_name','active', 'domain_id','modified_by','dtstmp')
#     if search =='inactive':
#         emp_data= EmployeeMaster.objects.filter(active=False).values('sl_no', 'emp_id', 'emp_name', 'designation', 'email_id', 'phone_number', 'function', 'sub_function', 'job_role', 'created_by', 'created_date','branch_code_id__branch_code', 'branch_code_id__branch_name','active', 'domain_id','modified_by','dtstmp')
#     if search is not None:
#         emp_data = EmployeeMaster.objects.filter(
#                 Q(active__contains=search)|
#                 Q(domain_id__contains=search)|
#                 Q(emp_id__contains=search)|
#                 Q(emp_name__contains=search)|
#                 Q(designation__contains=search)|
#                 Q(branch_code_id__branch_name__contains=search)|
#                 Q(branch_code_id__branch_code__contains=search)|
#                 Q(email_id__contains=search)|
#                 Q(function__contains=search)|
#                 Q(sub_function__contains=search)|
#                 Q(job_role__contains=search)
#                 ).values('sl_no', 'emp_id', 'emp_name', 'designation', 'email_id', 'phone_number', 'function', 'sub_function', 'job_role', 'created_by', 'created_date','branch_code_id__branch_code', 'branch_code_id__branch_name','active', 'domain_id','modified_by','dtstmp')
#     if emp_data is not None:
#         paginator = Paginator(emp_data, 50)
#         page_number = request.GET.get('page')
#         page_obj = paginator.get_page(page_number)
#     else:
#         page_obj = None
#         context ={'emp_data':page_obj, 'branch_list':branch_list}
#         return render(request, 'boss_admin/assign_role_page/add_employee.html', context)
#     return redirect('add_employee')

@csrf_exempt
@my_login_required
def add_employee_ajax(request):
    #print('********************')
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    try:
        if request.is_ajax() and request.method == "POST":
            id = request.POST['id']
            domain_id = request.POST['domain']
            emp_id = request.POST['emp_id']
            emp_name = request.POST['emp_name']
            phone = request.POST['phn_num']
            designation = request.POST['designation']
            branch_code = request.POST['branch_code']
            email_id = request.POST['email_id']
            function = request.POST['function']
            subfun = request.POST['sub_function']
            jobrole = request.POST['job_role']
            created_by = request.session['emp_id']
            i=1
            branch=BranchMaster.objects.filter(branch_code=request.session['branch_code']).values_list('sl_no', flat=True)
            #print(domain_id,emp_id,emp_name,jobrole,phone,designation,branch_code,email_id,function,subfun,created_by)
            err_logs=json.loads(emp_validation(domain_id,emp_id,branch_code,email_id,phone,i,request).content)
            print(err_logs)
            # if err_logs['err_logs'] == 'success':
            #     print(err_logs['err_logs'])
            #     messages.success(request, "Added successfully")
            # if not id:
            #     print('not id')
            #     if err_logs['dm_id'] == "no":
            #         messages.success(request, "The given domain id already tagged to an another employee")
            #     elif err_logs['branch_id'] == 'no':
            #         messages.success(request, "Branch code does not exist")
            #     elif err_logs['email'] =='no':
            #         messages.success(request, "Invalid email id format")
            #     elif err_logs['ph_num'] == "no":
            #         messages.success(request, "Phone number length should be between 10 to 12")
            #     elif err_logs['em_id']=="no":
            #         messages.success(request, "The given employee id already exist")
            # elif id:
            #     print('id')
            #     if EmployeeMaster.objects.exclude(sl_no=id).filter(domain_id=domain_id,active=True).exists():
            #         print('exist')
            #         messages.success(request, "The given domain id already tagged to an another employee")
 
            # if not id:
            #     print('not id')
            if not id and err_logs['dm_id'] == "no":
                messages.success(request, "The given domain id already tagged to an another employee")
            elif not id and err_logs['branch_id'] == 'no':
                messages.success(request, "Branch code does not exist")
            elif err_logs['email'] =='no':
                messages.success(request, "Invalid email id format")
            elif err_logs['ph_num'] == "no":
                messages.success(request, "Phone number length should be between 10 to 12")
            elif not id and err_logs['em_id']=="no":
                messages.success(request, "The given employee id already exist")
            # elif id:
            #     print('id')
            elif id and EmployeeMaster.objects.exclude(sl_no=id).filter(domain_id=domain_id,active=True).exists():
                #print('exist')
                messages.success(request, "The given domain id already tagged to an another employee")
            

            # emp_list=[]
            # emp_list1 =[]
            # emp_status= EmployeeMaster.objects.values_list('emp_name', flat='True')
            # # emp_domain_id = EmployeeMaster.objects.filter(active=True).values_list('domain_id', flat='True')
            # # print(emp_domain_id)
            # for i in emp_status:
            #     emp_list.append(i.lower())
            # if id:
            #     emp_status1= EmployeeMaster.objects.exclude(sl_no=id).values_list('emp_name', flat='True')
            #     for i in emp_status1:
            #         emp_list1.append(i.lower())            
            # if not id and EmployeeMaster.objects.filter(domain_id=domain_id, active=True).exists():
            #     print("im testing"+ domain_id)
            #     domain = "Yes"
            #     print(domain)
            #     messages.error(request, "Employee with same domain id already exist")
            # elif not (re.search(regex,email_id)):
            #     email='No'
            #     messages.error(request, "Invalid Email Id")
            # # else:
            # elif not id and  str(emp_name).lower() in emp_list:
            #     em_name="no"
            #     messages.error(request, "Employee Name already exist")
            # elif not id and EmployeeMaster.objects.get(emp_id=emp_id):
            #     messages.error(request, "Employee ID already exist")

            # elif id and EmployeeMaster.objects.exclude(sl_no=id).filter(domain_id=domain_id, active=True).exists():
            #     messages.error(request, "Employee with same domain id already exist")
            # elif id and  str(emp_name).lower() in emp_list1:
            #     em_name="no"
            #     messages.error(request, "Employee Name already exist")
            # # elif id and EmployeeMaster.objects.get(emp_id=emp_id):
            # #     messages.error(request, "Employee ID already exist")
            elif not id and err_logs['dm_id'] =='yes' and err_logs['branch_id'] == 'yes' and err_logs['em_id'] == 'yes' and err_logs['ph_num']=='yes' and err_logs['email']=='yes': 
                #print("creating")
                EmployeeMaster(domain_id=domain_id,emp_id=emp_id,emp_name=emp_name,branch_code_id=branch_code,phone_number=phone,designation=designation,email_id=email_id,function=function,sub_function=subfun,job_role=jobrole,created_user=created_by,modified_user=created_by,modified_date=datetime.now(),  branch_id_id=branch[0]).save()
                messages.success(request, "Added succesfully")
            elif id and err_logs['ph_num']=='yes' and err_logs['email']=='yes': #and not EmployeeMaster.objects.exclude(sl_no=id).filter(domain_id=domain_id,active=True).exists():
                EmployeeMaster.objects.filter(sl_no=id).update(domain_id=domain_id,emp_id=emp_id,emp_name=emp_name,designation=designation,email_id=email_id,function=function,sub_function=subfun,job_role=jobrole, phone_number=phone,modified_user=created_by,modified_date=datetime.now())
                messages.success(request, "Edited succesfully")
            # else:
            #     messages.error(request, "Failed to add")
            return HttpResponse("success")
    except Exception as e:
        print(str(e))
        return HttpResponse("error")


@csrf_exempt
@my_login_required
def branch_upload_new(request):
    config_data = Box(request.session['config_data'])
    tenant = config_data.tenant
    tenant_image = config_data.logo_image.image_path
    global err_logs,logs
    err_logs = []
    try:
        if request.method == 'POST':
            dataset = Dataset()
            try:
                new_b = request.FILES['myfile']
                pass
            except Exception as e:
                messages.error(request, 'No file Selected, Please choose the file..!')
                return render(request, 'boss_admin/assign_role_page/add_branch.html',{'tenant_image': tenant_image, "tenant":tenant})

            if not new_b.name.endswith('xlsx'):
                messages.error(request, 'wrong file format, please choose a .xlsx file')
                return render(request, 'boss_admin/assign_role_page/add_branch.html',{'tenant_image': tenant_image, "tenant":tenant})
            #branch_data_upload(new_b)
            #def branch_upload_new(new_b):
            df = pd.read_excel(new_b)
            #print(df)
            existing_count =0
            new_count=0
            branch_list=[]
            branch_list1=[]
            logs=[]
            branch=[]
            branch_status= list(BranchMaster.objects.values_list('branch_name', flat='True'))
            for i in branch_status:
                branch_list.append(i.lower())
            for i in df.index:
                existing_count+=1
                branch_name=df['Branch Name'][i]
                branch_code=df['Branch Code'][i]
                zone=df['Zone'][i]
                err_logs=json.loads(branch_validation(branch_code,branch_name,branch_list,i,request).content)    
                print(err_logs)
                if err_logs['err_logs']:
                    logs.append(err_logs['err_logs'])
                #print('here')
            if err_logs['brnch_code'] =='yes' and err_logs['brnch_name'] == 'yes':
                #print('no')
                branch.append({'branch_name':branch_name,'branch_code':branch_code,'zone':zone})
                #print(branch)
                new_count+=1
            save_data = [BranchMaster(branch_name=i['branch_name'],branch_code=i['branch_code'],zone=i['zone']) for i in branch]
            #print(save_data)
            BranchMaster.objects.bulk_create(save_data)
            if len(logs)!=0:
                print(logs,"logs")
                messages.error(request, 'Uploaded '+ str(new_count) +' out of '+ str(existing_count))
                return redirect('add_branch')   
            else:
                print(logs, 'logs empty')
                if new_count<existing_count:
                    messages.error(request, 'Uploaded '+ str(new_count) +' out of '+ str(existing_count))
                else:
                    messages.success(request, 'Uploaded '+ str(new_count) +' out of '+ str(existing_count))
            return redirect('add_branch')
    except Exception as e:
        print(str(e))
        messages.error(request, 'failed to upload')
        return redirect('add_branch')

@my_login_required
def admin_func(request):
    config_data = Box(request.session['config_data'])
    tenant = config_data.tenant
    display_name = config_data.module
    tenant_image = config_data.logo_image.image_path
    return render(request, 'boss_admin/assign_role_page/admin_page.html',{'tenant_image': tenant_image, "tenant":tenant, "display_name":display_name})

@my_login_required
def audit_func(request):
    config_data = Box(request.session['config_data'])
    tenant = config_data.tenant
    display_name = config_data.module
    tenant_image = config_data.logo_image.image_path
    return render(request, 'boss_admin/assign_role_page/audit_page.html',{'tenant_image': tenant_image, "tenant":tenant, "display_name":display_name})


@my_login_required
def designation_matrix(request):
    config_data = Box(request.session['config_data'])
    tenant = config_data.tenant
    display_name = config_data.module
    tenant_image = config_data.logo_image.image_path
    title = "Designation Matrix"
    data = DesignationMatrix.objects.filter(is_active = True).values('id', 'role_type', 'role_name','role_dept', 'designations')

    data1 = [[i['id'], i["designations"]] for i in data]
    #print(data1)

    # for i in range (0,(len(data))):
    #     #print(data[i]['designations'])
    #     data[i]['designations'] = data[i]['designations'][0]['roles']

    context = {'tenant_image': tenant_image, "tenant":tenant, "display_name":display_name, 'data':data, 'data1':data1, 'title':title}

    return render(request, 'boss_admin/assign_role_page/designation_matrix.html', context)

def edit_designationmatrix(request, pk):
    
    try:
        if request.is_ajax() and request.method == 'POST':
            role_name = request.POST['role_name']
            role_type = request.POST['role_type']
            role_dept = request.POST['role_dept']
            desigData = json.loads(request.POST['desigData'])
            if not desigData == []:
                DesignationMatrix.objects.filter(id=pk).update(
                role_name=role_name,
                role_type=role_type,
                role_dept=role_dept,
                designations=desigData,
                last_modified_date = datetime.now(), 
                last_modified_user = request.session['emp_id'], 
            )
                messages.success(request, "Designations modified successfully")
            else:
                messages.error(request,'Enter all details to update Designation')
            
                
            return HttpResponse("success")
       
    except Exception as e:
        print(e)
        return redirect('designation_matrix')