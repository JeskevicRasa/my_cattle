from datetime import date
from django.utils.text import slugify
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.template.defaultfilters import slugify
from django.utils import timezone
from .models import Herd, Field
from django.urls import reverse
from .groups import GroupsManagement, CattleGroupData


@login_required
def home(request):
    """
    Renders the home page of the "My Farm" application.

    Retrieves various statistics and groups of cattle for display on the home page.

    :param request: The HTTP request object.
    :return: The rendered home page with the required data.
    """
    active_herds_count = Herd.objects.filter(is_active=True, start_date__lte=timezone.now()).count()
    active_field_count = Field.objects.filter(is_active=True).count()

    groups_manager = GroupsManagement()
    today_groups = groups_manager.calculate_groups(estimation_date=date.today())

    total_cattle_count = 0
    for group_data in today_groups.values():
        alive_cows_in_group = 0
        for cattle_data in group_data:
            if cattle_data['cattle']['end_date'] is None:
                alive_cows_in_group += 1
        total_cattle_count += alive_cows_in_group

    groups = []
    for group_name, cattle_data in today_groups.items():
        group = CattleGroupData(group_name, cattle_data)
        group.count_active_cattle()
        group_url = reverse('my_farm:group_data', args=[slugify(group_name)])
        group.url = group_url
        groups.append(group)

    context = {
        'groups': groups,
        'active_herds_count': active_herds_count,
        'active_field_count': active_field_count,
        'total_cattle_count': total_cattle_count,
    }

    return render(request, 'my_farm/my_farm_main.html', context)


def group_data(request, group_name):
    """
    Renders the group data page for the selected group.

    Retrieves the cattle data for the selected group and displays it on the page.

    :param request: The HTTP request object.
    :param group_name: The name of the selected group.
    :return: The rendered group data page with the selected group's data.
    """
    groups_manager = GroupsManagement()
    today_cattle = groups_manager.calculate_groups(estimation_date=date.today())

    selected_group = group_name

    groups = []
    if selected_group in today_cattle:
        cattle_data = today_cattle[selected_group]
        group = CattleGroupData(selected_group, cattle_data)
        group.cattle_data()
        groups.append(group)

    context = {
        'groups': groups,
        'selected_group': selected_group
    }
    return render(request, 'my_farm/group_data.html', context)
