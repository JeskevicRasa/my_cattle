from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.shortcuts import render, redirect, get_object_or_404
from my_cattle.forms import FieldForm
from .models import Field, Herd


def field_list(request):
    """
    Retrieves field information and displays the list of fields.
    The fields are paginated to display 5 fields per page.

    :param request: The HTTP request object.
    :return: The rendered HTTP response with the field information displayed.
    """
    is_active = request.GET.get('is_active')
    fields = Field.objects.annotate(count_herd=Count('field_herds'))

    if is_active == 'True':
        fields = fields.filter(is_active=True)

    paginator = Paginator(fields, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'fields/field_list.html', {'page_obj': page_obj})


def add_field(request):
    """
    Adds a new row to the field table based on the submitted form data.

    :param request: The HTTP request object.
    :return: The rendered HTTP response with the form or a redirect to the field list page.
    """
    if request.method == 'POST':
        form = FieldForm(request.POST, request.FILES)
        if form.is_valid():
            field = form.save()
            herd_ids = request.POST.getlist('herd')
            herds = Herd.objects.filter(id__in=herd_ids)

            for herd in herds:
                herd.field = field
                herd.save()

            return redirect('my_farm:field_list')
    else:
        form = FieldForm()

    herd_queryset = Herd.objects.all()

    return render(request, 'fields/add_field.html', {'form': form, 'herd_queryset': herd_queryset})


def update_field(request, field_id):
    """
    Updates the information of a specific field based on the submitted form data.

    :param request: The HTTP request object.
    :param field_id: The ID of the herd to be updated.
    :return: The rendered HTTP response with the form or a redirect to the field list page.
    """
    field = get_object_or_404(Field, id=field_id) if field_id else None

    if request.method == 'POST':
        form = FieldForm(request.POST, request.FILES, instance=field)
        if form.is_valid():
            form.save()

            return redirect('my_farm:field_detail', field_id=field_id)
    else:
        form = FieldForm(instance=field)

    return render(request, 'fields/update_field.html', {'form': form, 'field': field})


def field_detail(request, field_id=None):
    """
    Displays detailed information about a specific field.

    :param request: The HTTP request object.
    :param field_id: The ID of the field to display information about.
    :return: The rendered HTTP response with the field information.
    """
    field = get_object_or_404(Field, id=field_id) if field_id else None

    if field:
        field.herd_count = field.field_herds.count()

    return render(request, 'fields/field_detail.html', {'field': field})


def upload_field_picture(request, field_id):
    """
    Handles the uploading of a picture for a specific field.

    :param request: The HTTP request object.
    :param field_id: The ID of the field to upload a picture for.
    :return: The rendered HTTP response with the form or a redirect to the field list page.
    """
    field = get_object_or_404(Field, id=field_id)

    if request.method == 'POST':
        picture = request.FILES.get('picture')

        if picture:
            field.picture = picture
            field.save()
            return redirect('my_farm:field_detail', field_id=field_id)

    return render(request, 'my_farm/upload_picture.html')


def herd_list_by_field(request, field_id):
    """
    Retrieves the list of herds belonging to a specific field.
    Filters the cattle_list based on the specified field ID.
    The cattle_list is then rendered using the cattle_list_by_herd.html template.

    :param request: The HTTP request object.
    :param field_id: The ID of the field for which to retrieve the herds list.
    :return: The rendered herd_list_by_field page with the field and herd_list as context.
    """
    field = get_object_or_404(Field, id=field_id)
    herd_list = Herd.objects.filter(field=field).annotate(
        count_cattle=Count('cattle', filter=Q(cattle__deleted=False, cattle__loss_method__isnull=True))
    )

    return render(request, 'fields/herd_list_by_field.html', {'field': field, 'herd_list': herd_list})


def search_field(request):
    """
    Performs a search query on the Field model based on the provided query parameter.
    It filters the field_list based on various fields and renders the search_field.html template.

    :param request: The HTTP request object.
    :return: The rendered search_field page with the filtered field_list and query parameter as context.
    """
    query = request.GET.get('query')

    if query:
        try:
            is_active_value = {'true': True, 'false': False}[query.lower()]
        except KeyError:
            is_active_value = None

        field_list = Field.objects.annotate(count_herd=Count('field_herds')).filter(
            Q(name__icontains=query) |
            Q(location__icontains=query) |
            Q(coordinates__icontains=query) |
            Q(field_size__icontains=query) |
            Q(size_unit__icontains=query) |
            Q(field_type__icontains=query) |
            Q(description__icontains=query) |
            Q(is_active=is_active_value)
        )
    else:
        field_list = Field.objects.annotate(count_herd=Count('field_herds'))

    context = {
        'field_list': field_list,
        'query': query,
    }
    return render(request, 'fields/search_field.html', context)


