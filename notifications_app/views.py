from django.shortcuts import render, redirect
from .models import Notification
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from box import Box

# Create your views here.

def notifications(request):
    config_data = Box(request.session['config_data'])
    tenant = config_data.tenant
    title = config_data.module.IN001.display_name
    tenant_image = config_data.logo_image.image_path
    goto = request.GET.get('goto', '')
    notification_id = request.GET.get('notification', 0)
    extra_id = request.GET.get('extra_id', 0)

    if goto != '':
        notification = Notification.objects.get(pk=notification_id)

        if notification.notification_type == Notification.SENT:
            return redirect('view_notification', notification=notification.id, extra_id=notification.extra_id)
        elif notification.notification_type == Notification.RECEIVED:
            return redirect('view_notification', notification=notification.id, extra_id=notification.extra_id)
        elif notification.notification_type == Notification.APPROVED:
            return redirect('view_notification', notification=notification.id, extra_id=notification.extra_id)

    return render(request, 'notifications_app/notification.html', context={'title':title, 'tenant_image': tenant_image, "tenant":tenant})


def view_notification(request, notification, extra_id):
    my_notification = Notification.objects.get(pk=notification)
    my_notification.is_read = True
    my_notification.save()
    config_data = Box(request.session['config_data'])
    tenant = config_data.tenant
    title = config_data.module.IN001.display_name
    tenant_image = config_data.logo_image.image_path
    model_name = my_notification.model_name
    # if model_name == "InwardMailTable":
    #     model_name = InwardMailTable
    #     model_data = model_name.objects.filter(pk=extra_id).values()
    # if model_name == "OutwardMailTable":
    #     model_name = OutwardMailTable
    #     model_data = model_name.objects.filter(pk=extra_id).values()
        
    data = Notification.objects.filter(pk=notification).values("register_type", "registers_id", "created_by__emp_name", "created_at")
    context = {'title':title, 'tenant_image': tenant_image, "tenant":tenant, "notification_data": data, 'model_data':model_data}
    return render(request, 'notifications_app/view_notification.html', context=context )


@csrf_exempt
def clear_notification(request):
    Notification.objects.filter(to_user=request.session["emp_id"]).update(is_seen=True)
    return JsonResponse({"msg": 'All the notification cleared '}, status=200)