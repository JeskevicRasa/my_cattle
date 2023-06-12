from django.urls import path
from .views import home, cattle_info, add_row, delete_row, confirmation_page, update_cattle, search_cattle


app_name = "my_farm"

urlpatterns = [
    path('', home, name='home'),
    path('cattle_info/', cattle_info, name='cattle_info'),
    path('add_row/', add_row, name='add_row'),
    path('update_cattle/<int:cattle_id>/', update_cattle, name='update_cattle'),
    path('delete_row/<int:cattle_id>/', delete_row, name='delete_row'),
    path('search_cattle/', search_cattle, name='search_cattle'),
    path('confirmation_page/', confirmation_page, name='confirmation_page'),


]