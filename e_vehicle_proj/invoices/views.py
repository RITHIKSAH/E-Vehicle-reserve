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
from e_vehicle_proj import settings
from datetime import datetime
from decimal import Decimal

# Create your views here.
def invoices_history(request):
    login_user = request.user
    invoiceset = Invoices.objects.filter(user=request.user).order_by('-invoice_id')
    context = {
        'invoiceset': invoiceset,
        'login_user': login_user,
    }
    return render(request, 'invoices/history.html', context)



def historyDetail(request, invoice_id=None):
    try:
        if invoice_id:
            detailInvoiceIns = Invoices.objects.get(invoice_id=invoice_id)
            detailReservationIns = Reservations.objects.get(reservation_id=detailInvoiceIns.reservation_id)
            detailVehicleIns = detailReservationIns.vehicle
            if detailInvoiceIns.end_at:
                hours = round((detailInvoiceIns.end_at - detailInvoiceIns.created_at).total_seconds()/3600, 2)
                totalVehicle = round(detailVehicleIns.vehicle_type.cost_ph*hours, 2)
                tax = round(totalVehicle*0.1,2)
                Total = round(totalVehicle + tax,2)
                context={
                    'paidInvoice_ID' : detailInvoiceIns.invoice_id,
                    'paidInvoice_Amount' : detailInvoiceIns.amount,
                    'paidInvoice_Created_at' : detailInvoiceIns.created_at,
                    'paidInvoice_Paid_at' : detailInvoiceIns.paid_at,
                    'paidInvoice_End_at' : detailInvoiceIns.end_at,
                    'paidInvoice_Reservation_id' : detailInvoiceIns.reservation_id,
                    'paidVehicle_Year' : detailVehicleIns.year,
                    'paidVehicle_Model' : detailVehicleIns.model,
                    'paidVehicle_Make' : detailVehicleIns.make,
                    'paidVehicle_Type' : detailVehicleIns.vehicle_type.vehicle_type,
                    'paidVehicle_Cost' : detailVehicleIns.vehicle_type.cost_ph,
                    'hours' : hours,
                    'totalVehicle' : totalVehicle,
                    'tax' : tax,
                    'Total' : Total,
                }
                return render(request, 'invoices/history_detail.html',context)
            else:
                context={
                        'paidInvoice_ID' : detailInvoiceIns.invoice_id,
                        'paidInvoice_Amount' : detailInvoiceIns.amount,
                        'paidInvoice_Created_at' : detailInvoiceIns.created_at,
                        'paidInvoice_Paid_at' : detailInvoiceIns.paid_at,
                        'paidInvoice_End_at' : detailInvoiceIns.end_at,
                        'paidInvoice_Reservation_id' : detailInvoiceIns.reservation_id,
                        'paidVehicle_Year' : detailVehicleIns.year,
                        'paidVehicle_Model' : detailVehicleIns.model,
                        'paidVehicle_Make' : detailVehicleIns.make,
                        'paidVehicle_Type' : detailVehicleIns.vehicle_type.vehicle_type,
                        'paidVehicle_Cost' : detailVehicleIns.vehicle_type.cost_ph,
                        'hours' : "Inprogress",
                        'totalVehicle' : "Inprogress",  
                        'tax' : "Inprogress",
                        'Total' : "Inprogress",
                }
                return render(request, 'invoices/history_detail.html',context)
    except Invoices.DoesNotExist:
        return JsonResponse({'Notice': 'no target invoice'}, status=400)

