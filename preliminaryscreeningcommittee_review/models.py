from django.db import models
from boss_admin.models import BranchMaster
from datetime import date, timedelta, datetime

class MOMTable(models.Model):
    """
    MOM Table
    """
    id = models.AutoField(primary_key=True, null=False,blank=False)
    created_user = models.CharField(max_length=150,null=False,blank=False)
    meeting_id = models.CharField(max_length=150,null=False,blank=False)
    mom_creation_date = models.DateTimeField(null=False,blank=False)
    mom_date = models.DateTimeField(null=False,blank=False)
    audience = models.JSONField(null=False,blank=False) #json
    loan_count = models.JSONField(null=True,blank=True)
    mom_closure_date = models.DateTimeField(null=True,blank=True)
    active = models.BooleanField(default=True,null=False,blank=False)
    last_modified_date = models.DateTimeField(null=False,blank=False,auto_now=True)
    last_modified_user = models.CharField(max_length=150,null=False,blank=False)
    review_type = models.CharField(max_length=150,null=False,blank=False)
    mom_users_log = models.JSONField(null=True, blank=True) #json

    class Meta:
        db_table = "mom_table"

    def __int__(self):
        return self.id 

class CustomerTable(models.Model):
    """
    Customer Table
    """      
    id = models.AutoField(primary_key=True, null=False,blank=False)
    creation_date = models.DateTimeField(null=False,blank=False,auto_now=True)
    created_user = models.CharField(max_length=150,null=False,blank=False)
    psc_rec_id = models.CharField(max_length=150,null=True,blank=True,unique=True)
    sac_rec_id = models.CharField(max_length=150,null=True,blank=True,unique=True)
    psc_review_id = models.CharField(max_length=150,null=True,blank=True,unique=True)
    sac_review_id = models.CharField(max_length=150,null=True,blank=True,unique=True)
    review_type = models.CharField(max_length=150,null=True,blank=True)
    cust_id = models.CharField(max_length=150,null=False,blank=False)
    borrower_name = models.CharField(max_length=150,null=False,blank=False)
    branch_code = models.ForeignKey(BranchMaster,null=True,blank=True, on_delete=models.CASCADE) #foreign key..
    region_name = models.CharField(max_length=150,null=True,blank=True)
    total_exposure = models.CharField(max_length=150,null=True,blank=True)
    acc_count = models.CharField(max_length=150,null=True,blank=True)
    current_role = models.CharField(max_length=150,null=True,blank=True)
    status = models.CharField(max_length=150,null=True,blank=True)
    npa_status = models.BooleanField(default=True,null=False,blank=False)
    last_modified_date = models.DateTimeField(null=False,blank=False,auto_now=True)
    last_modified_user = models.CharField(max_length=150,null=False,blank=False)
    sac_details = models.JSONField(null=True, blank=True) #json
    lapses_details = models.JSONField(null=True, blank=True) #json
    

    class Meta:
        db_table = "customer_table"

    def __int__(self):
        return self.id
     
