from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from datetime import date
from django.db.models import Q
from django.http import HttpResponse
from .models import Cattle
from django.views import generic
from django.shortcuts import render, redirect, get_object_or_404
from my_cattle.forms import GenderForm, CattleForm
from django.shortcuts import render, redirect
from my_cattle.forms import GenderForm
from django.db.models import Count
from constants.constants import FEMALE_BIRTH_WEIGHT, MALE_BIRTH_WEIGHT, FEMALE_MAX_WEIGHT, MALE_MAX_WEIGHT, \
    DAILY_WEIGHT_GAIN


def calculate_age_ranges():
    current_date = date.today()
    one_year_age_date = current_date - relativedelta(months=12)
    two_year_ago_date = current_date - relativedelta(months=24)

    age_ranges = {
        'total_calves': Cattle.objects.filter(
            Q(birth_date__gte=one_year_age_date) & (Q(gender='Heifer') | Q(gender='Bull'))
        ).count(),
        'total_young_heifer': Cattle.objects.filter(
            birth_date__lte=one_year_age_date,
            birth_date__gte=two_year_ago_date,
            gender='Heifer'
        ).count(),
        'total_adult_heifer': Cattle.objects.filter(
            birth_date__lte=two_year_ago_date,
            gender='Heifer'
        ).count(),
        'total_young_bull': Cattle.objects.filter(
            birth_date__lte=one_year_age_date,
            birth_date__gte=two_year_ago_date,
            gender='Bull'
        ).count(),
        'total_adult_bull': Cattle.objects.filter(
            birth_date__lte=two_year_ago_date,
            gender='Bull'
        ).count()
    }

    return age_ranges


def home(request):
    cattle_count = Cattle.objects.count()
    cow_count = Cattle.objects.filter(gender='Cow').count()

    context = {
        'total_cattle': cattle_count,
        'total_cow': cow_count,
        **calculate_age_ranges()
    }

    return render(request, 'my_farm/my_farm_main.html', context)


def cattle_info(request):
    cattle = Cattle.objects.all()

    # Get a list of all the columns in the Cattle model
    all_columns = [f.name for f in Cattle._meta.get_fields()]

    if request.method == 'POST':
        selected_columns = request.POST.getlist('columns')

        if len(selected_columns) > 0:
            # Build a dictionary of column names and their corresponding database field names
            column_dict = {'ID': 'id', 'Type': 'type', 'Number': 'number', 'Name': 'name', 'Gender': 'gender',
                           'Breed': 'breed', 'Birth Date': 'birth_date', 'acquisition_method': 'acquisition_method',
                           'Entry date': 'entry_date', 'loss_method': 'loss_method', 'End date': 'end_date',
                           'Comments': 'comments'}

            # Build a list of the selected database field names
            selected_fields = [column_dict[column] for column in selected_columns]

            # Filter the queryset to only include the selected fields
            cattle = cattle.values(*selected_fields)
        else:
            # If no columns were selected, display an error message
            error_message = 'Please select at least one column to display.'
            return render(request, 'my_farm/cattle_info.html',
                          {'cattle': cattle, 'columns': all_columns, 'error_message': error_message})

    # If the form has not been submitted, display all columns by default
    else:
        cattle = cattle.values()

    return render(request, 'my_farm/cattle_info.html', {'cattle': cattle, 'columns': all_columns})


def add_row(request):
    if request.method == 'POST':
        form = GenderForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('my_farm:cattle_info')
    else:
        form = GenderForm()
    return render(request, 'my_farm/add_row.html', {'form': form})


def update_cattle(request, cattle_id=None):
    cattle = get_object_or_404(Cattle, id=cattle_id) if cattle_id else None

    if request.method == 'POST':
        form = CattleForm(request.POST, instance=cattle)
        if form.is_valid():
            form.save()
            return redirect('my_farm:cattle_info')
    else:
        form = CattleForm(instance=cattle)

    context = {'form': form}
    return render(request, 'my_farm/update_cattle.html', context)


def delete_row(request, cattle_id):
    row = Cattle.objects.get(id=cattle_id)

    if request.method == 'POST':
        row.delete()
        return redirect('my_farm:confirmation_page')
    else:
        return render(request, 'my_farm/delete_row.html', {'row': row})


def confirmation_page(request):
    return render(request, 'my_farm/confirmation_page.html')


def search_cattle(request):
    query = request.GET.get('query')
    if query:
        cattle_list = Cattle.objects.filter(
            Q(type__icontains=query) |
            Q(number__icontains=query) |
            Q(name__icontains=query) |
            Q(gender__icontains=query) |
            Q(breed__icontains=query) |
            Q(birth_date__icontains=query) |
            Q(acquisition_method__icontains=query) |
            Q(entry_date__icontains=query) |
            Q(loss_method__icontains=query) |
            Q(end_date__icontains=query) |
            Q(comments__icontains=query)
        )
    else:
        cattle_list = Cattle.objects.all()

    context = {'cattle_list': cattle_list}
    return render(request, 'my_farm/search_cattle.html', context)


def estimate_cow_weight(request, cattle_id):
    cattle = Cattle.objects.get(id=cattle_id)
    birth_date = cattle.birth_date
    estimation_date = request.POST.get('estimation_date')
    estimation_date = date.fromisoformat(estimation_date)

    days_passed = (estimation_date - birth_date).days

    gender = cattle.gender

    if gender == 'female':
        weight = FEMALE_BIRTH_WEIGHT + (days_passed * DAILY_WEIGHT_GAIN)
        weight = min(weight, FEMALE_MAX_WEIGHT)  # Limit weight to maximum allowed for females
    elif gender == 'male':
        weight = MALE_BIRTH_WEIGHT + (days_passed * DAILY_WEIGHT_GAIN)
        weight = min(weight, MALE_MAX_WEIGHT)  # Limit weight to maximum allowed for males

    context = {
        'cattle': cattle,
        'birth_date': birth_date,
        'estimation_date': estimation_date,
        'weight': weight,
    }
    return render(request, 'my_farm/report.html', context)





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
        return redirect('my_farm:generate_report')

    # Clear the session data
    request.session['report_data'] = None

    # Perform necessary calculations for the report based on the provided dates
    start_date = report_data['start_date']
    end_date = report_data['end_date']

    start_datetime = datetime.strptime(start_date, "%Y-%m-%d")
    end_datetime = datetime.strptime(end_date, "%Y-%m-%d")

    total_calves_before_start_date = Cattle.objects.filter(
        Q(birth_date__lt=start_datetime) &
        (Q(gender='Heifer') | Q(gender='Bull'))
    ).count()

    total_calves_before_end_date = Cattle.objects.filter(
        Q(birth_date__lt=end_datetime) &
        (Q(gender='Heifer') | Q(gender='Bull'))
    ).count()


    # Generate the report data
    report_data['total_calves_first'] = total_calves_before_start_date
    report_data['total_calves_second'] = total_calves_before_end_date

    return render(request, 'my_farm/report.html', {'report_data': report_data})
