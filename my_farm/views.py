from django.http import HttpResponse


def home(request):
    return HttpResponse("Hello, you are in my farm yeay")