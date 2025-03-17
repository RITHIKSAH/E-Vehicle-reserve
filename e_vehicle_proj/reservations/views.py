import json

from django.shortcuts import render
from django.http import Http404
from django.views.decorators.http import require_GET
from django.urls import reverse
from django.shortcuts import redirect
from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from all_models.models import User
from all_models.models import HomeLocation
from all_models.models import Vehicles
from all_models.models import Reservations
from all_models.models import Invoices
from all_models.models import DefectiveVehicles
from e_vehicle_proj import settings
from datetime import datetime
from django.utils import timezone
from haversine import haversine, Unit
from django.db import transaction

# Create your views here.
def home_reservation(request):
    # Query the database for all vehicles
    try:
        home_locations = list(HomeLocation.objects.values())
        home_location_json = json.dumps(home_locations)
        context = {
            'google_maps_api_key': settings.GOOGLE_MAPS_API_KEY,
            'home_locations': home_location_json,
        }
        Reservations.objects.get(user=User.objects.get(id=request.user.id), attributereturned_at=False)
        return redirect('inprogress')
    except Reservations.DoesNotExist:
        try:
            Invoices.objects.get(user=User.objects.get(id=request.user.id), paid_at=None)
            return redirect('payment')
        except Invoices.DoesNotExist:
            return render(request, 'reservations/reservation.html',context)

@require_GET
def get_vehicles_by_homelocation_id(request):

    homelocation_id = request.GET.get('homelocation_id')
    if homelocation_id is None:
        return JsonResponse({'error': 'homelocation_id is required'}, status=400)
    # 查询匹配的车辆
    vehicles = list(
        Vehicles.objects
        .exclude(Q(is_defective=1) | Q(is_rented=1))
        .filter(home_location_id=homelocation_id)
        .values())
    return JsonResponse({'vehicles': vehicles})

@require_GET
def rent_vehicle(request):

    vehicle_id = request.GET.get('vehicle_id')
    homelocation_id = request.GET.get('homelocation_id')
    user_id = request.GET.get('user_id')
    try:
        Reservations.objects.get(user=User.objects.get(id=request.user.id), attributereturned_at=False)
        return HttpResponse(status=200)  # 200ok
    except Reservations.DoesNotExist:
        # table vehicle operation
        vehicleIns = Vehicles.objects.get(vehicle_id=vehicle_id)
        vehicleIns.is_rented = 1
        vehicleIns.location_lat = HomeLocation.objects.get(home_location_id=homelocation_id).location_lat
        vehicleIns.location_long = HomeLocation.objects.get(home_location_id=homelocation_id).location_long
        vehicleIns.save()

        # table reservation operation
        reservation = Reservations(
            vehicle = vehicleIns,
            picked_from = HomeLocation.objects.get(home_location_id=homelocation_id),
            user = User.objects.get(id=user_id),
            reserved_at = datetime.now(),
            returned_at = None,
            returned_to_long = None,
            returned_to_lat = None, 
            attributereturned_at = 0,
        )
        reservation.save()

        #table Invoice operation
        invoice = Invoices(
            user_id = user_id,
            amount = 0.00,
            created_at = datetime.now(),
            paid_at = None,
            reservation_id = Reservations.objects.get(user=User.objects.get(id=request.user.id), attributereturned_at=False).reservation_id
        )
        invoice.save()
        return HttpResponse(status=200)  # 404表示车辆未找到
    
def inprogress(request):
    try:
        Reservations.objects.get(user=User.objects.get(id=request.user.id), attributereturned_at=False)
        home_locations = list(HomeLocation.objects.values())
        home_location_json = json.dumps(home_locations)
        user_base_reservationIns = Reservations.objects.get(user=User.objects.get(id=request.user.id), attributereturned_at=False)
        if not user_base_reservationIns:
            raise Http404("该用户没有关联的租用车辆")
        context = {
            'google_maps_api_key': settings.GOOGLE_MAPS_API_KEY,
            'home_locations': home_location_json,
            'user_base_reservationIns': user_base_reservationIns,
        }
        return render(request, 'reservations/inprogress.html',context)
    except Reservations.DoesNotExist:
        return redirect('index')

@require_GET
def update_RentedVehicle_Location(request):

    vehicleNewPositionlat = request.GET.get('vehicleNewPositionlat')
    vehicleNewPositionlng = request.GET.get('vehicleNewPositionlng')
    try:
        # table vehicle operation
        vehicleIns = Reservations.objects.get(user=User.objects.get(id=request.user.id), attributereturned_at=False).vehicle
        vehicleIns.location_lat = float(vehicleNewPositionlat)
        vehicleIns.location_long = float(vehicleNewPositionlng)
        vehicleIns.save()
        return HttpResponse(status=200)  # 200ok
    except vehicleIns.DoesNotExist:
        return HttpResponse(status=404)  # 404表示车辆未找到
    
