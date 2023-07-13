from dateutil.relativedelta import relativedelta
from datetime import date
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import DeleteView
from my_cattle.forms import GenderForm, CattleForm
from .models import Cattle
from django.views import View
from django.urls import reverse, reverse_lazy
from .groups import GroupsManagement, GroupNumbers
from datetime import datetime


def calculate_cattle_age(birth_date, estimation_date):
    if estimation_date < birth_date:
        return -1
    else:
        age = relativedelta(estimation_date, birth_date)
        age_in_months = age.years * 12 + age.months
        return age_in_months


def calculate_cattle(estimation_date):
    cattle = Cattle.objects.filter(deleted=False)
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


def calculate_age_group(birth_date, estimation_date, gender):

    age_in_months = calculate_cattle_age(birth_date, estimation_date)
    print(age_in_months)
    if gender in 'Cows':
        return 'Cows'
    if gender in ['Heifer', 'Bull']:
        if age_in_months < 12:
            return 'Calves'
    if gender in 'Bull':
        if 12 <= age_in_months < 24:
            return 'Young Bull'
        if age_in_months >= 24:
            return 'Adult Bull'
    if gender == 'Heifer':
        if 12 <= age_in_months < 24:
            return 'Young Heifer'
        if age_in_months >= 24:
            return 'Adult Heifer'

    return 'Unknown'


def cattle_info(request):
    cattle = Cattle.objects.filter(deleted=False)
    paginator = Paginator(cattle, 3)  # Show 3 cattle per page

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    for cow in page_obj:
        cow.age_group = calculate_age_group(cow.birth_date, date.today(), cow.gender)
        print(cow.age_group)

    # print(cow.age_group)
    context = {
        'cattle': page_obj,
    }

    # Get a list of all the columns in the Cattle model
    all_columns = ['ID', 'Type', 'Number', 'Name', 'Gender', 'Age Group', 'Breed', 'Birth Date',
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
                'Age Group': 'age_group',
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

    return render(request, 'my_farm/cattle_info.html', context)


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
        form = CattleForm(request.POST, request.FILES, instance=cattle)
        if form.is_valid():
            form.save()
            return redirect('my_farm:one_cattle_info', cattle_id=cattle_id)
    else:
        form = CattleForm(instance=cattle)

    context = {'form': form, 'cattle': cattle}
    return render(request, 'my_farm/update_cattle.html', context)


def one_cattle_info(request, cattle_id=None):
    cattle = get_object_or_404(Cattle, id=cattle_id) if cattle_id else None

    context = {'cattle': cattle}
    return render(request, 'my_farm/one_cattle_info.html', context)


def upload_picture(request, cattle_id):
    cattle = get_object_or_404(Cattle, id=cattle_id)

    if request.method == 'POST':
        picture = request.FILES.get('picture')

        if picture:
            cattle.picture = picture
            cattle.save()
            return redirect('my_farm:one_cattle_info', cattle_id=cattle_id)

    return render(request, 'my_farm/upload_picture.html', {'cattle': cattle})


class CattleDeleteView(DeleteView):
    model = Cattle
    template_name = 'my_farm/cattle_confirm_delete.html'  # Update with the appropriate template name
    success_url = reverse_lazy('my_farm:cattle_info')  # Updated URL pattern name

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)
        if obj.deleted:
            raise Http404("The cattle does not exist.")
        return obj

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()  # Call the delete method
        return HttpResponseRedirect(self.get_success_url())


def confirmation_page(request):
    return render(request, 'my_farm/confirmation_page.html')


def search_cattle(request):
    query = request.GET.get('query')
    if query:
        cattle_list = Cattle.objects.filter(deleted=False).filter(
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
        cattle_list = Cattle.objects.filter(deleted=False)

    context = {
        'cattle_list': cattle_list,
        'query': query,
    }
    return render(request, 'my_farm/search_cattle.html', context)


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
