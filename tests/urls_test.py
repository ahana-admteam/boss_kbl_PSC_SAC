"""Minimal URLconf for tests."""
from django.urls import path
from django.http import HttpResponse


def stub(request, *args, **kwargs):
    return HttpResponse("ok")


urlpatterns = [
    path("login/", stub, name="login_page"),
    path("logout/", stub, name="log_out"),
    path("home/", stub, name="home_page"),
    path("notifications/", stub, name="notifications"),
    path(
        "notifications/<int:notification>/<int:extra_id>",
        stub,
        name="view_notification",
    ),
    path("dashboard/", stub, name="dashboard"),
    path("sac_review/", stub, name="sac_review"),
    path("sac_update/", stub, name="sac_update"),
    path("psc_review/", stub, name="psc_review"),
    path("psc_update/", stub, name="psc_update"),
    path("mom_dashboard/", stub, name="mom_dashboard"),
    path("mom_generate/", stub, name="mom_generate"),
    path("mom_edit/", stub, name="mom_edit"),
    path("mom_lapses/", stub, name="mom_lapses"),
    path("mom_review/", stub, name="mom_review"),
    path("mom_close/", stub, name="mom_close"),
    path("account_dashboard/", stub, name="account_dashboard"),
    path("role_assign/", stub, name="role_assign_page"),
    path("app_admin/", stub, name="app_admin"),
    path("add_branch/", stub, name="add_branch"),
    path("add_employee/", stub, name="add_employee"),
]