@require_GET
def update_RentedVehicle_Capacity(request):
    try:
        vehicleIns = Reservations.objects.get(user=User.objects.get(id=request.user.id), attributereturned_at=False).vehicle
        if vehicleIns.capacity > 0:
            vehicleIns.capacity-=1
        vehicleIns.save()
        return HttpResponse(status=200)  # 200ok
    except vehicleIns.DoesNotExist:
        return HttpResponse(status=404)  # 404表示车辆未找到
    
@require_GET
def get_RentedVehicle_Location(request):

    try:
        # table vehicle operation
        vehicleIns = Reservations.objects.get(user=User.objects.get(id=request.user.id), attributereturned_at=False).vehicle
        data = {
            'location_lat': vehicleIns.location_lat,
            'location_long': vehicleIns.location_long
        }

        return JsonResponse(data)
    except vehicleIns.DoesNotExist:
        return HttpResponse(status=404)  # 404表示车辆未找到
    
@require_GET
def get_RentedVehicle_Capacity(request):

    try:
        # table vehicle operation
        vehicleIns = Reservations.objects.get(user=User.objects.get(id=request.user.id), attributereturned_at=False).vehicle
        rentedVehicleCapacity = vehicleIns.capacity

        return JsonResponse({'rentedVehicleCapacity':rentedVehicleCapacity})
    except vehicleIns.DoesNotExist:
        return HttpResponse(status=404)  # 404表示车辆未找到
    
@require_GET
def get_Home_Location(request):
    home_id = request.GET.get('home_id')
    try:
        # table vehicle operation
        home_locationIns =  HomeLocation.objects.get(home_location_id=home_id)
        homeLocationData = {
            'home_location_lat': home_locationIns.location_lat,
            'home_location_long': home_locationIns.location_long
        }

        return JsonResponse(homeLocationData)
    except HomeLocation.DoesNotExist:
        return HttpResponse(status=404)  # 404表示车辆未找到
    
@require_GET
def returnRentedVehicle(request):
    fromwhere = request.GET.get('fromwhere')
    homeid = request.GET.get('homeid')
    try:
        # table vehicle operation
        reservationIns = Reservations.objects.get(user=User.objects.get(id=request.user.id), attributereturned_at=False)
        vehicleIns =  Reservations.objects.get(user=User.objects.get(id=request.user.id), attributereturned_at=False).vehicle
        invoiceIns = Invoices.objects.get(user=User.objects.get(id=request.user.id), paid_at=None)
        
        invoiceIns.amount = ((timezone.now() - invoiceIns.created_at).total_seconds()/3600)*vehicleIns.vehicle_type.cost_ph
        invoiceIns.end_at = datetime.now()
        invoiceIns.reservation_id = reservationIns.reservation_id
        invoiceIns.save()

        if (fromwhere == "outside"):
            vehicleIns.is_rented = 0
            vehicleIns.save()
        elif (fromwhere == "home"):
            homeobject = HomeLocation.objects.get(home_location_id=homeid)
            vehicleIns.is_rented = 0
            vehicleIns.home_location = homeobject
            vehicleIns.save()

        reservationIns.returned_at = datetime.now()
        reservationIns.returned_to_lat = vehicleIns.location_lat
        reservationIns.returned_to_long = vehicleIns.location_long
        reservationIns.attributereturned_at = True
        reservationIns.save()

        return HttpResponse(status=200)
    except Reservations.DoesNotExist:
        return HttpResponse(status=404)  # 404表示车辆未找到

@require_GET
def report_defective(request):

    vehicle_id = request.GET.get('vehicle_id')
    try:
        DefectiveVehicles.objects.get(vehicle=Vehicles.objects.get(vehicle_id=vehicle_id), repaired_at=None)
        context = {
            'notice' : "Duplication"
        }
        return JsonResponse(context)
    except DefectiveVehicles.DoesNotExist:
        defectiveVehicleIns = Vehicles.objects.get(vehicle_id=vehicle_id)
        defectiveVehicle_location = (defectiveVehicleIns.location_lat, defectiveVehicleIns.location_long)
        nearestHomeIns = None
        shortest_distance = float('inf')
        for homeIns in HomeLocation.objects.all():
            home_location = (homeIns.location_lat, homeIns.location_long)
            distance = haversine(defectiveVehicle_location, home_location, unit=Unit.KILOMETERS)
            if distance < shortest_distance:
                shortest_distance = distance
                nearestHomeIns = homeIns
        
        defectiveVehicle = DefectiveVehicles(
            vehicle = defectiveVehicleIns,
            repair_location = nearestHomeIns,
            repaired_at = None,
            reported_defective_at = datetime.now(),
        )
        defectiveVehicle.save()
        defectiveVehicleIns.is_defective = 1
        defectiveVehicleIns.save()
        context = {
            'notice' : "Success"
        }
        return JsonResponse(context)
    except Vehicles.DoesNotExist:
        context = {
            'notice' : "VehicleNotFound"
        }
        return JsonResponse(context)
    except Exception as e:
        return JsonResponse({'Error': 'An unexpected error occurred',
                             "details": str(e)
                             })
