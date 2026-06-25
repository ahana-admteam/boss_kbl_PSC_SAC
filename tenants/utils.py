from django.db import connection


def hostname_from_request(request):
    return request.get_host().split(":")[0].lower()


def tenant_db_from_request(request):
    hostname = hostname_from_request(request)
    tenants_map = get_tenants_map()
    # print(hostname, tenants_map)
    return tenants_map.get(hostname)


def get_tenants_map():
    return {"kotak.localhost": "kotak", "jana.localhost": "jana","fincare.localhost": "fincare", "hdfc.localhost": "default", "rbl.localhost":"rbl", "demo.localhost":"demo", "":"default", "ujjivan.localhost":"ujjivan", "svc.localhost":"svc", "localhost":"default"}