"""
Management command to seed test users for local development.
Creates branches, employees, register roles, and role assignments
for PSC (3 makers, 3 checkers), SAC (3 makers, 3 checkers), and 1 Convener.

Usage: python manage.py seed_local_users
"""
from django.core.management.base import BaseCommand
from boss_admin.models import (
    BranchMaster, EmployeeMaster, RegistersMaster,
    RegistersRoleMaster, EmployeeRegisterRoleMaster
)


# ── Role definitions ────────────────────────────────────────────────
# role_desc values are what the PSC/SAC views check in session['new_roles']
ROLES = [
    # PSC roles
    {'role_name': 'PSC BO Maker',   'role_desc': 'psc001maker1',   'reg': 'PSC001'},
    {'role_name': 'PSC BO Checker', 'role_desc': 'psc001checker1', 'reg': 'PSC001'},
    {'role_name': 'PSC RO Maker',   'role_desc': 'psc001maker2',   'reg': 'PSC001'},
    {'role_name': 'PSC RO Checker', 'role_desc': 'psc001checker2', 'reg': 'PSC001'},
    {'role_name': 'PSC HO Maker',   'role_desc': 'psc001maker3',   'reg': 'PSC001'},
    {'role_name': 'PSC HO Checker', 'role_desc': 'psc001checker3', 'reg': 'PSC001'},
    # SAC roles
    {'role_name': 'SAC RO Maker',   'role_desc': 'sac001maker2',   'reg': 'PSC001'},
    {'role_name': 'SAC RO Checker', 'role_desc': 'sac001checker2', 'reg': 'PSC001'},
    {'role_name': 'SAC HO Maker',   'role_desc': 'sac001maker3',   'reg': 'PSC001'},
    {'role_name': 'SAC HO Checker', 'role_desc': 'sac001checker3', 'reg': 'PSC001'},
    # Convener
    {'role_name': 'PSC Convener',   'role_desc': 'psc001convener', 'reg': 'PSC001'},
]

# ── Test users ──────────────────────────────────────────────────────
# Each user maps to exactly one role_desc for simplicity.
# domain_id is what they type in the login box; pwd is their password.
USERS = [
    # PSC 3 makers
    {'domain_id': 'psc_bo_maker',  'emp_id': 'PSC_M1', 'emp_name': 'PSC BO Maker',  'pwd': 'test123', 'designation': 'BO Maker',  'branch': 'BR001', 'role_desc': 'psc001maker1'},
    {'domain_id': 'psc_ro_maker',  'emp_id': 'PSC_M2', 'emp_name': 'PSC RO Maker',  'pwd': 'test123', 'designation': 'RO Maker',  'branch': 'BR002', 'role_desc': 'psc001maker2'},
    {'domain_id': 'psc_ho_maker',  'emp_id': 'PSC_M3', 'emp_name': 'PSC HO Maker',  'pwd': 'test123', 'designation': 'HO Maker',  'branch': 'BR003', 'role_desc': 'psc001maker3'},
    # PSC 3 checkers
    {'domain_id': 'psc_bo_checker','emp_id': 'PSC_C1', 'emp_name': 'PSC BO Checker', 'pwd': 'test123', 'designation': 'BO Checker','branch': 'BR001', 'role_desc': 'psc001checker1'},
    {'domain_id': 'psc_ro_checker','emp_id': 'PSC_C2', 'emp_name': 'PSC RO Checker', 'pwd': 'test123', 'designation': 'RO Checker','branch': 'BR002', 'role_desc': 'psc001checker2'},
    {'domain_id': 'psc_ho_checker','emp_id': 'PSC_C3', 'emp_name': 'PSC HO Checker', 'pwd': 'test123', 'designation': 'HO Checker','branch': 'BR003', 'role_desc': 'psc001checker3'},
    # SAC 3 makers
    {'domain_id': 'sac_ro_maker',  'emp_id': 'SAC_M2', 'emp_name': 'SAC RO Maker',  'pwd': 'test123', 'designation': 'RO Maker',  'branch': 'BR002', 'role_desc': 'sac001maker2'},
    {'domain_id': 'sac_ho_maker',  'emp_id': 'SAC_M3', 'emp_name': 'SAC HO Maker',  'pwd': 'test123', 'designation': 'HO Maker',  'branch': 'BR003', 'role_desc': 'sac001maker3'},
    {'domain_id': 'sac_bo_maker',  'emp_id': 'SAC_M1', 'emp_name': 'SAC BO Maker',  'pwd': 'test123', 'designation': 'BO Maker',  'branch': 'BR001', 'role_desc': 'psc001maker1'},  # SAC BO uses psc001maker1 role per existing code
    # SAC 3 checkers
    {'domain_id': 'sac_ro_checker','emp_id': 'SAC_C2', 'emp_name': 'SAC RO Checker', 'pwd': 'test123', 'designation': 'RO Checker','branch': 'BR002', 'role_desc': 'sac001checker2'},
    {'domain_id': 'sac_ho_checker','emp_id': 'SAC_C3', 'emp_name': 'SAC HO Checker', 'pwd': 'test123', 'designation': 'HO Checker','branch': 'BR003', 'role_desc': 'sac001checker3'},
    {'domain_id': 'sac_bo_checker','emp_id': 'SAC_C1', 'emp_name': 'SAC BO Checker', 'pwd': 'test123', 'designation': 'BO Checker','branch': 'BR001', 'role_desc': 'psc001checker1'},  # SAC BO uses psc001checker1 role per existing code
    # Convener
    {'domain_id': 'convener',      'emp_id': 'CONV01', 'emp_name': 'PSC Convener',   'pwd': 'test123', 'designation': 'Convener',  'branch': 'BR003', 'role_desc': 'psc001convener'},
]

