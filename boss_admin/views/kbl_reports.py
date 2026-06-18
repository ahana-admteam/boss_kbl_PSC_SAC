from .authentication import my_login_required
from django.shortcuts import render, redirect, HttpResponse
from preliminaryscreeningcommittee_review.models import PSCTable, SACTable, MOMTable
from box import Box
from django.core.paginator import Paginator
from django.http import JsonResponse
import pandas as pd
from datetime import date, timedelta, datetime
from openpyxl import Workbook    

@my_login_required
def kbl_reports(request):
    config_data = Box(request.session['config_data'])
    tenant = config_data.tenant
    display_name = config_data.module
    tenant_image = config_data.logo_image.image_path
    reports_type = config_data.reports_type
    title = "Excel Reports"
    try:
        context = {'tenant_image': tenant_image, "tenant":tenant, "display_name":display_name, 'title':title,'reports_type':reports_type}
        return render(request, 'boss_admin/assign_role_page/kbl_reports.html', context)
    except Exception as e:
        print(e)

@my_login_required
def kbl_report(request,val):
    global report_dataA
    global report_dataB
    config_data = Box(request.session['config_data'])
    tenant = config_data.tenant
    tenant_image = config_data.logo_image.image_path
    reports_type = config_data.reports_type
    today = datetime.now().date()
    title = "Excel Reports"
    try:
        if request.is_ajax() or request.method == 'POST':
            if val == 'A':
                from_date = request.POST.get('from_date')
                to_date = request.POST.get('to_date')
                review_type = request.POST.get('review_type')
                if review_type == 'PSC':
                    psc_data = list(PSCTable.objects.filter(creation_date__range=(from_date, to_date),npa_status=True).values('psc_rec_id','branch_code','region_name','cust_id','borrower_name','facility_num','sanc_limit','npa_date','nap_tag','status','current_role').order_by('-last_modified_date'))
                    report_dataA = psc_data
                    return JsonResponse({'psc_data':psc_data})
                elif review_type == 'SAC':
                    # Assuming get_sac_data is a function that fetches SAC data
                    sac_data = list(SACTable.objects.filter(creation_date__range=(from_date, to_date),psc_rec_id__npa_status=True).values('sac_rec_id','psc_rec_id__branch_code','psc_rec_id__region_name','psc_rec_id__cust_id','psc_rec_id__borrower_name','psc_rec_id__facility_num','psc_rec_id__sanc_limit','psc_rec_id__npa_date','psc_rec_id__nap_tag','psc_rec_id__borrower_name','status','current_role').order_by('-last_modified_date'))
                    report_dataA = sac_data
                    return JsonResponse({'sac_data':sac_data})
                
            elif val == 'B':
                psc_BOM = list(PSCTable.objects.filter(current_role = 'BO Maker',last_modified_date__date = today).values('psc_rec_id'))
                psc_BOC = list(PSCTable.objects.filter(current_role = 'BO Checker',last_modified_date__date = today).values('psc_rec_id'))
                psc_ROM = list(PSCTable.objects.filter(current_role = 'RO Maker',last_modified_date__date = today).values('psc_rec_id'))
                psc_ROC = list(PSCTable.objects.filter(current_role = 'RO Checker',last_modified_date__date = today).values('psc_rec_id'))
                psc_HOM = list(PSCTable.objects.filter(current_role = 'HO Maker',last_modified_date__date = today).values('psc_rec_id'))
                psc_HOC = list(PSCTable.objects.filter(current_role = 'HO Checker',last_modified_date__date = today).values('psc_rec_id'))
                psc_CON = list(PSCTable.objects.filter(current_role = 'Convener',last_modified_date__date = today).values('psc_rec_id'))
                sac_ROM = list(SACTable.objects.filter(current_role = 'RO Maker',last_modified_date__date = today).values('sac_rec_id'))
                sac_ROC = list(SACTable.objects.filter(current_role = 'RO Checker',last_modified_date__date = today).values('sac_rec_id'))
                sac_HOM = list(SACTable.objects.filter(current_role = 'HO Maker',last_modified_date__date = today).values('sac_rec_id'))
                sac_HOC = list(SACTable.objects.filter(current_role = 'HO Checker',last_modified_date__date = today).values('sac_rec_id'))
                sac_CON = list(SACTable.objects.filter(current_role = 'Convener',last_modified_date__date = today).values('sac_rec_id'))
                
                report_dataB = {
                                'psc_data': {
                                    'BOM': psc_BOM,
                                    'BOC': psc_BOC,
                                    'ROM': psc_ROM,
                                    'ROC': psc_ROC,
                                    'HOM': psc_HOM,
                                    'HOC': psc_HOC,
                                    'CON': psc_CON,
                                },
                                'sac_data': {
                                    'ROM': sac_ROM,
                                    'ROC': sac_ROC,
                                    'HOM': sac_HOM,
                                    'HOC': sac_HOC,
                                    'CON': sac_CON,
                                }
                            }
                return JsonResponse({
                                'psc_data': {
                                    'BOM': psc_BOM,
                                    'BOC': psc_BOC,
                                    'ROM': psc_ROM,
                                    'ROC': psc_ROC,
                                    'HOM': psc_HOM,
                                    'HOC': psc_HOC,
                                    'CON': psc_CON,
                                },
                                'sac_data': {
                                    'ROM': sac_ROM,
                                    'ROC': sac_ROC,
                                    'HOM': sac_HOM,
                                    'HOC': sac_HOC,
                                    'CON': sac_CON,
                                }
                            })

            else:
                print('in else')
            context = {'tenant_image': tenant_image, "tenant": tenant, 'title': title}            
            return render(request, 'boss_admin/assign_role_page/kbl_reports_dashboard.html', context=context)
        else:
            context = {'tenant_image': tenant_image, "tenant":tenant, 'title':title,"reports_type_data":val}
            return render(request, 'boss_admin/assign_role_page/kbl_reports_dashboard.html', context=context)
    except Exception as e:
        print(e)

