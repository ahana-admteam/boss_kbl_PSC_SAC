from django.core.management.base import BaseCommand, CommandError
import pandas as pd
from datetime import datetime
from boss_admin.models import BranchMaster  # Import your PSCTable model and BranchMaster model
import os
from boss_v1.settings.base import BASE_DIR

class Command(BaseCommand):
    help = "Upload data from Excel to BranchMaster model"


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

    def handle(self, *args, **options):
        
        for filename in options['filenames']:
            self.stdout.write(self.style.SUCCESS('Reading:{}'.format(filename)))
            file_path = self.get_excel_file(filename)
        try:
            # Read data from Excel file
            df = pd.read_excel(file_path)
        except FileNotFoundError:
            raise CommandError("File {} does not exist".format(file_path))

        # Iterate through each row of the dataframe
        for index, row in df.iterrows():
            
            branch_code = str(row['Branch Code']).zfill(3)  # Assuming you have a column named 'branch_code' in your Excel
            region_code = str(row['Region Code']).zfill(3)

            # Create BranchMaster object and populate fields
            branch_object = BranchMaster(
                created_user='py script', 
                modified_date=datetime.now(),
                branch_name=row['Branch Name'],
                branch_code=branch_code,  # Assuming you have a column named 'branch_name' in your Excel
                zone=region_code, 
                zone_name=row['Region Name'],
                city=row['City'],
                state=row['State'],
                created_date=datetime.now(),
                modified_user='py script'
            )
            
            # Save the object to the database
            branch_object.save()
        print(branch_object)
        self.stdout.write(self.style.SUCCESS('Data uploaded successfully'))


# Branch Code	
# Branch Name
# Region Code
# Region Name
# City
# State