import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64
from django.shortcuts import render
from all_models.models import Invoices, Reservations, Vehicles, DefectiveVehicles
from django.db.models import Sum, Count, F, Avg
from django.db.models.functions import TruncDate, TruncMonth
from matplotlib.patches import Patch
import matplotlib.patches as mpatches
# import seaborn as sns
import pandas as pd
import plotly.graph_objects as go
from django.contrib.auth.decorators import user_passes_test
import accounts.views as account_views
@user_passes_test(account_views.manager_group_check)
def earnings_chart(request):
    #1. Line chart - Amount Earned per Day
    daily_data = (
        Invoices.objects
        .annotate(payment_date=TruncDate('paid_at'))
        .values('payment_date')
        .annotate(total_amount=Sum('amount'))
        .order_by('payment_date')
    )
#  if item['payment_date'] else 'Not Paid'
    ride_date = [item['payment_date'].strftime('%d-%m-%Y') if item['payment_date'] else 'Amount Due' for item in daily_data]
    total_amount = [item['total_amount'] for item in daily_data]

    plt.figure(figsize=(10, 6))
    plt.plot(ride_date, total_amount, marker='o', linestyle='-', color='b')
    #plt.title("Amount Earned per Day")
    plt.xlabel("Date (DD-MM-YYYY)", fontsize=10, fontweight='bold')
    plt.ylabel("Amount Earned", fontsize=10, fontweight='bold')
    plt.xticks(rotation=45)
    plt.tight_layout()
    for i, amount in enumerate(total_amount):
        plt.text(ride_date[i], total_amount[i], f"{amount}", ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    image_line = io.BytesIO()
    plt.savefig(image_line, format='png')
    image_line.seek(0)
    line_amount_earned = base64.b64encode(image_line.getvalue()).decode('utf-8')
    image_line.close()
    plt.close()

    # 2. Bar graph - total bookings
    total_bookings = (
        Reservations.objects
        .annotate(reservation_date=TruncDate('reserved_at'))
        .values('reservation_date')
        .annotate(total_count=Count('reservation_id'))
        .order_by('reservation_date')
    )
    
    booking_date = [item['reservation_date'].strftime('%d-%m-%Y') if item['reservation_date'] else 'Not Paid' for item in total_bookings]
    booking_count = [item['total_count'] for item in total_bookings]

    plt.figure(figsize=(10, 6))
    plt.bar(booking_date, booking_count, color='g')
    #plt.title("Total Bookings Each day")
    plt.xlabel("Date (DD-MM-YYYY)", fontsize=10, fontweight='bold')
    plt.ylabel("No. of Bookings", fontsize=10, fontweight='bold')
    plt.xticks(rotation=45)
    plt.tight_layout()
    for i, count in enumerate(booking_count):
        plt.text(i, booking_count[i] + 0.1, f"{count}", ha='center', va='bottom', fontsize=10, fontweight='bold')  # Annotate values


    image_bar = io.BytesIO()
    plt.savefig(image_bar, format='png')
    image_bar.seek(0)
    bar_booking_count = base64.b64encode(image_bar.getvalue()).decode('utf-8')
    image_bar.close()
    plt.close()

    # 3. Pie Chart: Vehicle Bookings by Model
    vehicle_data = (
        Reservations.objects
        .select_related('vehicle')  # Join with the Vehicles table
        .values('vehicle__model')
        .annotate(bookings_count=Count('reservation_id'))
    )
    
    labels = [item['vehicle__model'] for item in vehicle_data]
    sizes = [item['bookings_count'] for item in vehicle_data]

    plt.figure(figsize=(8, 8))
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
    #plt.title("Vehicle Bookings by Model")
    plt.tight_layout()
    
    image_pie = io.BytesIO()
    plt.savefig(image_pie, format='png')
    image_pie.seek(0)
    pie_model = base64.b64encode(image_pie.getvalue()).decode('utf-8')
    image_pie.close()

    # 4. Horizontal Bar Chart: Battery Percentage by Vehicle Model and Home Location
    data = (
        Vehicles.objects
        .select_related('home_location')
        .filter(capacity__lte=80)  # Filter for battery <= 80%
        .values('model', 'home_location__name', 'capacity')
    )
    df = pd.DataFrame(data)
    df['label'] = df['model'] + " (" + df['home_location__name'] + ")"

    def color_code(capacity):
        if capacity < 20:
            return 'red'
        elif 20 <= capacity <= 50:
            return 'orange'
        else:
            return 'green'

    df['color'] = df['capacity'].apply(color_code)
    df = df.sort_values(by='capacity', ascending=True)

    plt.figure(figsize=(14, 12))
    bars = plt.barh(df['label'], df['capacity'], color=df['color'])

    for bar in bars:
        plt.text(
            bar.get_width() + 1, bar.get_y() + bar.get_height() / 2,
            f'{bar.get_width()}%', va='center', ha='left', fontsize=9, fontweight='bold'
        )

    plt.xlabel("Battery Percentage", fontsize=14, fontweight='bold')
    plt.ylabel("Vehicle Model (Home Location)", fontsize=14, fontweight='bold')
    #plt.title("Battery Percentage by Vehicle Model and Home Location", fontsize=24, fontweight='bold')
    plt.gca().invert_yaxis()

    red_patch = mpatches.Patch(color='red', label='Below 20%')
    orange_patch = mpatches.Patch(color='orange', label='20-50%')
    green_patch = mpatches.Patch(color='green', label='50-80%')
    plt.legend(handles=[red_patch, orange_patch, green_patch], loc='upper right', title="Battery Levels")
    plt.tight_layout()

    Image_buffer = io.BytesIO()
    plt.savefig(Image_buffer, format='png')
    Image_buffer.seek(0)
    horizontal_battery_bar = base64.b64encode(Image_buffer.getvalue()).decode('utf-8')
    Image_buffer.close()
    
    # 5. Speedometer graph for defective or not
    not_repaired_count = DefectiveVehicles.objects.filter(repaired_at__isnull=True).count()
    repaired_count = DefectiveVehicles.objects.filter(repaired_at__isnull=False).count()

    total_vehicles = not_repaired_count + repaired_count
    fig = go.Figure(go.Indicator(
    mode="gauge+number",
    value=not_repaired_count,
    title={'text': "No. of Defective Vehicles", 'font': {'size': 24}},
    gauge={
        'axis': {'range': [0, total_vehicles], 'tickwidth': 1, 'tickcolor': "darkblue"},
        'bar': {'color': "rgba(0,0,0,0)"},
        'steps': [
            {'range': [0, not_repaired_count], 'color': "red"},
            {'range': [not_repaired_count, total_vehicles], 'color': "green"},
        ],
    }
    ))

    fig.update_layout(
    font={'color': "darkblue", 'family': "Arial"},
    )
    speedometer_buffer = io.BytesIO()
    fig.write_image(speedometer_buffer, format="png")
    speedometer_buffer.seek(0)
    image_speedometer = base64.b64encode(speedometer_buffer.getvalue()).decode('utf-8')
    speedometer_buffer.close()

    #6: Tabular form stucture
    defective_vehicle_data = (
        Vehicles.objects
        .select_related('home_location')
        .filter(is_defective=True)
        .values('model', 'make', 'year', 'capacity', 'home_location__name')
    )

    df_defective_vehicles = pd.DataFrame(defective_vehicle_data)
    df_defective_vehicles.rename(
        columns={
            'model': 'Model',
            'make': 'Make',
            'year': 'Year of Manufacture',
            'capacity': 'Battery Percent',
            'home_location__name': 'Home Location'
        },
        inplace=True
    )
    defective_vehicles_table = df_defective_vehicles.to_html(
        index=False,
        classes="table table-striped table-bordered",
        border=0
    )

    #7. Pie Chart: Bookings by Vehicle Type (E-car, E-bike, E-scooter)
    vehicle_type_data = (
        Reservations.objects
        .select_related('vehicle__vehicle_type')
        .values('vehicle__vehicle_type__vehicle_type')
        .annotate(total_booking=Count('reservation_id'))
    )
    vehicle_labels = [item['vehicle__vehicle_type__vehicle_type'] for item in vehicle_type_data]
    vehicle_counts = [item['total_booking'] for item in vehicle_type_data]

    plt.figure(figsize=(8, 8))
    plt.pie(vehicle_counts, labels=vehicle_labels, autopct='%1.1f%%', startangle=140)
    #s=plt.title("Bookings by Vehicle Type")
    plt.tight_layout()
    
    buffer_pie_vehicle_type = io.BytesIO()
    plt.savefig(buffer_pie_vehicle_type, format='png')
    buffer_pie_vehicle_type.seek(0)
    pie_vehicle_type = base64.b64encode(buffer_pie_vehicle_type.getvalue()).decode('utf-8')
    buffer_pie_vehicle_type.close()
    plt.close()

    context = {
        'chart_line': line_amount_earned,
        'chart_bar': bar_booking_count,
        'chart_pie': pie_model,
        'chart_bar_battery': horizontal_battery_bar,
        'chart_speedometer': image_speedometer,
        'defective_vehicles_table': defective_vehicles_table,
        'chart_pie_vehicle_type': pie_vehicle_type,
    }
    return render(request, 'Visualisation/template.html', context)
