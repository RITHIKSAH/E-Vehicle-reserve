from django.urls import path
from .views import DefectiveVehiclesCreateView, DefectiveVehiclesDoneView, AllVehicleTrackingView, VehicleRechargeView, RechargeDoneView, VehicleRepairView, RepairDoneView, VehicleMoveView, MoveDoneView
urlpatterns = [
    path('report_defective/', DefectiveVehiclesCreateView.as_view(), name='report_defective'),
    path('report_defective_done/', DefectiveVehiclesDoneView.as_view(), name='report_defective_done'),
    path('tracking/', AllVehicleTrackingView.as_view(), name='tracking'),
    path('recharge/', VehicleRechargeView.as_view(), name='recharge'),
    path('recharge_done/', RechargeDoneView.as_view(), name='recharge_done'), 
    path('repair/', VehicleRepairView.as_view(), name='repair'),
    path('repair_done/', RepairDoneView.as_view(), name='repair_done'), 
    path('move/', VehicleMoveView.as_view(), name='move'),
    path('move_done/', MoveDoneView.as_view(), name='move_done'), 
]