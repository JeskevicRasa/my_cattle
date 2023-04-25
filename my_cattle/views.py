from django.shortcuts import render
from django.http import HttpResponse


def main(request):
    return HttpResponse("Hello, world. You're at the main page.")
    # render(request=request, template_name='home.html')
