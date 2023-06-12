from django.shortcuts import render
from django.contrib.auth.forms import AuthenticationForm


def main(request):
    form = AuthenticationForm()
    return render(request, 'main.html', {'form': form})