def payment(request):
    try:
        unpaidInvoiceIns = Invoices.objects.get(user=User.objects.get(id=request.user.id), paid_at=None)
        inprogressVehicleIns = Reservations.objects.get(reservation_id=unpaidInvoiceIns.reservation_id).vehicle
        if unpaidInvoiceIns.end_at:
            hours = round((unpaidInvoiceIns.end_at - unpaidInvoiceIns.created_at).total_seconds()/3600,2)
            totalVehicle = round(inprogressVehicleIns.vehicle_type.cost_ph*hours if hours else None,2)
            tax = round(totalVehicle*0.1,2)
            Total = round(totalVehicle + tax,2)
            unpaidInvoiceIns.amount = Total
            unpaidInvoiceIns.save()
            context={
                'unpaidInvoice_ID' : unpaidInvoiceIns.invoice_id,
                'unpaidInvoice_Amount' : unpaidInvoiceIns.amount,
                'unpaidInvoice_Created_at' : unpaidInvoiceIns.created_at,
                'unpaidInvoice_Paid_at' : unpaidInvoiceIns.paid_at,
                'unpaidInvoice_End_at' : unpaidInvoiceIns.end_at,
                'unpaidInvoice_Reservation_id' : unpaidInvoiceIns.reservation_id,
                'inprogressVehicle_Year' : inprogressVehicleIns.year,
                'inprogressVehicle_Model' : inprogressVehicleIns.model,
                'inprogressVehicle_Make' : inprogressVehicleIns.make,
                'inprogressVehicle_Type' : inprogressVehicleIns.vehicle_type.vehicle_type,
                'inprogressVehicle_Cost' : inprogressVehicleIns.vehicle_type.cost_ph,
                'hours' : hours,
                'totalVehicle' : totalVehicle,
                'tax' : tax,
                'Total' : Total,
            }
            return render(request, 'invoices/payment_active.html',context)
        else:
            context={
                'unpaidInvoice_ID' : unpaidInvoiceIns.invoice_id,
                'unpaidInvoice_Amount' : unpaidInvoiceIns.amount,
                'unpaidInvoice_Created_at' : unpaidInvoiceIns.created_at,
                'unpaidInvoice_Paid_at' : unpaidInvoiceIns.paid_at,
                'unpaidInvoice_End_at' : unpaidInvoiceIns.end_at,
                'unpaidInvoice_Reservation_id' : unpaidInvoiceIns.reservation_id,
                'inprogressVehicle_Year' : inprogressVehicleIns.year,
                'inprogressVehicle_Model' : inprogressVehicleIns.model,
                'inprogressVehicle_Make' : inprogressVehicleIns.make,
                'inprogressVehicle_Type' : inprogressVehicleIns.vehicle_type.vehicle_type,
                'inprogressVehicle_Cost' : inprogressVehicleIns.vehicle_type.cost_ph,
                'hours' : "Inprogress",
                'totalVehicle' : "Inprogress",
                'tax' : "Inprogress",
                'Total' : "Inprogress",
            }
            return render(request, 'invoices/payment_active.html',context)
    except Invoices.DoesNotExist:
        context = {

        }
        return render(request, 'invoices/payment_inactive.html',context)
    except Reservations.DoesNotExist:
        context = {

        }
        return render(request, 'invoices/payment_inactive.html',context)

@require_GET
def payOutstandingBill(request):   
    try:
        unpaidInvoiceIns = Invoices.objects.get(user=User.objects.get(id=request.user.id), paid_at=None)
        billAmount = unpaidInvoiceIns.amount
        user_Balance = request.user.balance
        if (user_Balance >= billAmount):
            request.user.balance -= billAmount
            request.user.save()
            unpaidInvoiceIns.paid_at = datetime.now()
            unpaidInvoiceIns.save()
            context={
                'noticeText' : "PaymentSuccess"
            }
            return JsonResponse(context)
        else:
            context={
                'noticeText' : "PaymentFail"
            }
            return JsonResponse(context)
    except (ValueError, TypeError):
        # 如果 billAmount 不是有效的数字，返回错误信息
        return JsonResponse({'Notice': 'Invalid Amount!', 'Remaining Balance': request.user.balance}, status=400)
    
@require_GET
def recharge(request, invoice_id=None):
    amount = Decimal(request.GET.get('amount'))
    try:
        request.user.balance += amount
        request.user.save()
        return HttpResponse(status=200)
    except Exception as e:
        return HttpResponse(status=500 )