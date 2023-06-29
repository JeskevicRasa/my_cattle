from datetime import date
from dateutil.relativedelta import relativedelta
from django.db.models import Q
from django.views import View
from django.shortcuts import redirect, render

from .constants import FEMALE_BIRTH_WEIGHT, DAILY_WEIGHT_GAIN, FEMALE_MAX_WEIGHT, MALE_BIRTH_WEIGHT, MALE_MAX_WEIGHT
from .models import Cattle


class LivestockMovementReportView(View):
    template_name = 'my_farm/livestock_movement_report.html'

    def __init__(self):
        self.current_date = date.today()
        self.start_date = None
        self.end_date = None
        self.start_date_ranges = None
        self.end_date_ranges = None
        self.current_date_ranges = None

    def get_period(self, request):
        return render(request, 'my_farm/generate_report.html')

    def post_period(self, request):
        self.start_date = date.fromisoformat(request.POST.get('start_date'))
        self.end_date = date.fromisoformat(request.POST.get('end_date'))

        # Store the data in session
        request.session['report_data'] = {
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat(),
        }

        return redirect('my_farm:report')

    def calculate_cattle_age(self, birth_date, estimation_date):
        age = relativedelta(estimation_date, birth_date)
        age_in_months = age.years * 12 + age.months
        return age_in_months

    def calculate_cattle(self, estimation_date):
        cattle = Cattle.objects.all()
        total_cattle = cattle.count()

        age_list = []
        for c in cattle:
            age_in_months = self.calculate_cattle_age(c.birth_date, estimation_date)
            cattle_dict = {
                'gender': c.gender,
                'age_in_months': age_in_months,
            }
            age_list.append(cattle_dict)

        total_cows = sum(1 for c in cattle if c.gender == 'Cow')
        total_calves = sum(
            1 for item in age_list if item['gender'] in ['Heifer', 'Bull'] and item['age_in_months'] < 12)
        total_young_heifer = sum(
            1 for item in age_list if item['gender'] == 'Heifer' and 12 <= item['age_in_months'] < 24)
        total_adult_heifer = sum(1 for item in age_list if item['gender'] == 'Heifer' and item['age_in_months'] >= 24)
        total_young_bull = sum(1 for item in age_list if item['gender'] == 'Bull' and 12 <= item['age_in_months'] < 24)
        total_adult_bull = sum(1 for item in age_list if item['gender'] == 'Bull' and item['age_in_months'] >= 24)

        return {
            'total_cattle': total_cattle,
            'total_cows': total_cows,
            'total_calves': total_calves,
            'total_young_heifer': total_young_heifer,
            'total_adult_heifer': total_adult_heifer,
            'total_young_bull': total_young_bull,
            'total_adult_bull': total_adult_bull,
        }

    def calculate_cattle_by_date(self, request):
        report_data = request.session.get('report_data')

        if not report_data:
            return redirect('my_farm:generate_report')

        start_date = report_data['start_date']
        end_date = report_data['end_date']

        cattle_count_report = {
            'reporting_start_date': self.calculate_cattle(start_date),
            'reporting_end_date': self.calculate_cattle(end_date),
        }

        return render(request, self.template_name, cattle_count_report)

    def estimate_cow_weight(self, request, cattle_id, estimation_date):
        cattle = Cattle.objects.get(id=cattle_id)
        birth_date = cattle.birth_date

        days_passed = (estimation_date - birth_date).days

        gender = cattle.gender

        if gender in ['Heifer', 'Cow']:
            weight = FEMALE_BIRTH_WEIGHT + (days_passed * DAILY_WEIGHT_GAIN)
            weight = min(weight, FEMALE_MAX_WEIGHT)
        elif gender == 'Bull':
            weight = MALE_BIRTH_WEIGHT + (days_passed * DAILY_WEIGHT_GAIN)
            weight = min(weight, MALE_MAX_WEIGHT)
        else:
            raise ValueError("Invalid gender. Must be 'Heifer', 'Cow', or 'Bull'.")

        context = {
            'cattle': cattle,
            'birth_date': birth_date,
            'estimation_date': estimation_date,
            'weight': weight,
        }
        return render(request, self.template_name, context)

    def estimate_total_weight_by_ranges(self, request, estimation_date):
        total_weight = 0
        age_ranges = self.calculate_cattle(estimation_date)
        for age_category, count in age_ranges.items():
            if count > 0:
                cattle_queryset = Cattle.objects.filter(gender=age_category)
                for cattle in cattle_queryset:
                    total_weight += self.estimate_cow_weight(request, cattle.id, estimation_date)

        return total_weight

    def get_weight_ranges_by_date(self, request):
        report_data = request.session.get('report_data')

        if not report_data:
            return redirect('my_farm:generate_report')

        self.start_date = date.fromisoformat(report_data['start_date'])
        self.end_date = date.fromisoformat(report_data['end_date'])

        start_weight_ranges = self.estimate_total_weight_by_ranges(request, self.start_date)
        end_weight_ranges = self.estimate_total_weight_by_ranges(request, self.end_date)
        current_weight_ranges = self.estimate_total_weight_by_ranges(request, self.current_date)

        context = {
            'start_weight_ranges': start_weight_ranges,
            'end_weight_ranges': end_weight_ranges,
            'current_weight_ranges': current_weight_ranges,
        }

        return render(request, self.template_name, context)
