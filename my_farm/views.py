from django.db.models import Q
from django.http import HttpResponse
from .models import Cattle
from django.views import generic
from django.shortcuts import render, redirect, get_object_or_404
from my_cattle.forms import GenderForm, CattleForm


def home(request):
    return HttpResponse("Hello, you are in my farm yeay")


# def cattle_info(request):
#     rows = Cattle.objects.all()
#     return render(request, 'my_farm/cattle_info.html', {'rows': rows})

def cattle_info(request):
    cattle = Cattle.objects.all()

    # Get a list of all the columns in the Cattle model
    all_columns = [f.name for f in Cattle._meta.get_fields()]

    if request.method == 'POST':
        selected_columns = request.POST.getlist('columns')

        if len(selected_columns) > 0:
            # Build a dictionary of column names and their corresponding database field names
            column_dict = {'ID': 'id', 'Type': 'type', 'Number': 'number', 'Name': 'name', 'Gender': 'gender',
                           'Breed': 'breed', 'Birth Date': 'birth_date', 'acquisition_method': 'acquisition_method',
                           'Entry date': 'entry_date', 'loss_method': 'loss_method', 'End date': 'end_date',
                           'Comments': 'comments'}

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

    return render(request, 'my_farm/cattle_info.html', {'cattle': cattle, 'columns': all_columns})


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
        form = CattleForm(request.POST, instance=cattle)
        if form.is_valid():
            form.save()
            return redirect('my_farm:cattle_info')
    else:
        form = CattleForm(instance=cattle)

    context = {'form': form}
    return render(request, 'my_farm/update_cattle.html', context)


def delete_row(request, cattle_id):
    row = Cattle.objects.get(id=cattle_id)

    if request.method == 'POST':
        row.delete()
        return redirect('my_farm:confirmation_page')
    else:
        return render(request, 'my_farm/delete_row.html', {'row': row})


def confirmation_page(request):
    return render(request, 'my_farm/confirmation_page.html')


def search_cattle(request):
    query = request.GET.get('query')
    if query:
        cattle_list = Cattle.objects.filter(
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
        cattle_list = Cattle.objects.all()

    context = {'cattle_list': cattle_list}
    return render(request, 'my_farm/search_cattle.html', context)