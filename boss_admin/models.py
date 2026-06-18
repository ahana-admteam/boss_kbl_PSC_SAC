"""
models
"""
from django.db import models

class BranchMaster(models.Model):
    """
    BranchMaster Model
    """
    def from_500():
        """
        sl no generate
        """
        largest = BranchMaster.objects.all().order_by('sl_no').last()
        if not largest:
            return 1
        return largest.sl_no + 1
    sl_no = models.IntegerField(default=from_500, primary_key=True)
    modified_date = models.DateTimeField(auto_now=True, blank=True, null=True)
    branch_name = models.CharField(max_length=100, null=True)
    branch_code = models.CharField(unique=True, max_length=50)
    active = models.BooleanField(default=True)
    zone = models.CharField(max_length=100, null=True)
    zone_name = models.CharField(max_length=250, null=True)
    city = models.CharField(max_length=250, null=True)
    state = models.CharField(max_length=250, null=True)
    created_user = models.CharField(max_length=150, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_user = models.CharField(max_length=150, null=True)
    retention_limit = models.IntegerField(null=True)



    class Meta:
        db_table = "branch_master"
        ordering= ['sl_no']

    def __str__(self):
        return self.branch_code  # display the emp_name

class EmployeeMaster(models.Model):
    """
    EmployeeMaster Model
    """
    def from_500():
        """
        sl no generate
        """
        largest = EmployeeMaster.objects.all().order_by('sl_no').last()
        if not largest:
            return 1
        return largest.sl_no + 1

    sl_no = models.IntegerField(default=from_500, primary_key=True)
    domain_id = models.CharField(max_length=200)
    emp_id = models.CharField(unique=True, max_length=50)
    emp_name = models.CharField( max_length=50, null=False)
    pwd = models.CharField(max_length=100, null=False)
    designation = models.CharField(max_length=100, null=True)
    remarks = models.CharField(max_length=500, null=True)
    modified_date = models.DateTimeField(auto_now=True, blank=True, null=True)
    branch_code = models.ForeignKey(BranchMaster, to_field="branch_code", on_delete=models.CASCADE, null=True)
    is_staff = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=True)
    active = models.BooleanField(default=True)
    role = models.IntegerField(null=True)
    created_user = models.CharField(max_length=150, null=True)
    created_date = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    email_id = models.EmailField(max_length=100, null=True)
    phone_number=models.BigIntegerField(blank=True,null=True)
    function = models.CharField(max_length=100, blank=True, null=True)
    sub_function = models.CharField(max_length=100, blank=True, null=True)
    job_role = models.CharField(max_length=100, blank=True, null=True)
    modified_user = models.CharField(max_length=150, null=True)
    branch_id = models.ForeignKey(BranchMaster, related_name="branch_id", on_delete=models.CASCADE)
    signature = models.FileField(upload_to=None, max_length=500, null=True) 

    class Meta:
        db_table = "employee_master"
        ordering= ['sl_no']

    def __str__(self):
        return self.domain_id  # display the emp_name


class RegistersMaster(models.Model):
    """
    RegistersMaster Model
    """
    def from_500():
        """
        sl no generate
        """
        largest = RegistersMaster.objects.all().order_by('sl_no').last()
        if not largest:
            return 1
        return largest.sl_no + 1
    sl_no = models.IntegerField(default=from_500)
    registers_code = models.CharField(primary_key = True, unique=True, max_length=50)
    registers_type = models.CharField(max_length=100, null=True)
    registers_desc = models.CharField(max_length=500, null=True)
    is_active = models.BooleanField(default=True)
    created_user = models.CharField(max_length=150, null=True)
    created_date = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    modified_date = models.DateTimeField(auto_now=True, blank=True, null=True)
    modified_user = models.CharField(max_length=150, null=True)



    class Meta:
        db_table = "registers_master"

    def __str__(self):
        return self.registers_code  # display the emp_name


