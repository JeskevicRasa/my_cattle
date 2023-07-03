from dateutil.relativedelta import relativedelta
from datetime import date
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from my_cattle.forms import GenderForm, CattleForm
from .models import Cattle
from .constants import FEMALE_BIRTH_WEIGHT, MALE_BIRTH_WEIGHT, FEMALE_MAX_WEIGHT, MALE_MAX_WEIGHT, DAILY_WEIGHT_GAIN

from django.views import View
from django.urls import reverse
from .groups import GroupsManagement, GroupNumbers


def calculate_cattle_age(birth_date, estimation_date):
    if estimation_date < birth_date:
        return -1
    else:
        age = relativedelta(estimation_date, birth_date)
        age_in_months = age.years * 12 + age.months
        return age_in_months


def calculate_cattle(estimation_date):

    cattle = Cattle.objects.all()
    total_cattle = cattle.count()
    age_list = []
    for c in cattle:
        age_in_months = calculate_cattle_age(c.birth_date, estimation_date)
        cattle_dict = {
            'gender': c.gender,
            'age_in_months': age_in_months,
        }
        age_list.append(cattle_dict)
    total_cows = sum(1 for c in cattle if c.gender == 'Cow')
    total_calves = sum(1 for item in age_list if item['gender'] in ['Heifer', 'Bull'] and item['age_in_months'] < 12)
    total_young_heifer = sum(1 for item in age_list if item['gender'] == 'Heifer' and 12 <= item['age_in_months'] < 24)
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


def home(request):
    context = {**calculate_cattle(estimation_date=date.today())}
    return render(request, 'my_farm/my_farm_main.html', context)


def cattle_info(request):
    cattle = Cattle.objects.filter(hidden=False)

    # Get a list of all the columns in the Cattle model
    all_columns = ['ID', 'Type', 'Number', 'Name', 'Gender', 'Breed', 'Birth Date',
                   'Acquisition Method', 'Entry Date', 'Loss Method', 'End Date', 'Comments']

    if request.method == 'POST':
        selected_columns = request.POST.getlist('columns')

        if len(selected_columns) > 0:
            # Build a dictionary of column names and their corresponding database field names
            column_dict = {
                'ID': 'id',
                'Type': 'type',
                'Number': 'number',
                'Name': 'name',
                'Gender': 'gender',
                'Breed': 'breed',
                'Birth Date': 'birth_date',
                'Acquisition Method': 'acquisition_method',
                'Entry Date': 'entry_date',
                'Loss Method': 'loss_method',
                'End Date': 'end_date',
                'Comments': 'comments'
            }

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


# def delete_row(request, cattle_id):
#     row = Cattle.objects.get(id=cattle_id)
#
#     if request.method == 'POST':
#         row.delete()
#         return redirect('my_farm:confirmation_page')
#     else:
#         return render(request, 'my_farm/cattle_confirm_delete.html', {'row': row})


class CattleDeleteView(View):
    def get(self, request, cow_id):
        cow = get_object_or_404(Cattle, id=cow_id)

        # Set the hidden field to True
        cow.hidden = True
        cow.save()

        # Store the hidden cow ID in session or any other storage mechanism
        hidden_cows = request.session.get('hidden_cows', [])
        hidden_cows.append(cow_id)
        request.session['hidden_cows'] = hidden_cows

        return redirect('my_farm:cattle_info')


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



    # def calculate_cattle(self, estimation_date):
    #     cattle = Cattle.objects.all()
    #     total_cattle = cattle.count()
    #
    #     age_list = []
    #     for c in cattle:
    #         age_in_months = self.calculate_cattle_age(c.birth_date, estimation_date)
    #         cattle_dict = {
    #             'id': c.id,  # Add cattle ID to the dictionary
    #             'gender': c.gender,
    #             'age_in_months': age_in_months,
    #         }
    #         age_list.append(cattle_dict)
    #
    #     total_cows = sum(1 for c in cattle if c.gender == 'Cow')
    #     total_calves = sum(
    #         1 for item in age_list if item['gender'] in ['Heifer', 'Bull'] and item['age_in_months'] < 12)
    #     total_young_heifer = sum(
    #         1 for item in age_list if item['gender'] == 'Heifer' and 12 <= item['age_in_months'] < 24)
    #     total_adult_heifer = sum(1 for item in age_list if item['gender'] == 'Heifer' and item['age_in_months'] >= 24)
    #     total_young_bull = sum(1 for item in age_list if item['gender'] == 'Bull' and 12 <= item['age_in_months'] < 24)
    #     total_adult_bull = sum(1 for item in age_list if item['gender'] == 'Bull' and item['age_in_months'] >= 24)
    #
    #     cattle_count = {
    #         'total_cattle': total_cattle,
    #         'total_cows': total_cows,
    #         'total_calves': total_calves,
    #         'total_young_heifer': total_young_heifer,
    #         'total_adult_heifer': total_adult_heifer,
    #         'total_young_bull': total_young_bull,
    #         'total_adult_bull': total_adult_bull,
    #     }
    #
    #     return cattle_count


