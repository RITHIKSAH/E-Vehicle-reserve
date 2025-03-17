from django.urls import path
from . import views

urlpatterns = [
    path('payment/', views.payment, name='payment'),
    path('payment/payOutstandingBill/', views.payOutstandingBill, name='payOutstandingBill'),
    path('history/', views.invoices_history, name='history'),
    path('historyDetail/<int:invoice_id>/', views.historyDetail, name='historyDetail'),
    path('history/recharge/', views.recharge, name='recharge'),
    path('payment/recharge/', views.recharge, name='recharge'),
    path('historyDetail/<int:invoice_id>/recharge/', views.recharge, name='recharge'),
]