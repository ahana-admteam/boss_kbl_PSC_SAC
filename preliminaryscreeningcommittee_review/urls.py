from django.urls import path
from .views import psc_views,sac_views,account_views, pdf_exports
from boss_v1 import settings
from django.conf.urls.static import static

urlpatterns = [
    path('dashboard/', psc_views.dashboard, name='dashboard'),
    path('fetch_employee_data/', psc_views.fetch_employee_data, name='fetch_employee_data'),
    path('get_mom_data/', psc_views.get_mom_data, name='get_mom_data'),
    path('get_psc_data/', psc_views.get_psc_data, name='get_psc_data'),
    path('get_sac_data/', psc_views.get_sac_data, name='get_sac_data'),
    # PSC
    path('psc_review/', psc_views.psc_review, name='psc_review'),
    path('psc_review/<int:pk>', psc_views.psc_review, name='psc_review'),
    path('psc_update/', psc_views.psc_update, name='psc_update'),
    path('psc_update/<int:pk>', psc_views.psc_update, name='psc_update'),
    path('psc_update/<int:pk>/<str:val>', psc_views.psc_update, name='psc_update'),

    # SAC 
    path('sac_review/', sac_views.sac_review, name='sac_review'),
    path('sac_review/<int:pk>', sac_views.sac_review, name='sac_review'),
    path('sac_update/', sac_views.sac_update, name='sac_update'),
    path('sac_update/<int:pk>', sac_views.sac_update, name='sac_update'),
    path('sac_update/<int:pk>/<str:val>', sac_views.sac_update, name='sac_update'),

    # MOM
    path('mom_dashboard/', psc_views.mom_dashboard, name='mom_dashboard'),
    path('mom_generate/', psc_views.mom_generate, name='mom_generate'),
    path('mom_generate/<str:review>', psc_views.mom_generate, name='mom_generate'),
    path('mom_edit/', psc_views.mom_edit, name='mom_edit'),
    path('mom_edit/<int:pk>', psc_views.mom_edit, name='mom_edit'),
    # path('mom_generate/<str:review>/<int:pk>', psc_views.mom_generate, name='psc_mom_generate'),
    path('mom_lapses/', psc_views.mom_lapses, name='mom_lapses'),
    path('mom_lapses/<str:review>', psc_views.mom_lapses, name='mom_lapses'),
    path('mom_lapses/<str:review>/<int:pk>', psc_views.mom_lapses, name='mom_lapses'),
    path('mom_review/', psc_views.mom_review, name='mom_review'),
    path('mom_review/<int:id>', psc_views.mom_review, name='mom_review'),
    path('mom_review/<int:mom_id>/<str:review>', psc_views.mom_review, name='mom_review'),
    path('mom_review/<int:mom_id>/<str:review>/<int:pk>', psc_views.mom_review, name='mom_review'),
    # path('mom_date_fetch/', psc_views.mom_date_fetch, name='mom_date_fetch'),
    # path('mom_date_fetch/<int:id>', psc_views.mom_date_fetch, name='mom_date_fetch'),
    path('sac_review_export/<int:pk>', pdf_exports.sac_review_export, name='sac_review_export'),
    path('psc_review_export/<int:pk>', pdf_exports.psc_review_export, name='psc_review_export'),
    path('sac_review_export/<int:pk>/<str:merge_condition>', pdf_exports.sac_review_export, name='sac_review_export'),
    path('psc_review_export/<int:pk>/<str:merge_condition>', pdf_exports.psc_review_export, name='psc_review_export'),
    path('mom_lapse_export/<int:pk>', pdf_exports.mom_lapse_export, name='mom_lapse_export'),
    path('mom_lapse_export/<int:pk>/<str:preps>', pdf_exports.mom_lapse_export, name='mom_lapse_export'),
    path('mom_review_export/<int:pk>/<int:m_id>', pdf_exports.mom_review_export, name='mom_review_export'),
    path('mom_close/', psc_views.mom_close, name='mom_close'),
    path('account_dashboard', account_views.account_dashboard, name='account_dashboard')
]


if settings.DEBUG:
    urlpatterns += static(settings.base.MEDIA_URL,
                          document_root=settings.base.MEDIA_ROOT)



