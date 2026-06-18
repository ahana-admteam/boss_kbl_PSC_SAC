from box import Box
from django.shortcuts import render, redirect
from ..models import *

def account_log(request,review_type,review_id):
    config_data = Box(request.session['config_data'])
    tenant = config_data.tenant
    tenant_image = config_data.logo_image.image_path
    try:
        if review_type == 'PSC':
            acc_data = PSCTable.objects.filter(psc_rec_id=review_id).values(
                    'psc_rec_id', 'psc_users_log'
                )
            context = {'title': 'PSC Account Log', 'tenant_image': tenant_image,
            "tenant": tenant,'acc_data':acc_data[0],'review_type':review_type}
            return render(request, 'preliminaryscreeningcommittee_review/account_log.html', context=context)
        elif review_type == 'SAC':
            acc_data = SACTable.objects.filter(sac_rec_id=review_id).values(
                'sac_rec_id', 'sac_users_log'
            )
            context = {'title': 'SAC Account Log', 'tenant_image': tenant_image,
            "tenant": tenant,'acc_data':acc_data[0],'review_type':review_type}
            return render(request, 'preliminaryscreeningcommittee_review/account_log.html', context=context)
    except Exception as e:
        print('account log error',e)
        return redirect('account_dashboard')
        
        
def account_dashboard(request):
    config_data = Box(request.session['config_data'])
    tenant = config_data.tenant
    tenant_image = config_data.logo_image.image_path
    try:
        if request.method == 'POST':
            review_type = request.POST['review_type']
            review_id = request.POST['review_id']
            return account_log(request,review_type,review_id)
            
        else:
            context = {'title': 'Accounts Log Dashboard', 'tenant_image': tenant_image,
            "tenant": tenant}
            return render(request, 'preliminaryscreeningcommittee_review/account_logs_db.html', context=context)
    except Exception as e:
        print('account log error',e)
        return redirect('account_dashboard')



