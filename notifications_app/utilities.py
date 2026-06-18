from .models import Notification

def create_notification(from_user, to_user, register_id, register_type, register_role, choice, model_name, hyper_link, extra_id):
    print('notify')
    try:
        notification = Notification.objects.create(to_user=to_user,registers_id=register_id, register_type=register_type, notification_type=choice, register_role=register_role, created_by=from_user, model_name=model_name, hyper_link=hyper_link, extra_id=extra_id)
    except Exception as e:
        print(e)