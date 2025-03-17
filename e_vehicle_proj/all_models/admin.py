from django.contrib import admin
from .models import HomeLocation, Vehicles, DefectiveVehicles, Invoices, Reports, Reservations, VehicleType

class HomeLocationAdmin(admin.ModelAdmin):
    pass

class VehiclesAdmin(admin.ModelAdmin):
    pass

class DefectiveVehiclesAdmin(admin.ModelAdmin):
    pass

class InvoicesAdmin(admin.ModelAdmin):
    pass

class ReportsAdmin(admin.ModelAdmin):
    pass

class ReservationsAdmin(admin.ModelAdmin):
    pass

class VehicleTypeAdimin(admin.ModelAdmin):
    pass

    
admin.site.register(HomeLocation, HomeLocationAdmin)
admin.site.register(Vehicles, VehiclesAdmin)
admin.site.register(DefectiveVehicles, DefectiveVehiclesAdmin)
admin.site.register(Invoices, InvoicesAdmin)
admin.site.register(Reports, ReportsAdmin)
admin.site.register(Reservations, ReservationsAdmin)
admin.site.register(VehicleType, VehicleTypeAdimin)