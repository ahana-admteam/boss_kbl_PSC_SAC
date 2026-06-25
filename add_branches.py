import os
import django
import sys
import pandas as pd

def run():
    sys.path.append(os.getcwd())
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'boss_v1.settings')
    django.setup()

    from boss_admin.models import BranchMaster

    df = pd.read_excel('AD_UAT_list_PSC_SAC_Testing.xlsx', sheet_name='All Users', skiprows=3)

    branches = df[['Unnamed: 3', 'Unnamed: 5']].dropna(subset=['Unnamed: 3']).drop_duplicates()
    print('Total unique branches in excel:', len(branches))

    added = 0
    for _, row in branches.iterrows():
        bcode = str(row['Unnamed: 3']).strip()
        if '.' in bcode: bcode = bcode.split('.')[0]
        bname = str(row['Unnamed: 5']).strip()
        if bcode == '-' or not bcode.isdigit():
            continue
        
        if len(bcode) <= 3:
            bcode = bcode.zfill(3)
            
        if not BranchMaster.objects.filter(branch_code=bcode).exists():
            BranchMaster.objects.create(
                branch_code=bcode,
                branch_name=bname,
                zone='Testing Zone',
                zone_name='Testing Zone',
                created_user='script'
            )
            added += 1

    print(f'Added {added} new branches.')

if __name__ == "__main__":
    run()