class PSCTable(models.Model):
    """
    PSC Table
    """      
    id = models.AutoField(primary_key=True, null=False,blank=False)
    creation_date = models.DateTimeField(null=False,blank=False,auto_now=True)
    created_user = models.CharField(max_length=150,null=False,blank=False)
    psc_rec_id = models.CharField(max_length=150,null=True,blank=True)
    branch_code = models.ForeignKey(BranchMaster,null=False,blank=False, on_delete=models.CASCADE) #foreign key..
    region_name = models.CharField(max_length=150,null=False,blank=False)
    cust_id = models.CharField(max_length=150,null=False,blank=False)
    facility_num = models.CharField(max_length=150,null=False,blank=False)
    sanc_limit = models.BigIntegerField(null=False,blank=False)
    npa_date = models.DateTimeField(null=False,blank=False)
    nap_tag = models.CharField(max_length=150,null=False,blank=False)
    npa_status = models.BooleanField(default=True,null=False,blank=False)
    status = models.CharField(max_length=150,null=True,blank=True)
    current_role = models.CharField(max_length=150,null=True,blank=True)
    borrower_name = models.CharField(max_length=150,null=False,blank=False)
    address = models.CharField(max_length=150,null=True,blank=True)
    constitution = models.CharField(max_length=150,null=True,blank=True)
    partners = models.CharField(max_length=150,null=True,blank=True)
    establishment_date = models.DateTimeField(null=True,blank=True)
    networth = models.BigIntegerField(null=True,blank=True)
    dealing_since = models.DateTimeField(null=True,blank=True)
    business_nature = models.CharField(max_length=500,null=True,blank=True)
    guarantors_name = models.CharField(max_length=150,null=True,blank=True)
    past_performance = models.CharField(max_length=500,null=True,blank=True)
    npa_reasons = models.CharField(max_length=500,null=True,blank=True)
    recovery_steps = models.CharField(max_length=500,null=True,blank=True)
    staff_accountability = models.JSONField(null=True, blank=True) #json
    ob_branch_head = models.CharField(max_length=500,null=True,blank=True)
    ob_regional_head = models.CharField(max_length=500,null=True,blank=True)
    ob_dept_head = models.CharField(max_length=500,null=True,blank=True)
    reject_remarks = models.JSONField(null=True, blank=True) #json
    mom_lapse = models.CharField(max_length=500,null=True,blank=True)
    mom_lapse_desc = models.JSONField(null=True, blank=True) #json
    mom_br_head = models.JSONField(null=True, blank=True) #json
    mom_id = models.ForeignKey(MOMTable,null=True,blank=True,on_delete=models.CASCADE)
    last_modified_date = models.DateTimeField(null=False,blank=False,auto_now=True)
    last_modified_user = models.CharField(max_length=150,null=False,blank=False)
    current_role = models.CharField(max_length=150,null=True,blank=True)
    form_creation_date = models.DateTimeField(null=True,blank=True)
    psc_users_log = models.JSONField(null=True, blank=True) #json

    
    class Meta:
        db_table = "psc_table"

    def __int__(self):
        return self.id
     
class CreditFacilityTable(models.Model):
    """
    Credit Facility Table
    """
    id = models.AutoField(primary_key=True, null=False,blank=False)
    creation_date = models.DateTimeField(null=False,blank=False,auto_now=True)
    created_user = models.CharField(max_length=150,null=False,blank=False)
    psc_id = models.ForeignKey(CustomerTable, on_delete=models.CASCADE)
    credit_feci_slno = models.IntegerField(null=False,blank=False)
    reference_num = models.CharField(max_length=150,null=False,blank=False)
    sanction_date = models.DateTimeField(null=False,blank=False)
    account_nature = models.CharField(max_length=150,null=False,blank=False)
    advance_nature = models.CharField(max_length=150,null=False,blank=False)
    lan = models.CharField(max_length=150,null=False,blank=False)
    sanctioned_limit = models.DecimalField(max_digits=12, decimal_places=2, null=False,blank=False)
    due_date = models.DateTimeField(null=False,blank=False)
    npa_balance = models.DecimalField(max_digits=12, decimal_places=2, null=False,blank=False)
    balance = models.DecimalField(max_digits=12, decimal_places=2, null=False,blank=False)
    advance_purpose = models.CharField(max_length=500,null=False,blank=False)
    npa_date = models.DateTimeField(null=False,blank=False)
    asset_classification = models.CharField(max_length=150,null=False,blank=False)
    last_modified_date = models.DateTimeField(null=False,blank=False,auto_now=True)
    last_modified_user = models.CharField(max_length=150,null=False,blank=False)
    cf_aod_data = models.JSONField(null=True, blank=True, default=dict) #json
    doc_date = models.DateTimeField(null=False,blank=False,default=datetime.now())
    
    class Meta:
        db_table = "creditfacility_table"

    def __int__(self):
        return self.id 
    