class GenerateReportView(View):
    generate_report_template = 'my_farm/generate_report.html'
    def __init__(self):
        self.start_date = None
        self.end_date = None

    def get(self, request):
        return render(request, self.generate_report_template)

    def post(self, request):
        self.start_date = date.fromisoformat(request.POST.get('start_date'))
        self.end_date = date.fromisoformat(request.POST.get('end_date'))

        # Store the data in session
        request.session['report_data'] = {
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat(),
        }

        return redirect(reverse('my_farm:report'))


class LivestockMovementReportView(GroupsManagement, GroupNumbers, GenerateReportView, View):
    report_template = 'my_farm/livestock_movement_report.html'

    def __init__(self):
        super().__init__()
        self.groups = []

    def load_report_data(self, request):
        report_data = request.session.get('report_data')
        if not report_data:
            return False

        self.start_date = date.fromisoformat(report_data['start_date'])
        self.end_date = date.fromisoformat(report_data['end_date'])

        return True

    def get(self, request):
        if not self.load_report_data(request):
            return redirect('my_farm:generate_report')

        groups_manager = GroupsManagement

        estimation_date = groups_manager.calculate_groups(self, estimation_date=self.end_date)
        start_date_groups = groups_manager.calculate_groups(self, estimation_date=self.start_date)
        end_date_groups = groups_manager.calculate_groups(self, estimation_date=self.end_date)
        # start_date_weight = groups_manager.estimate_weight_by_groups(self, estimation_date=self.start_date,
        #                                                              group_data=start_date_groups)
        # end_date_weight = groups_manager.estimate_weight_by_groups(self, estimation_date=self.end_date,
        #                                                            group_data=end_date_groups)

        self.groups = []
        for group_name, cattle_data in estimation_date.items():
            group = GroupNumbers(group_name, cattle_data)
            group.quantity(start_date_groups, end_date_groups)
            group.weight_in_groups_by_date(start_date_groups, end_date_groups)
            group.acquisition_loss(self.start_date, self.end_date)
            group.check_movement(start_date_groups, end_date_groups)
            self.groups.append(group)

        context = {
            'start_date': self.start_date,
            'end_date': self.end_date,
            'groups': self.groups,
        }

        return render(request, self.report_template, context)

    def calculate_cattle(self, estimation_date):
        cattle = Cattle.objects.all()
        total_cattle = cattle.count()

        age_list = []
        cattle_ids = {
            'total_cows': [],
            'total_calves': [],
            'total_young_heifer': [],
            'total_adult_heifer': [],
            'total_young_bull': [],
            'total_adult_bull': [],
        }

        for c in cattle:
            age_in_months = self.calculate_cattle_age(c.birth_date, estimation_date)
            cattle_dict = {
                'id': c.id,  # Add cattle ID to the dictionary
                'gender': c.gender,
                'age_in_months': age_in_months,
            }
            age_list.append(cattle_dict)

            if c.gender in ['Cow'] and age_in_months >= 24:
                cattle_ids['total_cows'].append(c.id)
            if c.gender in ['Heifer', 'Bull'] and age_in_months < 12:
                cattle_ids['total_calves'].append(c.id)
            elif c.gender == 'Heifer' and 12 <= age_in_months < 24:
                cattle_ids['total_young_heifer'].append(c.id)
            elif c.gender == 'Heifer' and age_in_months >= 24:
                cattle_ids['total_adult_heifer'].append(c.id)
            elif c.gender == 'Bull' and 12 <= age_in_months < 24:
                cattle_ids['total_young_bull'].append(c.id)
            elif c.gender == 'Bull' and age_in_months >= 24:
                cattle_ids['total_adult_bull'].append(c.id)

        total_cows = len(cattle_ids['total_cows'])
        total_calves = len(cattle_ids['total_calves'])
        total_young_heifer = len(cattle_ids['total_young_heifer'])
        total_adult_heifer = len(cattle_ids['total_adult_heifer'])
        total_young_bull = len(cattle_ids['total_young_bull'])
        total_adult_bull = len(cattle_ids['total_adult_bull'])

        cattle_count = {
            'total_cattle': total_cattle,
            'total_cows': total_cows,
            'total_calves': total_calves,
            'total_young_heifer': total_young_heifer,
            'total_adult_heifer': total_adult_heifer,
            'total_young_bull': total_young_bull,
            'total_adult_bull': total_adult_bull,
        }

        return cattle_ids, cattle_count

    def estimate_cow_weight(self, cattle_id, estimation_date):
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

        return weight

    def estimate_total_weight_by_ranges(self, estimation_date):
        cattle_ids, _ = self.calculate_cattle(estimation_date)  # Assign only the cattle_ids dictionary

        total_weight = {}
        for age_category, ids_list in cattle_ids.items():
            if ids_list:
                cattle_queryset = Cattle.objects.filter(id__in=ids_list)  # Filter by the cattle IDs
                weight = 0
                for cattle in cattle_queryset:
                    weight += self.estimate_cow_weight(cattle.id, estimation_date)

                total_weight[age_category] = weight

        return total_weight

    def calculate_cattle_weight_by_date(self, request):
        if not self.load_report_data(request):
            return redirect('my_farm:generate_report')

        weight_count_by_date = {
            'start_date_count_weight': self.estimate_total_weight_by_ranges(self.start_date),
            'end_date_count_weight': self.estimate_total_weight_by_ranges(self.end_date)
        }

        return weight_count_by_date


