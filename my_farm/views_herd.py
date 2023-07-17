
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.shortcuts import render, redirect, get_object_or_404
from my_cattle.forms import HerdForm
from my_farm.models import Cattle, Herd


def herd_list(request):
    herds = Herd.objects.annotate(count_cattle=Count('cattle', filter=Q(cattle__deleted=False)))

    paginator = Paginator(herds, 5)  # Show 10 herds per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'herd/herd_list.html', {'page_obj': page_obj})


def add_herd(request):
    if request.method == 'POST':
        form = HerdForm(request.POST, request.FILES)
        if form.is_valid():
            herd = form.save(commit=False)

            # Save the herd without assigning cattle and herd leader initially
            herd.save()

            # Update the selected cattle with the herd id
            cattle_ids = request.POST.getlist('cattle')
            if cattle_ids:
                for cattle_id in cattle_ids:
                    cattle = Cattle.objects.get(id=cattle_id)
                    cattle.herd = herd
                    cattle.save()

            herd_leader_id = request.POST.get('herd_leader')
            if herd_leader_id:
                herd_leader = Cattle.objects.get(id=herd_leader_id)
                herd.herd_leader = herd_leader
                herd.save()

            return redirect('my_farm:herd_list')
    else:
        form = HerdForm()

    # Pass the cattle queryset to the template context
    cattle_queryset = Cattle.objects.all()

    return render(request, 'herd/add_herd.html', {'form': form, 'cattle_queryset': cattle_queryset})

def update_herd(request, herd_id=None):
    herd = get_object_or_404(Herd, id=herd_id) if herd_id else None

    if request.method == 'POST':
        form = HerdForm(request.POST, request.FILES, instance=herd)
        if form.is_valid():
            updated_herd = form.save()

            cattle_ids = request.POST.getlist('cattle')
            cattle = Cattle.objects.filter(id__in=cattle_ids)

            # Deallocate cattle from their old herds
            Cattle.objects.filter(herd=updated_herd).update(herd=None)

            # Allocate cattle to the updated herd
            cattle.update(herd=updated_herd)

            return redirect('my_farm:herd_detail', herd_id=herd_id)
    else:
        form = HerdForm(instance=herd)

    form.fields['cattle'].queryset = Cattle.objects.filter(deleted=False)  # Set the cattle queryset for the form field

    return render(request, 'herd/update_herd.html', {'form': form, 'herd': herd})


def herd_detail(request, herd_id=None):
    herd = get_object_or_404(Herd, id=herd_id) if herd_id else None

    if herd:
        herd.cattle_count = herd.cattle_set.filter(deleted=False).count()

    return render(request, 'herd/herd_detail.html', {'herd': herd})


def upload_herd_picture(request, herd_id):
    herd = get_object_or_404(Herd, id=herd_id)

    if request.method == 'POST':
        picture = request.FILES.get('picture')

        if picture:
            herd.picture = picture
            herd.save()
            return redirect('my_farm:herd_detail', herd_id=herd_id)

    return render(request, 'my_farm/upload_picture.html')


def cattle_list_by_herd(request, herd_id):
    herd = get_object_or_404(Herd, id=herd_id)
    cattle_list = Cattle.objects.filter(herd=herd, deleted=False)

    context = {
        'herd': herd,
        'cattle_list': cattle_list,
    }
    return render(request, 'herd/cattle_list_by_herd.html', context)


def search_herd(request):
    query = request.GET.get('query')

    if query:
        try:
            is_active_value = {'true': True, 'false': False}[query.lower()]
        except KeyError:
            is_active_value = None

        herd_list = Herd.objects.annotate(
            num_cattle=Count('cattle')
        ).filter(
            Q(name__icontains=query) |
            Q(location__icontains=query) |
            Q(field__name__icontains=query) |
            Q(description__icontains=query) |
            Q(start_date__icontains=query) |
            Q(herd_leader__name__icontains=query) |
            Q(num_cattle__icontains=query) |  # Include search by number of cattle
            Q(is_active=is_active_value)  # Handle boolean values separately
        )
    else:
        herd_list = Herd.objects.annotate(num_cattle=Count('cattle'))

    context = {
        'herd_list': herd_list,
        'query': query,
    }
    return render(request, 'herd/search_herd.html', context)

