from django.shortcuts import render
from django.contrib.auth.forms import AuthenticationForm


def main(request):
    """
    View function to render the main page of the application.

    :param request: The HTTP request object.
    :return: Rendered main template with the authentication form.
    """
    form = AuthenticationForm()
    return render(request, 'main.html', {'form': form})
