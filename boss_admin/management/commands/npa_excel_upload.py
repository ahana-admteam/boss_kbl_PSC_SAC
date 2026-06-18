from django.core.management.base import BaseCommand, CommandError
import pandas as pd
from datetime import datetime
from preliminaryscreeningcommittee_review.models import PSCTable, CustomerTable  # Import your PSCTable model and BranchMaster model
import os
from boss_v1.settings.base import BASE_DIR
from boss_admin.models import BranchMaster
import pandas as pd
from datetime import datetime
from collections import defaultdict

class Command(BaseCommand):
    help = "Upload data from Excel to PSCTable model"


    def get_excel_file(self, filename):
        #app_path = self.get_current_app_path()
        file_path = os.path.join(BASE_DIR, filename)
        return file_path
    
    def add_arguments(self, parser):
        parser.add_argument('filenames',
                            nargs='+',
                            type=str,
                            help="Inserts Upazila Office reports from CSV file")
        # Named (optional) arguments
        parser.add_argument(
            '--acland',
            action='store_true',
            help='Insert AC land office reports rather than UNO office',
        )

    def modify_br_code(self, str_br):
        code = str(int(str_br))
        if len(code) <= 3:
            return code.zfill(3)
        elif len(code) == 4:
            return code
        else:
            raise ValueError("Branch code must be 3 or 4 digits")

    def handle(self, *args, **options):
        # Path to your Excel file
        # excel_file_path = 'C:/Users/SrikanthP/Github/boss_v1/preliminaryscreeningcommittee_review/psc_data.xlsx'
        for filename in options['filenames']:
            self.stdout.write(self.style.SUCCESS('Reading:{}'.format(filename)))
            file_path = self.get_excel_file(filename)
        try:
            # Read data from Excel file
            df = pd.read_excel(file_path)
        except FileNotFoundError:
            raise CommandError("File {} does not exist".format(file_path))


        customer_data = defaultdict(lambda: {
            'total_exposure': 0,
            'acc_count': 0,
            'facility_nums': [],
            'region_name': '',
            'branch_code_id': '',
            'cust_id': '',
            'psc_objects': []
        })

        

        # First pass: Aggregate data and create PSCTable objects
        for index, row in df.iterrows():
            # branch_code = str(row['BRANCH_CODE']).zfill(3)
            # region_name = BranchMaster.objects.filter(branch_code=branch_code).values('zone_name')[0]['zone_name']
            # branch_code_id = BranchMaster.objects.filter(branch_code=branch_code).values('sl_no')[0]['sl_no']

            
            


            
            branch_code = self.modify_br_code(str(row['BRANCH_CODE']))
            # print('br_code', branch_code)
            branch_info = BranchMaster.objects.filter(branch_code=branch_code).values('zone_name', 'sl_no').first()
            # print(branch_info)
            if not branch_info:
                
                self.stdout.write(self.style.WARNING(f"Branch code {branch_code} not found for cust id {row['CUSTOMER_ID']}"))
                continue

            region_name = branch_info['zone_name']
            branch_code_id = branch_info['sl_no']
            # branch_code_id = BranchMaster.objects.filter(branch_code=branch_code).values('sl_no')[0]['sl_no']
            
            cust_id = row['CUSTOMER_ID']
            borrower_name = row['BORROWER_NAME']
            # facility_num = str(row['FACILITY_NUMBER']).zfill(16)  # Ensure 16-digit format
            facility_num = str(row['FACILITY_NUMBER']).strip("'").zfill(16)  # Ensure 16-digit format
            # Create PSCTable object
            psc_object = PSCTable(
                created_user='created_user', 
                creation_date=datetime.now(),
                branch_code_id=branch_code_id,
                region_name=region_name, 
                cust_id=cust_id,
                facility_num=facility_num,  # Now always 16 digits
                sanc_limit=row['SANCTION_LIMIT'],
                npa_date=row['NPA_DATE'],
                nap_tag=row['NPA_TAG'],
                borrower_name=row['BORROWER_NAME'],
                last_modified_date=datetime.now(),
                last_modified_user="created_user",
                psc_users_log={"bo_maker": [], "bo_checker": [], "ro_maker": [], "ro_checker": [], "ho_maker": [], "ho_checker": [], "convener": []}
            )

            # Store in customer_data for further processing
            customer_data[cust_id]['total_exposure'] += row['SANCTION_LIMIT']
            customer_data[cust_id]['acc_count'] += 1
            customer_data[cust_id]['facility_nums'].append(facility_num)
            customer_data[cust_id]['region_name'] = ''
            customer_data[cust_id]['branch_code_id'] = ''
            customer_data[cust_id]['cust_id'] = cust_id
            customer_data[cust_id]['psc_objects'].append(psc_object)
            customer_data[cust_id]['borrower_name'] = borrower_name


        for cust_id, data in customer_data.items():
            today_date = datetime.now().strftime("%d%m%Y")
            psc_rec_id = f'PSC{cust_id}{today_date}'

            # Create CustomerTable object
            customer_object = CustomerTable(
                created_user='created_user',
                creation_date=datetime.now(),
                psc_rec_id=psc_rec_id,
                branch_code_id=data['branch_code_id'],
                region_name=data['region_name'],
                cust_id=data['cust_id'],
                borrower_name=data['borrower_name'],
                total_exposure=data['total_exposure'],
                acc_count=data['acc_count'],
                npa_status= True,
                last_modified_date=datetime.now(),
                last_modified_user="created_user"
            )

            customer_object.save()

            # Assign psc_rec_id to psc_objects and save them
            for psc_object in data['psc_objects']:
                psc_object.psc_rec_id = psc_rec_id
                psc_object.save()
            print(f'Customer Object Created: cust_id={customer_object.cust_id}, creation_date={customer_object.creation_date}, total_exposure={customer_object.total_exposure},{customer_object.region_name},{customer_object.borrower_name}')
            print(f'Updated {len(data["psc_objects"])} PSC Objects with psc_rec_id={psc_rec_id}')
        

        
        self.stdout.write(self.style.SUCCESS('Data uploaded successfully'))


