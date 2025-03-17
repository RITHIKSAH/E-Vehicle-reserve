# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.

from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()  # this is the custom user type in the proj

class HomeLocation(models.Model):
    home_location_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    capacity = models.IntegerField()
    is_repair_facility = models.BooleanField()
    location_lat = models.FloatField()
    location_long = models.FloatField()

    class Meta:
        db_table = 'Home_Location'
        verbose_name = 'Home Location'
        verbose_name_plural = 'Home Locations'
    
    def __str__(self):
        return f'{self.name} ({self.address})'

class VehicleType(models.Model):
    vehicle_type_id = models.AutoField(primary_key=True)
    vehicle_type = models.CharField(max_length=255)
    cost_ph = models.FloatField()

    class Meta:
        db_table = 'Vehicle_Type'
        verbose_name = 'Vehicle Type'
        verbose_name_plural = 'Vehicle Types'
    
    def __str__(self):
        return self.vehicle_type

class Vehicles(models.Model):
    vehicle_id = models.AutoField(primary_key=True)
    home_location = models.ForeignKey(HomeLocation, models.DO_NOTHING)
    model = models.CharField(max_length=255)
    make = models.CharField(max_length=255)
    year = models.IntegerField()
    is_defective = models.BooleanField()
    is_rented = models.BooleanField()
    location_lat = models.FloatField()
    location_long = models.FloatField()
    capacity = models.IntegerField()
    vehicle_type = models.ForeignKey(VehicleType, models.DO_NOTHING)

    class Meta:
        db_table = 'Vehicles'
        verbose_name = 'Vehicle'
        verbose_name_plural = 'Vehicles'
    
    def __str__(self):
        return f'No.{self.vehicle_id}: {self.vehicle_type} {self.model} {self.make} ({self.year})'

class DefectiveVehicles(models.Model):
    defective_vehicle_id = models.AutoField(primary_key=True)
    vehicle = models.ForeignKey(Vehicles, models.DO_NOTHING, blank=False)
    repair_location = models.ForeignKey(HomeLocation, models.DO_NOTHING, db_column='repair_location')
    repaired_at = models.DateTimeField(blank=True, null=True)
    reported_defective_at = models.DateTimeField(auto_now_add = True)

    class Meta:
        db_table = 'Defective_Vehicles'
        verbose_name = 'Defective Vehicle'
        verbose_name_plural = 'Defective Vehicles'

class Invoices(models.Model):
    invoice_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, models.DO_NOTHING)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(blank=True, null=True)
    paid_at = models.DateTimeField()
    end_at = models.DateTimeField()
    reservation_id = models.IntegerField()


    class Meta:
        db_table = 'Invoices'
        verbose_name = 'Invoice'
        verbose_name_plural = 'Invoices'

class Reports(models.Model):
    report_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, models.DO_NOTHING)
    vehicle = models.ForeignKey(Vehicles, models.DO_NOTHING)
    created_at = models.DateTimeField()
    report = models.TextField()

    class Meta:
        db_table = 'Reports'
        verbose_name = 'Report'
        verbose_name_plural = 'Reports'

class Reservations(models.Model):
    reservation_id = models.IntegerField(primary_key=True)
    vehicle = models.ForeignKey(Vehicles, models.DO_NOTHING)
    picked_from = models.ForeignKey(HomeLocation, models.DO_NOTHING, db_column='picked_from')
    # returned_to = models.ForeignKey(HomeLocation, models.DO_NOTHING, db_column='returned_to', related_name='reservations_returned_to_set')
    user = models.ForeignKey(User, models.DO_NOTHING)
    reserved_at = models.DateTimeField()
    returned_at = models.DateTimeField()
    returned_to_long = models.FloatField()
    returned_to_lat = models.FloatField()
    attributereturned_at = models.BooleanField()

    class Meta:
        db_table = 'Reservations'
        verbose_name = 'Reservation'
        verbose_name_plural = 'Reservations'

