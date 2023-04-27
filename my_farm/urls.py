from django.urls import path
from .views import home, cattle_info

app_name = "my_farm"

urlpatterns = [
    path('', home, name='home'),
    path('cattle_info/', cattle_info, name='cattleinfo'),

]