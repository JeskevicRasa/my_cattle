from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver

from dateutil.relativedelta import relativedelta
from datetime import date, datetime
from django.core.paginator import Paginator
from django.db.models import Q, Max
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import DeleteView
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

from my_cattle.forms import GenderForm, CattleForm
from .models import Cattle, CattleMovementReport
from django.views import View
from django.urls import reverse, reverse_lazy
from .groups import GroupsManagement, GroupNumbers
import json
import io
from django.http import HttpResponse
from .constants import MAX_REPORTS


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
    """
    Retrieves cattle information and handles column selection for display.

    :param request: The HTTP request object.
    :return: The rendered HTTP response with the cattle information displayed.
    """
    cattle = Cattle.objects.filter(deleted=False)
    paginator = Paginator(cattle, 5)  # Show 3 cattle per page

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
    """
    Adds a new row to the cattle table based on the submitted form data.

    :param request: The HTTP request object.
    :return: The rendered HTTP response with the form or a redirect to the cattle information page.
    """
    if request.method == 'POST':
        form = GenderForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('my_farm:cattle_info')
    else:
        form = GenderForm()
    return render(request, 'my_farm/add_row.html', {'form': form})


def update_cattle(request, cattle_id=None):
    """
    Updates the information of a specific cattle based on the submitted form data.

    :param request: The HTTP request object.
    :param cattle_id: The ID of the cattle to be updated.
    :return: The rendered HTTP response with the form or a redirect to the cattle information page.
    """
    cattle = get_object_or_404(Cattle, id=cattle_id) if cattle_id else None

    if request.method == 'POST':
        form = GenderForm(request.POST, request.FILES, instance=cattle)
        if form.is_valid():
            form.save()
            return redirect('my_farm:one_cattle_info', cattle_id=cattle_id)
    else:
        form = GenderForm(instance=cattle)

    context = {'form': form, 'cattle': cattle}
    return render(request, 'my_farm/update_cattle.html', context)


def one_cattle_info(request, cattle_id=None):
    """
    Displays detailed information about a specific cattle.

    :param request: The HTTP request object.
    :param cattle_id: The ID of the cattle to display information about.
    :return: The rendered HTTP response with the cattle information.
    """
    cattle = get_object_or_404(Cattle, id=cattle_id) if cattle_id else None

    context = {'cattle': cattle}
    return render(request, 'my_farm/one_cattle_info.html', context)


def upload_picture(request, cattle_id):
    """
    Handles the uploading of a picture for a specific cattle.

    :param request: The HTTP request object.
    :param cattle_id: The ID of the cattle to upload a picture for.
    :return: The rendered HTTP response with the form or a redirect to the cattle information page.
    """
    cattle = get_object_or_404(Cattle, id=cattle_id)

    if request.method == 'POST':
        picture = request.FILES.get('picture')

        if picture:
            cattle.picture = picture
            cattle.save()
            return redirect('my_farm:one_cattle_info', cattle_id=cattle_id)

    return render(request, 'my_farm/upload_picture.html', {'cattle': cattle})


class CattleDeleteView(DeleteView):
    """
    This class is responsible for deleting a cattle object. It inherits from the DeleteView class provided
    by the Django framework. Upon deletion, it redirects to the cattle_info page.

    Attributes:
    model: The model to be deleted (Cattle).
    template_name: The name of the template used for the confirmation page.
    success_url: The URL to redirect to after successful deletion.

    Methods:
    get_object(self, queryset=None): Retrieves the cattle object to be deleted. If the cattle object
    is already marked as deleted, it raises an Http404 exception.
    post(self, request, *args, **kwargs): Handles the HTTP POST request for deleting the cattle object.
    It calls the _delete() method on the cattle object and redirects to the success_url.
    """
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
    """
    Renders the confirmation_page.html template.

    :param request: The HTTP request object.
    :return: The rendered confirmation page.
    """
    return render(request, 'my_farm/confirmation_page.html')


def search_cattle(request):
    """
    Performs a search query on the Cattle model based on the provided query parameter.
    It filters the cattle_list based on various fields and renders the search_cattle.html template.

    :param request: The HTTP request object.
    :return: The rendered search_cattle page with the filtered cattle_list and query parameter as context.
    """
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
    """
    A view class for generating a report.

    Inherits from View.

    Attributes:
        generate_report_template (str): The template for rendering the generate report page.

    Methods:
        __init__(): Initializes the class and sets initial values.
        get(request): Handles the GET request for displaying the generate report page.
        post(request): Handles the POST request for generating a report.
    """

    generate_report_template = 'my_farm/generate_report.html'

    def __init__(self):
        """
        Initializes the GenerateReportView class.

        Sets initial values for start_date and end_date attributes.

        Calls the __init__ method of the super class.
        """
        super().__init__()
        self.start_date = None
        self.end_date = None

    def get(self, request):
        """
        Handles the GET request for displaying the generate report page.

        Args:
            request (HttpRequest): The HTTP request object.

        Returns:
            HttpResponse: The rendered HTTP response for the generate report page.
        """
        return render(request, self.generate_report_template)

    def post(self, request):
        """
        Handles the POST request for generating a report.

        Args:
            request (HttpRequest): The HTTP request object.

        Returns:
            HttpResponse: The redirect HTTP response to the report page.
        """
        start_date = datetime.fromisoformat(request.POST.get('start_date')).date()
        end_date = datetime.fromisoformat(request.POST.get('end_date')).date()

        # Store the data in session
        request.session['report_data'] = {
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
        }

        return redirect('my_farm:report')


