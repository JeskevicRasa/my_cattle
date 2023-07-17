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



@login_required
def home(request):
    active_herds_count = Herd.objects.filter(is_active=True, start_date__lte=timezone.now()).count()
    active_field_count = Field.objects.filter(is_active=True).count()

    groups_manager = GroupsManagement()
    today_groups = groups_manager.calculate_groups(estimation_date=date.today())

    total_cattle_count = 0
    for group_data in today_groups.values():
        alive_cows_in_group = 0  # Initialize a counter for alive cows in the group
        for cattle_data in group_data:
            if cattle_data['cattle']['end_date'] is None:  # Check if cattle is still active
                alive_cows_in_group += 1  # Increment the counter for each active cattle
        total_cattle_count += alive_cows_in_group  # Add the count of active cattle in the group to the total count

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
    return render(request, 'my_farm/search_cattle.html', context)



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
