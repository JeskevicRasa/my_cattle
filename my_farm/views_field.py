from django.core.paginator import Paginator
from django.db.models import Count
from django.shortcuts import render, redirect, get_object_or_404
from my_cattle.forms import FieldForm
from .models import Field, Herd


def field_list(request):
    fields = Field.objects.annotate(count_herd=Count('field_herds'))

    paginator = Paginator(fields, 5)  # Show 10 herds per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'fields/field_list.html', {'page_obj': page_obj})


def add_field(request):
    if request.method == 'POST':
        form = FieldForm(request.POST, request.FILES)
        if form.is_valid():
            field = form.save()
            herd_ids = request.POST.getlist('herd')
            herds = Herd.objects.filter(id__in=herd_ids)

            # Allocate herds to the newly created field
            for herd in herds:
                herd.field = field
                herd.save()

            return redirect('my_farm:field_list')
    else:
        form = FieldForm()

    # Retrieve the herd_queryset
    herd_queryset = Herd.objects.all()

    return render(request, 'fields/add_field.html', {'form': form, 'herd_queryset': herd_queryset})


def update_field(request, field_id):
    field = get_object_or_404(Field, id=field_id) if field_id else None

    if request.method == 'POST':
        form = FieldForm(request.POST, request.FILES, instance=field)
        if form.is_valid():
            updated_field = form.save()

            herd_ids = request.POST.getlist('herd')
            herds = Herd.objects.filter(id__in=herd_ids)

            # Deallocate herds from their old fields
            Herd.objects.filter(field=updated_field).update(field=None)

            # Allocate herds to the updated field
            herds.update(field=updated_field)

            return redirect('my_farm:field_detail', field_id=field_id)
    else:
        form = FieldForm(instance=field)

    # Retrieve the herd_queryset
    herd_queryset = Herd.objects.all()

    return render(request, 'fields/update_field.html', {'form': form, 'field': field, 'herd_queryset': herd_queryset})


def field_detail(request, field_id=None):
    field = get_object_or_404(Field, id=field_id) if field_id else None

    if field:
        field.herd_count = field.field_herds.count()

    return render(request, 'fields/field_detail.html', {'field': field})


def upload_field_picture(request, field_id):
    field = get_object_or_404(Field, id=field_id)

    if request.method == 'POST':
        picture = request.FILES.get('picture')

        if picture:
            field.picture = picture
            field.save()
            return redirect('my_farm:field_detail', field_id=field_id)

    return render(request, 'my_farm/upload_picture.html')


def herd_list_by_field(request, field_id):
    field = get_object_or_404(Field, id=field_id)
    herd_list = Herd.objects.filter(field=field).annotate(count_cattle=Count('cattle'))

    return render(request, 'fields/herd_list_by_field.html', {'field': field, 'herd_list': herd_list})