class RegistersRoleMaster(models.Model):
    """
    RegistersRoleMaster Model
    """
    role_id = models.AutoField(primary_key=True, null=False, editable=True)
    role_name = models.CharField(max_length=150, null=True)
    role_desc = models.CharField(max_length=500, null=True)
    registers_code = models.ForeignKey(RegistersMaster, on_delete=models.CASCADE, null=True)
    is_active = models.BooleanField(default=True)
    created_user = models.CharField(max_length=150, null=True)
    created_date = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    modified_date = models.DateTimeField(auto_now=True, blank=True, null=True)
    modified_user = models.CharField(max_length=150, null=True)
    
    class Meta:
        db_table = "registers_role_master"

    def __str__(self):
        return self.role_name  # display the emp_name


class EmployeeRegisterRoleMaster(models.Model):
    """
    EmployeeRegisterRoleMaster Model
    """
    emp_reg_role_id = models.AutoField(primary_key=True, null=False)
    emp_id = models.ForeignKey(EmployeeMaster, to_field="emp_id", on_delete=models.CASCADE)
    registers_code = models.ForeignKey(RegistersMaster, on_delete=models.CASCADE)
    role_id = models.ForeignKey(RegistersRoleMaster, on_delete=models.CASCADE)
    created_user = models.ForeignKey(EmployeeMaster, to_field="emp_id", related_name='assigner_emp_id', on_delete=models.CASCADE, null=True)
    designation = models.CharField(max_length=150, null=True)
    branch_code = models.ForeignKey(BranchMaster, to_field="branch_code", on_delete=models.CASCADE)
    modified_date = models.DateTimeField(auto_now_add=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True, null=True)  # u can select datetime now
    is_active = models.BooleanField(default=True)
    modified_user = models.ForeignKey(EmployeeMaster, to_field="emp_id", related_name='modifier_emp_id', on_delete=models.CASCADE, null=True)
    branch_id = models.ForeignKey(BranchMaster, related_name="role_branch_id", on_delete=models.CASCADE)

    class Meta:
        db_table = "employee_register_role_master"

class AuditorConnectionMaster(models.Model):
    """
    AuditorConnectionMaster Model
    """
    emp_reg_role_id = models.AutoField(primary_key=True, null=False)
    emp_id = models.ForeignKey(EmployeeMaster, to_field="emp_id", related_name='employee_audit', on_delete=models.CASCADE, null=True)
    registers_code = models.ForeignKey(RegistersMaster, on_delete=models.CASCADE)
    role_id = models.ForeignKey(RegistersRoleMaster, on_delete=models.CASCADE)
    created_user = models.ForeignKey(EmployeeMaster, to_field="emp_id", related_name='assigner_emp', on_delete=models.CASCADE, null=True)
    designation = models.CharField(max_length=150, null=True)
    branch_code = models.ForeignKey(BranchMaster, to_field="branch_code", related_name='audit_branch', on_delete=models.CASCADE)
    assigner_branch_code = models.ForeignKey(BranchMaster, to_field="branch_code", related_name='assigner_branch', on_delete=models.CASCADE)
    modified_date = models.DateTimeField(auto_now_add=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True, null=True)  # u can select datetime now
    is_active = models.BooleanField(default=True)
    modified_user = models.ForeignKey(EmployeeMaster, to_field="emp_id", related_name='audit_modifier_emp', on_delete=models.CASCADE, null=True)
    branch_id = models.ForeignKey(BranchMaster, related_name="auditrole_branch_id", on_delete=models.CASCADE)


    class Meta:
        db_table = "auditor_connection_master"

class Session(models.Model):
    """
    Session Model
    """
    ses_id = models.AutoField(primary_key=True)
    ses_key = models.CharField(max_length=200, null=True)
    ses_data = models.CharField(max_length=200, null=True)

    class Meta:
        db_table = "session_data"

class Log(models.Model):
    """
    Log Model
    """
    log_id = models.AutoField(primary_key = True)
    emp_id = models.ForeignKey(EmployeeMaster, to_field="emp_id", on_delete=models.CASCADE)
    log_date = models.DateTimeField(auto_now_add=True)
    log_ip= models.CharField(max_length=200, null=True, blank=True)
    in_out = models.DateTimeField(null=True)
    ses_key = models.CharField(max_length=200, null=True)
    status = models.CharField(max_length=200, null=True)

    class Meta:
        db_table = "log_data"


class PhoneMaster(models.Model):
    Mobile = models.IntegerField(blank=False)
    isVerified = models.BooleanField(blank=False, default=False)
    counter = models.IntegerField(default=0, blank=False)

    class Meta:
        db_table = "phone_master"

    def __str__(self):
        return str(self.Mobile)