class SecuritiesTable(models.Model):
    """
    Securities Table					
    """				
    id = models.AutoField(primary_key=True, null=False,blank=False)
    creation_date = models.DateTimeField(null=False,blank=False,auto_now=True)
    created_user = models.CharField(max_length=150,null=False,blank=False)
    psc_id = models.ForeignKey(CustomerTable, on_delete=models.CASCADE)
    security_nature = models.CharField(max_length=150,null=False,blank=False) #should it be dd?
    lan = models.CharField(max_length=150,null=False,blank=False)
    security_type = models.CharField(max_length=150,null=False,blank=False)
    sanction_valuation = models.DecimalField(max_digits=12, decimal_places=2, null=False,blank=False)
    sanction_valuation_date = models.DateTimeField(null=False,blank=False)
    latest_valuation = models.DecimalField(max_digits=12, decimal_places=2, null=False,blank=False)
    latest_valuation_date = models.DateTimeField(null=False,blank=False)
    insurance_valid_upto = models.DateTimeField(null=True,blank=True)
    insurance_value = models.DecimalField(max_digits=12, decimal_places=2, null=False,blank=False)
    cersai_num = models.CharField(max_length=150,null=False,blank=False)
    last_modified_date = models.DateTimeField(null=False,blank=False,auto_now=True)
    last_modified_user = models.CharField(max_length=150,null=False,blank=False)

    class Meta:
        db_table = "securities_table"

    def __int__(self):
        return self.id 

class SACTable(models.Model):
    """
    SAC Table
    """
    id = models.AutoField(primary_key=True, null=False,blank=False)
    creation_date = models.DateTimeField(null=False,blank=False,auto_now=True)
    created_user = models.CharField(max_length=150,null=False,blank=False)
    psc_rec_id = models.ForeignKey(PSCTable, on_delete=models.CASCADE)
    sac_rec_id = models.CharField(max_length=150,null=False,blank=False)
    emp_name = models.CharField(max_length=150,null=True,blank=True)
    staff_no = models.CharField(max_length=150,null=True,blank=True)
    present_designation = models.CharField(max_length=150,null=True,blank=True)
    present_working = models.CharField(max_length=150,null=True,blank=True)
    status = models.CharField(max_length=150,null=True,blank=True)    
    psc_date = models.DateTimeField(null=False,blank=False)
    lapses_data = models.JSONField(null=True,blank=True) #json 
    reject_remarks = models.JSONField(null=True, blank=True) #json
    ob_regional_head = models.CharField(max_length=500,null=True,blank=True)
    ob_dept_head = models.CharField(max_length=500,null=True,blank=True)
    mom_lapse = models.CharField(max_length=500,null=True,blank=True)
    mom_lapse_desc = models.JSONField(null=True, blank=True) #json
    mom_br_head = models.JSONField(null=True, blank=True) #json
    mom_id = models.ForeignKey(MOMTable,null=True,blank=True,on_delete=models.CASCADE)
    last_modified_date = models.DateTimeField(null=False,blank=False,auto_now=True)
    last_modified_user = models.CharField(max_length=150,null=False,blank=False)
    current_role = models.CharField(max_length=150,null=True,blank=True)
    sac_users_log = models.JSONField(null=True, blank=True) #json

    class Meta:
        db_table = "sac_table"

    def __int__(self):
        return self.id 
    
class DocumentTable(models.Model):
    """
    Document Table
    """
    document_id = models.AutoField(primary_key=True, null=False,blank=False)
    created_user = models.CharField(max_length=150,null=True,blank=True)
    section = models.CharField(max_length=150,null=True,blank=True)
    review_type = models.CharField(max_length=150,null=True,blank=True)
    review_id = models.CharField(max_length=100, null=True, blank=True) 
    app = models.CharField(max_length=150,null=True,blank=True)
    file = models.TextField(null=True,blank=True)
    file_name = models.CharField(max_length=150,null=True,blank=True)
    file_type = models.CharField(max_length=150,null=True,blank=True)
    last_modified_date = models.DateTimeField(null=True,blank=True,auto_now=True)
    last_modified_user = models.CharField(max_length=150,null=True,blank=True)



    class Meta:
            db_table = "document_table"

    def __str__(self):
        return self.document_id 

# from preliminaryscreeningcommittee_review.models import MOMTable, CustomerTable, PSCTable, CreditFacilityTable, SecuritiesTable, SACTable, DocumentTable

