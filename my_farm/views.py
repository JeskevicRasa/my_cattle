from django.http import HttpResponse


def home(request):
    return HttpResponse("Hello, you are in my farm yeay")


def cattle_info(request):
    return HttpResponse("Hello, here is going to be all cattle info")