class LivestockMovementReportView(GroupsManagement, GenerateReportView, View):
    """
    A view class for generating and displaying the livestock movement report.

    Inherits from GroupsManagement, GenerateReportView, and View.

    Attributes:
        report_template (str): The template for rendering the report.

    Methods:
        __init__(): Initializes the class and sets initial values.
        load_report_data(request): Loads the report data from the session.
        get(request): Handles the GET request for generating and displaying the report.
    """

    report_template = 'my_farm/livestock_movement_report.html'

    def __init__(self):
        """
        Initializes the LivestockMovementReportView class.

        Calls the __init__ methods of the super classes and sets initial values for groups and encoder_class attributes.
        """
        super(GroupsManagement, self).__init__()
        super(GenerateReportView, self).__init__()
        super(View, self).__init__()
        self.groups = []
        self.encoder_class = GroupNumbersEncoder

    def load_report_data(self, request):
        """
        Loads the report data from the session.

        Args:
            request (HttpRequest): The HTTP request object.

        Returns:
            bool: True if the report data is loaded successfully, False otherwise.
        """
        report_data = request.session.get('report_data')
        if not report_data:
            return False

        self.start_date = date.fromisoformat(report_data['start_date'])
        self.end_date = date.fromisoformat(report_data['end_date'])

        return True

    def get(self, request):
        """
        Handles the GET request for generating and displaying the livestock movement report.

        Args:
            request (HttpRequest): The HTTP request object.

        Returns:
            HttpResponse: The rendered HTTP response with the generated report.
        """
        if not self.load_report_data(request):
            return redirect('my_farm:generate_report')

        groups_manager = GroupsManagement()

        estimation_date = groups_manager.calculate_groups(estimation_date=self.end_date)
        start_date_groups = groups_manager.calculate_groups(estimation_date=self.start_date)
        end_date_groups = groups_manager.calculate_groups(estimation_date=self.end_date)

        self.groups = []
        for group_name, cattle_data in estimation_date.items():
            group = GroupNumbers(group_name, cattle_data)
            group.quantity(start_date_groups, end_date_groups)
            group.weight_in_groups_by_date(start_date_groups, end_date_groups)
            group.acquisition_loss(self.start_date, self.end_date)
            group.check_movement(start_date_groups, end_date_groups)
            self.groups.append(group)

        context = {
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat(),
            'groups': self.groups,
        }

        group_dicts = [group.to_dict() for group in self.groups]

        # Check if the last reports URL is accessed
        last_reports = CattleMovementReport.objects.order_by('-id')[1:4]

        # Pass the last reports to the template
        context['last_reports'] = last_reports

        # Save the report data
        report_data = json.dumps(group_dicts, cls=self.encoder_class, default=str)
        report_title = f'Cattle Movement Report ({self.start_date.isoformat()} - {self.end_date.isoformat()})'
        report = CattleMovementReport(title=report_title, report_data=report_data)
        report.save()

        all_reports = CattleMovementReport.objects.order_by('-id')

        # Keep the most recent reports (MAX_REPORTS)
        recent_reports = all_reports[:MAX_REPORTS]

        # Delete reports that are not in the recent reports list
        old_reports = all_reports.exclude(pk__in=recent_reports)
        old_reports.delete()

        # Pass the report ID to the template
        context['report_id'] = report.pk

        return render(request, self.report_template, context)


class GroupNumbersEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, GroupNumbers):
            return obj.to_dict()
        if isinstance(obj, date):
            return obj.isoformat()
        return super().default(obj)


class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, date):
            return obj.isoformat()
        return super().default(obj)


def generate_pdf(request):
    # Set up Selenium webdriver with Chrome options
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run Chrome in headless mode
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    # Initialize the Chrome webdriver
    driver = webdriver.Chrome(options=options)

    # Load the web page
    driver.get('http://127.0.0.1:8000/my_farm/livestock_movement_report/')

    # Wait for the report to load
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.container')))

    # Take a screenshot of the web page
    screenshot = driver.get_screenshot_as_png()

    # Close the Selenium webdriver
    driver.quit()

    # Create an empty PDF file
    pdf_file = io.BytesIO()

    # Convert the screenshot image to PDF
    from PIL import Image
    img = Image.open(io.BytesIO(screenshot))
    img.save(pdf_file, 'PDF')

    # Set the PDF file content type and headers
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="report.pdf"'

    # Write the PDF file content to the response
    response.write(pdf_file.getvalue())

    return response
