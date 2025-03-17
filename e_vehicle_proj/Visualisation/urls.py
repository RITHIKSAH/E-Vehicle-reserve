# e_vehicle_proj/Visualisation/urls.py
from django.urls import path
from . import views  # Import the views from the current Visualisation app

urlpatterns = [
    path('earnings-chart/', views.earnings_chart, name='earnings_chart'),  # URL path for your chart view
]
