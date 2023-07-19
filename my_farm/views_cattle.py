from django.core.paginator import Paginator
from django.db.models import Q
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import DeleteView
from my_cattle.forms import GenderForm, CattleForm
from my_farm.models import Cattle, Herd


def cattle_info(request):
    query_loss_method_null = request.GET.get('query_loss_method_null')

    cattle = Cattle.objects.filter(deleted=False)

    if query_loss_method_null:
        cattle = cattle.filter(loss_method__isnull=True)

    paginator = Paginator(cattle, 6)  # Show 3 cattle per page

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'cattle': page_obj,
    }
    # print(context)

    # Get a list of all the columns in the Cattle model
    all_columns = ['ID', 'Type', 'Number', 'Name', 'Gender', 'Breed', 'Birth Date',
                   'Acquisition Method', 'Entry Date', 'Loss Method', 'End Date', 'Comments']

    if request.method == 'POST':
        selected_columns = request.POST.getlist('columns')

        if len(selected_columns) > 0:
            # Build a dictionary of column names and their corresponding database field names
            column_dict = {
                'ID': 'id',
                'Type': 'type',
                'Number': 'number',
                'Name': 'name',
                'Gender': 'gender',
                'Breed': 'breed',
                'Birth Date': 'birth_date',
                'Acquisition Method': 'acquisition_method',
                'Entry Date': 'entry_date',
                'Loss Method': 'loss_method',
                'End Date': 'end_date',
                'Comments': 'comments'
            }

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

    return render(request, 'cattle/cattle_info.html', context)


def search_cattle(request):
    query = request.GET.get('query')
    if query:
        cattle_list = Cattle.objects.filter(deleted=False).filter(
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
        cattle_list = Cattle.objects.filter(deleted=False)

    context = {
        'cattle_list': cattle_list,
        'query': query,
    }
    return render(request, 'cattle/search_cattle.html', context)


def add_cattle(request):
    if request.method == 'POST':
        form = GenderForm(request.POST, request.FILES)
        if form.is_valid():
            cattle = form.save(commit=False)
            herd_id = request.POST.get('herd')  # Get the selected herd ID from the POST data
            herd = Herd.objects.get(id=herd_id)  # Retrieve the corresponding herd object
            cattle.herd = herd  # Assign the herd to the cattle object
            cattle.save()  # Save the cattle object
            return redirect('my_farm:cattle_info')
    else:
        form = GenderForm()
    herd_queryset = Herd.objects.all()  # Retrieve all herd objects
    return render(request, 'cattle/add_cattle.html', {'form': form, 'herd_queryset': herd_queryset})


def update_cattle(request, cattle_id=None):
    cattle = get_object_or_404(Cattle, id=cattle_id) if cattle_id else None

    if request.method == 'POST':
        form = CattleForm(request.POST, request.FILES, instance=cattle)
        if form.is_valid():
            cattle = form.save(commit=False)
            herd_id = request.POST.get('herd')  # Get the selected herd ID from the POST data
            herd = Herd.objects.get(id=herd_id)  # Retrieve the corresponding herd object
            cattle.herd = herd  # Assign the herd to the cattle object
            cattle.save()  # Save the cattle object
            return redirect('my_farm:cattle_detail', cattle_id=cattle_id)
    else:
        form = CattleForm(instance=cattle)

    context = {'form': form, 'cattle': cattle}
    return render(request, 'cattle/update_cattle.html', context)


def cattle_detail(request, cattle_id=None):
    cattle = get_object_or_404(Cattle, id=cattle_id) if cattle_id else None
    return render(request, 'cattle/cattle_detail.html', {'cattle': cattle})


def upload_cattle_picture(request, cattle_id):
    cattle = get_object_or_404(Cattle, id=cattle_id)

    if request.method == 'POST':
        picture = request.FILES.get('picture')

        if picture:
            cattle.picture = picture
            cattle.save()
            return redirect('my_farm:cattle_detail', cattle_id=cattle_id)

    return render(request, 'my_farm/upload_picture.html')


class CattleDeleteView(DeleteView):
    model = Cattle
    template_name = 'cattle/cattle_confirm_delete.html'  # Update with the appropriate template name
    success_url = reverse_lazy('my_farm:cattle_info')  # Updated URL pattern name

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)
        if obj.deleted:
            raise Http404("The cattle does not exist.")
        return obj

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()  # Call the delete method
        return HttpResponseRedirect(self.get_success_url())


def delete_confirmation_page(request):
    return render(request, 'cattle/confirmation_page.html')

