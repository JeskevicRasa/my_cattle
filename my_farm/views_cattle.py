from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import DeleteView
from my_cattle.forms import GenderForm, CattleForm
from my_farm.models import Cattle, Herd



def cattle_info(request):
    """
    Retrieves cattle information and handles column selection for display.
    The cattle are paginated to display 5 cattle per page.

    :param request: The HTTP request object.
    :return: The rendered HTTP response with the cattle information displayed.
    """
    query_loss_method_null = request.GET.get('query_loss_method_null')

    cattle = Cattle.objects.filter(deleted=False)

    if query_loss_method_null:
        cattle = cattle.filter(loss_method__isnull=True)

    paginator = Paginator(cattle, 4)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'cattle': page_obj,
    }

    all_columns = ['ID', 'Type', 'Number', 'Name', 'Gender', 'Breed', 'Birth Date',
                   'Acquisition Method', 'Entry Date', 'Loss Method', 'End Date', 'Comments']

    if request.method == 'POST':
        selected_columns = request.POST.getlist('columns')

        if len(selected_columns) > 0:
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

            selected_fields = [column_dict[column] for column in selected_columns]

            cattle = cattle.values(*selected_fields)
        else:
            error_message = 'Please select at least one column to display.'
            context['error_message'] = error_message

    else:
        cattle = cattle.values()
        context['selected_columns'] = all_columns


    return render(request, 'cattle/cattle_info.html', context)


def search_cattle(request):
    """
    Performs a search query on the Cattle model based on the provided query parameter.
    It filters the cattle_list based on various fields and renders the search_cattle.html template.

    :param request: The HTTP request object.
    :return: The rendered search_cattle page with the filtered cattle_list and query parameter as context.
    """
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
    """
    Adds a new row to the cattle table based on the submitted form data.

    :param request: The HTTP request object.
    :return: The rendered HTTP response with the form or a redirect to the cattle information page.
    """
    if request.method == 'POST':
        form = GenderForm(request.POST, request.FILES)
        if form.is_valid():
            cattle = form.save(commit=False)
            herd_id = request.POST.get('herd')
            herd = Herd.objects.get(id=herd_id)
            cattle.herd = herd
            cattle.save()
            return redirect('my_farm:cattle_info')
    else:
        form = GenderForm()
    herd_queryset = Herd.objects.all()
    return render(request, 'cattle/add_cattle.html', {'form': form, 'herd_queryset': herd_queryset})


def update_cattle(request, cattle_id=None):
    """
    Updates the information of a specific cattle based on the submitted form data.

    :param request: The HTTP request object.
    :param cattle_id: The ID of the cattle to be updated.
    :return: The rendered HTTP response with the form or a redirect to the cattle information page.
    """
    cattle = get_object_or_404(Cattle, id=cattle_id) if cattle_id else None

    if request.method == 'POST':
        form = CattleForm(request.POST, request.FILES, instance=cattle)
        if form.is_valid():
            cattle = form.save(commit=False)
            herd_id = request.POST.get('herd')
            herd = Herd.objects.get(id=herd_id)
            cattle.herd = herd
            cattle.save()
            return redirect('my_farm:cattle_detail', cattle_id=cattle_id)
    else:
        form = CattleForm(instance=cattle)

    context = {'form': form, 'cattle': cattle}
    return render(request, 'cattle/update_cattle.html', context)


def cattle_detail(request, cattle_id=None):
    """
    Displays detailed information about a specific cattle.

    :param request: The HTTP request object.
    :param cattle_id: The ID of the cattle to display information about.
    :return: The rendered HTTP response with the cattle information.
    """
    cattle = get_object_or_404(Cattle, id=cattle_id) if cattle_id else None
    return render(request, 'cattle/cattle_detail.html', {'cattle': cattle})


def upload_cattle_picture(request, cattle_id):
    """
    Handles the uploading of a picture for a specific cattle.

    :param request: The HTTP request object.
    :param cattle_id: The ID of the cattle to upload a picture for.
    :return: The rendered HTTP response with the form or a redirect to the cattle information page.
    """
    cattle = get_object_or_404(Cattle, id=cattle_id)

    if request.method == 'POST':
        picture = request.FILES.get('picture')

        if picture:
            cattle.picture = picture
            cattle.save()
            return redirect('my_farm:cattle_detail', cattle_id=cattle_id)

    return render(request, 'my_farm/upload_picture.html')


class CattleDeleteView(DeleteView):
    """
    This class is responsible for deleting a cattle object. It inherits from the DeleteView class provided
    by the Django framework. Upon deletion, it redirects to the cattle_info page.

    """
    model = Cattle
    template_name = 'cattle/cattle_confirm_delete.html'
    success_url = reverse_lazy('my_farm:cattle_info')

    def get_object(self, queryset=None):
        """
        Retrieves the cattle object to be deleted. If the cattle object is already marked as deleted,
        it raises an Http404 exception.

        :param queryset: The queryset from which to retrieve the cattle object (default: None).
        :return: The cattle object to be deleted.
        :raises Http404: If the cattle object is already deleted.
        """
        obj = super().get_object(queryset=queryset)
        if obj.deleted:
            raise Http404("The cattle does not exist.")
        return obj

    def post(self, request, *args, **kwargs):
        """
        Handles the HTTP POST request for deleting the cattle object.
        It calls the delete() method on the cattle object and redirects to the success_url.

        :param request: The HTTP request object.
        :param args: Additional positional arguments.
        :param kwargs: Additional keyword arguments.
        :return: The HTTP response redirecting to the success_url.
        """
        self.object = self.get_object()
        self.object.delete()
        return HttpResponseRedirect(self.get_success_url())


def delete_confirmation_page(request):
    """
    Renders the confirmation_page.html template.

    :param request: The HTTP request object.
    :return: The rendered confirmation page.
    """
    return render(request, 'cattle/confirmation_page.html')