class RuleSetup(models.Model):
    register = models.CharField(max_length=250, null=True, blank=True)
    rule_type = models.CharField(max_length=250, null=True, blank=True)
    rule_data = models.JSONField(null=True, blank=True)
    modified_date = models.DateField(auto_now= True,null=True)
    created_user = models.ForeignKey(EmployeeMaster, to_field="emp_id",null=True, related_name='rulesetup_creator', on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    modified_user = models.ForeignKey(EmployeeMaster,null=True, to_field="emp_id", related_name='rulesetup_modifier', on_delete=models.CASCADE)
    class Meta:
        db_table = "rule_setup_table"

    def __str__(self):
        return str(self.register)

class BranchVerification(models.Model):
    branch_code = models.ForeignKey(BranchMaster, to_field="branch_code", on_delete=models.CASCADE,null=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    modified_date =  models.DateField(auto_now= True,null=True)
    created_user = models.ForeignKey(EmployeeMaster, to_field="emp_id",null=True, related_name='branch_verify_creator', on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    modified_user = models.ForeignKey(EmployeeMaster, to_field="emp_id",null=True, related_name='branch_verify_modifier', on_delete=models.CASCADE)

    class Meta:
        db_table = "branch_verification_table"

    def __str__(self):
        return str(self.start_date)

class PropertyDocuments(models.Model):
    id = models.AutoField(primary_key=True)
    date = models.DateField(auto_now=True)
    source_branch = models.ForeignKey(BranchMaster, to_field="branch_code", on_delete=models.CASCADE, null=True, related_name='from_branch')
    # Branch where the outward mail originated from
    destination_branch = models.ForeignKey(BranchMaster, to_field="branch_code", on_delete=models.CASCADE, null=True, related_name='to_branch')
    # Branch where the outward mail is going to
    sender = models.ForeignKey(EmployeeMaster, to_field="emp_id", on_delete=models.CASCADE, null=True)
    packet_id = models.CharField(max_length=50, null=True, blank=True)
    mail_type = models.CharField(max_length=50, null=True, blank=True)
    remarks = models.CharField(max_length=250, blank=True, null=True)
    packet_contents = models.JSONField(null=True)
    status = models.CharField(default='Pending',max_length=50, null=True,blank=True)
    ho_remarks = models.CharField(max_length=250, null=True, blank=True)

    class Meta:
        db_table = "property_document_table"
        ordering = ['packet_id']

    def __str__(self):
        return str(self.packet_id)

class LocationMaster(models.Model):
    """
    table structure for asset registers
    """
    id = models.AutoField(primary_key = True)
    location_code = models.ForeignKey(BranchMaster, to_field="branch_code", on_delete=models.CASCADE, null=True)
    address = models.CharField(max_length=250, null=True, blank=True)
    city = models.CharField(max_length=150, null=True, blank=True)
    pin_code = models.CharField(max_length=20, null=True, blank=True)
    latittude = models.CharField(max_length=100, null=True, blank=True)
    longitude = models.CharField(max_length=100, null=True, blank=True)
    building = models.CharField(max_length=100, null=True, blank=True)
    floor = models.CharField(max_length=100, null=True, blank=True)
    room = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        db_table = 'locationmaster'
        ordering= ['id']

    def __str__(self):
        return f'{self.id}'
    

class DesignationMatrix(models.Model):
    """
    Table stucture for designation matrix
    """
    id = models.AutoField(primary_key=True)
    created_date = models.DateTimeField(auto_now=True)
    role_type = models.CharField(max_length=250, null=False, blank=False)
    role_name = models.CharField(max_length=250, null=False, blank=False)
    role_code = models.CharField(max_length=250, null=False, blank=False)
    role_dept = models.CharField(max_length=250, null=True, blank=True)
    designations = models.JSONField(null=True, blank=True)
    last_modified_user = models.CharField(max_length=250, null=True, blank=True)
    last_modified_date = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(null=False, blank=False, default=True)

    class Meta:
        db_table = 'designation_matrix'
        ordering= ['id']

    def __str__(self):
        return f'{self.id}'