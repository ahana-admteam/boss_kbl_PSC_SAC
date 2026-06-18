
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include("boss_admin.urls"), name="boss_admin"),
    path('admin/', include('smuggler.urls')),
    # path('audit/', include('boss_audit.urls'), name='boss_audit'),
    path('notifications/', include('notifications_app.urls'), name='notification'),
    # path(r'inward/', include("inward_register.urls"), name='inward'),
    # path(r'outward/', include('outward_registers.urls'), name='outward'),
    # path(r'keys/', include('key_movement_registers.urls'), name='keys'),
    # path(r'branchdocuments/', include('branch_document_registers.urls'), name='docs'),
    # path(r'securityStockRegister/', include('security_stock_registers.urls'), name='securityStockRegister'),
    # path(r'suspensecash/', include('suspense_cash_registers.urls'), name='suspensecash'),
    # path(r'issuanceregister/', include('issuance_registers.urls'), name='issuanceregister'),
    # path(r'securityequipments/', include('security_equipment_registers.urls'), name='securityEquipmentsRegister'),
    # path(r'pettycash/', include('petty_cash_register.urls'), name='petty_cash_register'),
    # path(r'complaints/', include('complaint_registers.urls'), name='complaintsregisters'),
    # path(r'goldloan/', include('gold_loan_registers.urls'), name='gold_loan_registers'),
    # path(r'fixedasset/', include('fixed_asset_registers.urls'), name='fixed_asset_registers'),
    # path(r'it-assets/', include('it_asset_registers.urls'), name='itassetregisters'),
    # path(r'assets/', include('asset_management.urls'), name='asset_management'),
    # path(r'chequedropbox/', include('cheque_dropbox_register.urls'), name='cheque_dropbox_register'),

    # path(r'counterfeitnotes/', include('counterfeit_notes.urls'), name='counterfeitnotes'),
    # path(r'cashlimit/', include('cash_limit_registers.urls'), name='cashlimit'),
    # path(r'notesexchange/', include('coins_fresh_notes_exchange_register.urls'), name='notesexchange'),
    # path(r'aofmovement/', include('aof_movement_register.urls'), name='aofmovement'),
    # path(r'cash_register/', include('cash_register.urls'), name='cash_register'),
    # path(r'cash_reports/', include('cash_register_reports.urls'), name='cash_register_reports'),
    path(r'screeningcommittee/', include('preliminaryscreeningcommittee_review.urls'), name='screeningcommittee'),





]
