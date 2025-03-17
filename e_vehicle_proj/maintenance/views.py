from django.shortcuts import redirect
from django.views import View
from django.utils import timezone
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, TemplateView, ListView
from django.contrib import messages
import haversine
from all_models.models import Vehicles, DefectiveVehicles, HomeLocation
import e_vehicle_proj.secrets as secrets
import accounts.views as account_views

class DefectiveVehiclesCreateView(CreateView):
    template_name = 'maintenance/report_defective.html'
    success_url = reverse_lazy('report_defective_done')
    model = DefectiveVehicles
    fields = ['vehicle']

    def form_valid(self, form):
        # get the defective_vehicle without save
        defective = form.save(commit=False)
        if defective.vehicle.is_rented:
            messages.add_message(self.request, messages.INFO, 'Vehicle can not be marked as defective because it is in use.')
            return super().form_invalid(form)
        elif defective.vehicle.is_defective:
            messages.add_message(self.request, messages.INFO, 'This vehicle has already been marked as defective.')
            return super().form_invalid(form)
        vehicle_location = (defective.vehicle.location_lat, defective.vehicle.location_long)
        repair_locations = list(HomeLocation.objects.filter(is_repair_facility = True))
        nearest_location = min(repair_locations, key=lambda x:haversine.haversine(vehicle_location, (x.location_lat, x.location_long)))
        defective.repair_location = HomeLocation.objects.get(pk=nearest_location.home_location_id)
        defective.vehicle.is_defective = True
        defective.vehicle.save()
        defective.save()
        return super().form_valid(form)
    
class DefectiveVehiclesDoneView(TemplateView):
    template_name = 'maintenance/report_defective_done.html'

class AllVehicleTrackingView(account_views.OperatorViewMixin, ListView):
    template_name = 'maintenance/tracking.html'
    model = Vehicles
    context_object_name = 'vehicles'
    queryset = Vehicles.objects.filter(location_lat__isnull=False)
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        js_vehicles = list(Vehicles.objects.filter(location_lat__isnull=False).values())
        for vehicle in js_vehicles:
            vehicle['is_defective'] = int(vehicle['is_defective'])
            vehicle['is_rented'] = int(vehicle['is_rented'])   
        context['jsvehicles'] = js_vehicles
        context['google_maps_api_key'] = secrets.google_maps_api_key
        return context

class VehicleRepairView(account_views.OperatorViewMixin, ListView):
    template_name = 'maintenance/repair.html'
    model = DefectiveVehicles
    context_object_name = 'repairs'
    # search for defective reports not yet dealt with
    queryset = DefectiveVehicles.objects.select_related('vehicle').filter(repaired_at__isnull = True)
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        defective_vehicles = DefectiveVehicles.objects.select_related('vehicle', 'repair_location').filter(repaired_at__isnull = True)
        js_defective_dicts = [
            {
                'id': defective.pk,
                'vehicle_id': defective.vehicle.pk,
                'home_id': defective.repair_location.pk,
                'vehicle_details': {'model': defective.vehicle.model, 'make': defective.vehicle.make, 'year': defective.vehicle.year, 'capacity': defective.vehicle.capacity},
                'home_details': {'name': defective.repair_location.name, 'address': defective.repair_location.address},
                'vehicle_location': {'lat': defective.vehicle.location_lat, 'long': defective.vehicle.location_long},
                'repair_location': {'lat': defective.repair_location.location_lat, 'long': defective.repair_location.location_long},
            }
            for defective in defective_vehicles
        ] 
        context['js_defective_vehicles'] = js_defective_dicts
        context['google_maps_api_key'] = secrets.google_maps_api_key
        return context

class RepairDoneView(View):
    def post(self, request):
        # The id of DefectiveVehicle
        repair_id = request.POST['repair_id']
        # get the DefectiveVehicles object from database by vehicle_id
        repair = DefectiveVehicles.objects.get(pk=repair_id)
        # set the repair time to now
        repair.repaired_at = timezone.now()
        # set location of vehicle to location of repair place
        repair.vehicle.location_lat = repair.repair_location.location_lat
        repair.vehicle.location_long = repair.repair_location.location_long
        # set home of vehicle to the repair place
        repair.vehicle.home_location = repair.repair_location
        # mark vehicle as not defective
        repair.vehicle.is_defective = False
        # save changes to database
        repair.vehicle.save()
        repair.save()
        return redirect(reverse('repair'))