# ── Branch definitions ──────────────────────────────────────────────
BRANCHES = [
    {'branch_code': 'BR001', 'branch_name': 'Test Branch Office',    'zone': 'BR002'},
    {'branch_code': 'BR002', 'branch_name': 'Test Regional Office',  'zone': 'BR002'},
    {'branch_code': 'BR003', 'branch_name': 'Test Head Office',      'zone': 'BR003'},
]


class Command(BaseCommand):
    help = 'Seed local test users for PSC/SAC workflow (no LDAP required)'

    def handle(self, *args, **options):
        self.stdout.write('\n' + '=' * 60)
        self.stdout.write('  Seeding local test data for PSC/SAC')
        self.stdout.write('=' * 60)

        # 1. Create branches
        self.stdout.write('\n-- Creating branches --')
        for b in BRANCHES:
            obj, created = BranchMaster.objects.get_or_create(
                branch_code=b['branch_code'],
                defaults={
                    'branch_name': b['branch_name'],
                    'zone': b['zone'],
                }
            )
            status = 'CREATED' if created else 'EXISTS'
            self.stdout.write(f'  [{status}] {b["branch_code"]} - {b["branch_name"]}')

        # 2. Create PSC001 register if not exists
        self.stdout.write('\n-- Creating register master --')
        reg, created = RegistersMaster.objects.get_or_create(
            registers_code='PSC001',
            defaults={
                'registers_type': 'PSC',
                'registers_desc': 'Preliminary Screening Committee',
                'is_active': True,
            }
        )
        status = 'CREATED' if created else 'EXISTS'
        self.stdout.write(f'  [{status}] PSC001 - Preliminary Screening Committee')

        # 3. Create role entries in RegistersRoleMaster
        self.stdout.write('\n-- Creating role definitions --')
        role_objs = {}  # role_desc -> RegistersRoleMaster object
        for r in ROLES:
            obj, created = RegistersRoleMaster.objects.get_or_create(
                role_desc=r['role_desc'],
                defaults={
                    'role_name': r['role_name'],
                    'registers_code': RegistersMaster.objects.get(registers_code=r['reg']),
                    'is_active': True,
                }
            )
            role_objs[r['role_desc']] = obj
            status = 'CREATED' if created else 'EXISTS'
            self.stdout.write(f'  [{status}] {r["role_desc"]} ({r["role_name"]})')

        # 4. Create employees and assign roles
        self.stdout.write('\n-- Creating test users --')
        for u in USERS:
            branch = BranchMaster.objects.get(branch_code=u['branch'])

            emp, created = EmployeeMaster.objects.get_or_create(
                emp_id=u['emp_id'],
                defaults={
                    'domain_id': u['domain_id'],
                    'emp_name': u['emp_name'],
                    'pwd': u['pwd'],
                    'designation': u['designation'],
                    'branch_code': branch,
                    'branch_id': branch,
                    'email_id': f'{u["domain_id"]}@test.local',
                    'phone_number': 9999999999,
                }
            )
            if not created:
                # Update password in case it changed
                emp.pwd = u['pwd']
                emp.save()

            status = 'CREATED' if created else 'EXISTS'
            self.stdout.write(f'  [{status}] {u["domain_id"]} ({u["emp_name"]}) @ {u["branch"]}')

            # Assign role
            role_obj = role_objs[u['role_desc']]
            _, role_created = EmployeeRegisterRoleMaster.objects.get_or_create(
                emp_id=emp,
                registers_code=RegistersMaster.objects.get(registers_code='PSC001'),
                role_id=role_obj,
                branch_code=branch,
                defaults={
                    'is_active': True,
                    'branch_id': branch,
                    'designation': u['designation'],
                }
            )
            role_status = 'ASSIGNED' if role_created else 'ALREADY ASSIGNED'
            self.stdout.write(f'    +-- Role: {u["role_desc"]} [{role_status}]')

        # 5. Summary
        self.stdout.write('\n' + '=' * 60)
        self.stdout.write('  [OK] Seeding complete!')
        self.stdout.write('')
        self.stdout.write('  Login credentials (all passwords: test123):')
        self.stdout.write('  -------------------------------------------')
        self.stdout.write('  PSC Makers:   psc_bo_maker, psc_ro_maker, psc_ho_maker')
        self.stdout.write('  PSC Checkers: psc_bo_checker, psc_ro_checker, psc_ho_checker')
        self.stdout.write('  SAC Makers:   sac_bo_maker, sac_ro_maker, sac_ho_maker')
        self.stdout.write('  SAC Checkers: sac_bo_checker, sac_ro_checker, sac_ho_checker')
        self.stdout.write('  Convener:     convener')
        self.stdout.write('=' * 60 + '\n')
