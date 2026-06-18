from notifications_app.models import Notification
from itertools import chain
from boss_admin.views import my_login_required
from django.contrib.auth.decorators import login_required


global notis, temp
def notifications(request):
    if request.session.get('emp_id') is not None and request.session.get('new_roles') is not None  :
        try:
            login_roles = request.session['new_roles']
            roles = login_roles.split("_")
            note = Notification.objects.filter(register_role__role_desc="", is_read=True, is_seen= False)
            for role in roles:
                if role == 'doc001custodian' and Notification.objects.filter(register_role__role_desc=role, is_read=False, is_seen=False).exists() :
                    note = note | Notification.objects.filter(register_role__role_desc=role, is_read=False, is_seen=False, to_user = request.session['emp_id'])
                elif Notification.objects.filter(register_role__role_desc=role, is_read=False, is_seen=False).exists() :
                    note = note | Notification.objects.filter(register_role__role_desc=role, is_read=False, is_seen=False)
            note = note | Notification.objects.filter(to_user=request.session['emp_id'], registers_id='KEY001', is_read=False, is_seen=False)
            return {'notifications': note}
        except Exception as e:
            print(e)
            return {'notifications': []}

    else:
        print("else condition")
        return {'notifications': []}
