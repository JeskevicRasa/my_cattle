from django.urls import path
from .views import home

app_name = "my_farm"

urlpatterns = [
    path('', home, name='home'),

]