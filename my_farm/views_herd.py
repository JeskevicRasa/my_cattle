from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.shortcuts import render, redirect, get_object_or_404
from my_cattle.forms import HerdForm
from my_farm.models import Cattle, Herd


def herd_list(request):
    """
    Retrieves herd information and displays the list of herds.

    This view retrieves information about herds, including the number of active cattle in each herd. Only cattle that
    are not marked as deleted and have no loss method specified are counted. The herds are paginated to display 5 herds
    per page.

    :param request: The HTTP request object.
    :return: The rendered HTTP response with the herd information displayed.

    """

    cattle_count_query = Count(
        'cattle',
        filter=Q(cattle__deleted=False, cattle__loss_method__isnull=True)
    )

    is_active = request.GET.get('is_active')

    herds = Herd.objects.annotate(count_cattle=cattle_count_query)
    if is_active == 'True':
        herds = herds.filter(is_active=True)

    paginator = Paginator(herds, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {'page_obj': page_obj}
    return render(request, 'herd/herd_list.html', context)


def add_herd(request):
    """
    Adds a new row to the herd table based on the submitted form data.

    :param request: The HTTP request object.
    :return: The rendered HTTP response with the form or a redirect to the herd list page.
    """
    if request.method == 'POST':
        form = HerdForm(request.POST, request.FILES)
        if form.is_valid():
            herd = form.save(commit=False)

            herd.save()

            herd_leader_id = request.POST.get('herd_leader')
            if herd_leader_id:
                herd_leader = Cattle.objects.filter(id=herd_leader_id, deleted=False, loss_method__isnull=True).first()
                if herd_leader:
                    herd.herd_leader = herd_leader
                    herd.save()

            return redirect('my_farm:herd_list')
    else:
        form = HerdForm()

    cattle_queryset = Cattle.objects.filter(deleted=False, loss_method__isnull=True)

    return render(request, 'herd/add_herd.html', {'form': form, 'cattle_queryset': cattle_queryset})


def update_herd(request, herd_id=None):
    """
    Updates the information of a specific herd based on the submitted form data.

    :param request: The HTTP request object.
    :param herd_id: The ID of the herd to be updated.
    :return: The rendered HTTP response with the form or a redirect to the herd list page.
    """
    herd = get_object_or_404(Herd, id=herd_id) if herd_id else None

    if request.method == 'POST':
        form = HerdForm(request.POST, request.FILES, instance=herd)
        if form.is_valid():
            updated_herd = form.save()

            herd_leader_id = request.POST.get('herd_leader')
            if herd_leader_id:
                herd_leader = Cattle.objects.get(id=herd_leader_id)
                updated_herd.herd_leader = herd_leader
                updated_herd.save()

            return redirect('my_farm:herd_detail', herd_id=herd_id)
    else:
        form = HerdForm(instance=herd)

    form.fields['cattle'].queryset = Cattle.objects.filter(deleted=False, loss_method__isnull=True)
    form.fields['herd_leader'].queryset = Cattle.objects.filter(deleted=False, loss_method__isnull=True)

    return render(request, 'herd/update_herd.html', {'form': form, 'herd': herd})


def herd_detail(request, herd_id=None):
    """
    Displays detailed information about a specific herd.

    :param request: The HTTP request object.
    :param herd_id: The ID of the herd to display information about.
    :return: The rendered HTTP response with the herd information.
    """
    herd = get_object_or_404(Herd, id=herd_id) if herd_id else None

    if herd:
        herd.cattle_count = herd.cattle_set.filter(deleted=False, loss_method__isnull=True).count()

    return render(request, 'herd/herd_detail.html', {'herd': herd})


def upload_herd_picture(request, herd_id):
    """
    Handles the uploading of a picture for a specific herd.

    :param request: The HTTP request object.
    :param herd_id: The ID of the herd to upload a picture for.
    :return: The rendered HTTP response with the form or a redirect to the herd list page.
    """
    herd = get_object_or_404(Herd, id=herd_id)

    if request.method == 'POST':
        picture = request.FILES.get('picture')

        if picture:
            herd.picture = picture
            herd.save()
            return redirect('my_farm:herd_detail', herd_id=herd_id)

    return render(request, 'my_farm/upload_picture.html')


def cattle_list_by_herd(request, herd_id):
    """
    Retrieves the list of cattle belonging to a specific herd.
    Filters the cattle_list based on the specified herd ID, ensuring that only
    cattle that are not deleted and have no loss_method assigned are included.
    The cattle_list is then rendered using the cattle_list_by_herd.html template.

    :param request: The HTTP request object.
    :param herd_id: The ID of the herd for which to retrieve the cattle list.
    :return: The rendered cattle_list_by_herd page with the herd and cattle_list as context.
    """
    herd = get_object_or_404(Herd, id=herd_id)
    cattle_list = Cattle.objects.filter(herd=herd, deleted=False, loss_method__isnull=True)

    context = {
        'herd': herd,
        'cattle_list': cattle_list,
    }
    return render(request, 'herd/cattle_list_by_herd.html', context)


def search_herd(request):
    """
    Performs a search query on the Herd model based on the provided query parameter.
    It filters the herd_list based on various fields. The filtered herd_list is
    then rendered using the search_herd.html template.

    :param request: The HTTP request object.
    :return: The rendered search_herd page with the filtered herd_list and query parameter as context.
    """
    query = request.GET.get('query')

    if query:
        try:
            is_active_value = {'true': True, 'false': False}[query.lower()]
        except KeyError:
            is_active_value = None

        herd_list = Herd.objects.annotate(
            count_cattle=Count('cattle')
        ).filter(
            Q(name__icontains=query) |
            Q(location__icontains=query) |
            Q(field__name__icontains=query) |
            Q(description__icontains=query) |
            Q(start_date__icontains=query) |
            Q(herd_leader__name__icontains=query) |
            Q(count_cattle__icontains=query) |
            Q(is_active=is_active_value)
        )
    else:
        herd_list = Herd.objects.annotate(count_cattle=Count('cattle'))

    context = {
        'herd_list': herd_list,
        'query': query,
    }
    return render(request, 'herd/search_herd.html', context)

