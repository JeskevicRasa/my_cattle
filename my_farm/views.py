from django.http import HttpResponse
from .models import Cattle
from django.views import generic
from django.shortcuts import render, redirect
from my_cattle.forms import GenderForm


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
                           'Breed': 'breed', 'Birth Date': 'birth_date', 'Entry date': 'entry_date', 'End date': 'end_date',
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


def delete_row(request, cattle_id):
    row = Cattle.objects.get(id=cattle_id)

    if request.method == 'POST':
        row.delete()
        return redirect('my_farm:confirmation_page')
    else:
        return render(request, 'my_farm/delete_row.html', {'row': row})


def confirmation_page(request):
    return render(request, 'my_farm/confirmation_page.html')