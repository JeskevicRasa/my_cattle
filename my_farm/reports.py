from datetime import datetime

from django.db.models import Q
from django.shortcuts import redirect, render

from my_farm.models import Cattle


def generate_report(request):
    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')

        # Store the data in session
        request.session['report_data'] = {
            'start_date': start_date,
            'end_date': end_date,
        }

        return redirect('my_farm:report')

    return render(request, 'my_farm/generate_report.html')


def report(request):
    # Retrieve the data from session
    report_data = request.session.get('report_data')
    if not report_data:
        return redirect('generate_report')

    # Clear the session data
    request.session['report_data'] = None

    # Perform necessary calculations for the report based on the provided dates
    start_date = report_data['start_date']
    end_date = report_data['end_date']

    start_datetime = datetime.strptime(start_date, "%Y-%m-%d")
    end_datetime = datetime.strptime(end_date, "%Y-%m-%d")

    total_calves = Cattle.objects.filter(
        Q(birth_date__gte=start_datetime) &
        Q(birth_date__lte=end_datetime) &
        (Q(gender='Heifer') | Q(gender='Bull'))
    ).count()

    # Generate the report data
    report_data['total_calves'] = total_calves

    return render(request, 'my_farm/report.html', {'report_data': report_data})

