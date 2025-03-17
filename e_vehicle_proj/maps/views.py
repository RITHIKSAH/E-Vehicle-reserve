import json

from django.shortcuts import render

from all_models.models import Vehicles
from e_vehicle_proj import settings


# Create your views here.

def map_view(request):
    # Query the database for all vehicles
    vehicles = list(Vehicles.objects.exclude(location_lat__isnull=True, location_long__isnull=True).values())
    vehicles_json = json.dumps(vehicles)
    context = {
        'google_maps_api_key': settings.GOOGLE_MAPS_API_KEY,
        'vehicles': vehicles_json,
    }
    return render(request, 'map.html', context)
