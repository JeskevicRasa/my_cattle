from datetime import date, datetime
from django.shortcuts import render, redirect
from django.views import View
from .constants import MAX_REPORTS
from .groups import GroupsManagement, GroupNumbers
import json
from .models import CattleMovementReport


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
        # print(end_date_groups)
        print(start_date_groups)



        self.groups = []
        for group_name, cattle_data in end_date_groups.items():
            group = GroupNumbers(group_name, cattle_data)
            # group.weight_in_groups_by_date(start_date_groups, end_date_groups)
            # group.birth_acquisition(self.start_date, self.end_date)
            # group.other_acquisition(self.start_date, self.end_date)
            # group.loss_method(self.start_date, self.end_date)
            group.acquisition_loss(self.start_date, self.end_date)
            group.quantity(start_date_groups, end_date_groups)
            # group.weight_in_groups_by_date(start_date_groups, end_date_groups)
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