class VehicleRechargeView(account_views.OperatorViewMixin, ListView):
    template_name = 'maintenance/recharge.html'
    model = Vehicles
    context_object_name = 'vehicles'
    queryset = Vehicles.objects.filter(capacity__lte=10, is_rented=False)
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        js_vehicles = list(Vehicles.objects.filter(location_lat__isnull=False, capacity__lte=10, is_rented=False).values())
        for vehicle in js_vehicles:
            vehicle['is_defective'] = int(vehicle['is_defective'])
            vehicle['is_rented'] = int(vehicle['is_rented'])   
        context['jsvehicles'] = js_vehicles
        context['google_maps_api_key'] = secrets.google_maps_api_key
        return context

class RechargeDoneView(View):
    def post(self, request):
        vehicle_id = request.POST['vehicle_id']
        # get the vehicle object from database by vehicle_id
        vehicle = Vehicles.objects.get(pk=vehicle_id)
        # set power of the vehicle back to 100%
        vehicle.capacity = 100
        # commit the change
        vehicle.save()
        return redirect(reverse('recharge'))
    
class VehicleMoveView(account_views.OperatorViewMixin, ListView):
    template_name = 'maintenance/move.html'
    model = Vehicles
    context_object_name = 'vehicles'
    # queryset = Vehicles.objects.filter(is_rented=False)
    paginate_by = 10

    def get_queryset(self):
        queryset = Vehicles.objects.select_related('home_location').filter(location_lat__isnull=False, is_rented=False)
        queryset = [vehicle for vehicle in queryset if haversine.haversine((vehicle.location_lat, vehicle.location_long), (vehicle.home_location.location_lat, vehicle.home_location.location_long), unit='m') >10]
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        vehicles = Vehicles.objects.filter(location_lat__isnull=False, is_rented=False)
        vehicles = [vehicle for vehicle in vehicles if haversine.haversine((vehicle.location_lat, vehicle.location_long), (vehicle.home_location.location_lat, vehicle.home_location.location_long), unit='m') >10]
        homes = HomeLocation.objects.all()
        move_to_list = []
        for vehicle in vehicles:
            move_to = min(homes, key=lambda x:haversine.haversine((vehicle.location_lat, vehicle.location_long), (x.location_lat, x.location_long)))
            move_to_list.append(move_to)
        js_vehicles = [
            {
                'vehicle_id': vehicles[i].pk,
                'home_id': move_to_list[i].pk,
                'vehicle_details': {'model': vehicles[i].model, 'make': vehicles[i].make, 'year': vehicles[i].year, 'capacity': vehicles[i].capacity},
                'home_details': {'name': move_to_list[i].name, 'address': move_to_list[i].address},
                'vehicle_location': {'lat': vehicles[i].location_lat, 'long': vehicles[i].location_long},
                'home_location': {'lat': move_to_list[i].location_lat, 'long': move_to_list[i].location_long},
            }
            for i in range(len(vehicles))
        ] 
        context['jsvehicles'] = js_vehicles
        context['google_maps_api_key'] = secrets.google_maps_api_key
        return context    

class MoveDoneView(View):
    def post(self, request):
        vehicle_id = request.POST['vehicle_id']
        # get the vehicle and the nearest home
        vehicle = Vehicles.objects.get(pk=vehicle_id)
        homes = HomeLocation.objects.all()
        home = min(homes, key=lambda x:haversine.haversine((vehicle.location_lat, vehicle.location_long), (x.location_lat, x.location_long)))
        # move vehicle to nearest home
        vehicle.location_lat = home.location_lat
        vehicle.location_long = home.location_long
        vehicle.home_location = home
        # commit the change
        vehicle.save()
        return redirect(reverse('move'))