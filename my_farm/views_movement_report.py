
from datetime import date
from django.shortcuts import render, redirect
from django.views import View
from django.urls import reverse
from .groups import GroupsManagement, GroupNumbers


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
