from django.http import HttpResponse
from .models import Cattle
from django.views import generic
from django.shortcuts import render, redirect
from my_cattle.forms import GenderForm


def home(request):
    return HttpResponse("Hello, you are in my farm yeay")


def cattle_info(request):
    rows = Cattle.objects.all()
    return render(request, 'my_farm/cattle_info.html', {'rows': rows})


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