def download_excel_A(request):
    first_element_key = list(report_dataA[0].keys())[0]
    if first_element_key == 'psc_rec_id':
        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = 'attachment; filename="PSC_report.xlsx"'
        columns = ['PSC Srl Num','Branch Code','Region Name', 'Customer ID', 'Borrower Name','Facility No', 'Sanction Limit', 'NPA Date',	'NPA Tag', 'Status', 'Current Role']
        # 'psc_rec_id','branch_code','region_name','cust_id','facility_num','sanc_limit','npa_date','nap_tag','status','borrower_name','current_role'
        for item in report_dataA:
            if 'npa_date' in item:
                item['npa_date'] = item['npa_date'].replace(tzinfo=None)
        df4 = pd.DataFrame(report_dataA)
        # #print((df4.columns))
        # df4.drop(df4.columns[[11]], axis=1, inplace=True)
        df4.to_excel(excel_writer=response, engine="xlsxwriter", header=columns, index=False)  # with other applicable parameters
        return response
    elif first_element_key == 'sac_rec_id':
        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = 'attachment; filename="SAC_report.xlsx"'
        columns = ['SAC Srl Num','Branch Code','Region Name', 'Customer ID', 'Borrower Name','Facility No', 'Sanction Limit', 'NPA Date',	'NPA Tag', 'Status', 'Current Role']
        # 'psc_rec_id','branch_code','region_name','cust_id','facility_num','sanc_limit','npa_date','nap_tag','status','borrower_name','current_role'
        for item in report_dataA:
            if 'psc_rec_id__npa_date' in item:
                item['psc_rec_id__npa_date'] = item['psc_rec_id__npa_date'].replace(tzinfo=None)
        df4 = pd.DataFrame(report_dataA)
        # #print((df4.columns))
        # df4.drop(df4.columns[[11]], axis=1, inplace=True)
        df4.to_excel(excel_writer=response, engine="xlsxwriter", header=columns, index=False)  # with other applicable parameters
        return response
        
def download_excel_B(request):
    data = report_dataB
    # Create a workbook and add sheets
    wb = Workbook()
    psc_sheet = wb.active
    psc_sheet.title = 'PSC'
    sac_sheet = wb.create_sheet(title='SAC')

    # Define headers
    psc_headers = ['BO Maker', 'BO Checker', 'RO Maker', 'RO Checker', 'HO Maker', 'HO Checker', 'HO Convener']
    sac_headers = ['RO Maker', 'RO Checker', 'HO Maker', 'HO Checker', 'HO Convener']

    # Function to add data and counts to the sheet
    # Function to add data to the sheet without the count row
    def add_data(sheet, data, keys, headers):
        # Add headers
        sheet.append(headers)
        counts = []
        for key in keys:
            counts.append(len(data[key]))
        sheet.append(counts)
        # Add data rows
        max_length = max(len(data[key]) for key in keys)
        for i in range(max_length):
            row = []
            for key in keys:
                if i < len(data[key]):
                    row.append(data[key][i].get('psc_rec_id', data[key][i].get('sac_rec_id', '')))
                else:
                    row.append('')
            sheet.append(row)

    # Add PSC data
    psc_keys = ['BOM', 'BOC', 'ROM', 'ROC', 'HOM', 'HOC', 'CON']
    add_data(psc_sheet, data['psc_data'], psc_keys, psc_headers)

    # Add SAC data
    sac_keys = ['ROM', 'ROC', 'HOM', 'HOC', 'CON']
    add_data(sac_sheet, data['sac_data'], sac_keys, sac_headers)

    # Save the workbook to a response
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=report.xlsx'
    wb.save(response)
    return response
