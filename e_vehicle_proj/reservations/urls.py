from django.urls import path
from . import views

urlpatterns = [
    #make_reservation
    path('make_reservation/', views.home_reservation, name='make_reservation'),
    path('make_reservation/get_vehicles_by_homelocation_id/', views.get_vehicles_by_homelocation_id, name='get_vehicles_by_homelocation_id'),
    path('inprogress/get_vehicles_by_homelocation_id/', views.get_vehicles_by_homelocation_id, name='get_vehicles_by_homelocation_id'),
    path('make_reservation/rent_vehicle/', views.rent_vehicle, name='rent_vehicle'),
    path('make_reservation/report_defective/', views.report_defective, name='report_defective'),
    
    #inprogress
    path('inprogress/', views.inprogress, name='inprogress'),
    path('inprogress/update_RentedVehicle_Location/', views.update_RentedVehicle_Location, name='update_RentedVehicle_Location'),
    path('inprogress/get_RentedVehicle_Location/', views.get_RentedVehicle_Location, name='get_RentedVehicle_Location'),
    path('inprogress/get_RentedVehicle_Capacity/', views.get_RentedVehicle_Capacity, name='get_RentedVehicle_Capacity'),
    path('inprogress/get_Home_Location/', views.get_Home_Location, name='get_Home_Location'),
    path('inprogress/returnRentedVehicle/', views.returnRentedVehicle, name='returnRentedVehicle'),
    path('inprogress/report_defective/', views.report_defective, name='report_defective'),
    path('inprogress/update_RentedVehicle_Capacity/', views.update_RentedVehicle_Capacity, name='update_RentedVehicle_Capacity'),
]