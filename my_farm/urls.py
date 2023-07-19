
from django.urls import path
from .views import home, group_data
from .views_herd import herd_list, add_herd, herd_detail, cattle_list_by_herd, search_herd, update_herd, \
    upload_herd_picture
from .views_movement_report import GenerateReportView, LivestockMovementReportView
from .views_field import field_list, field_detail, herd_list_by_field, update_field, add_field, upload_field_picture, \
    search_field
from .views_cattle import cattle_info, add_cattle, update_cattle, search_cattle, cattle_detail, \
    delete_confirmation_page, CattleDeleteView, upload_cattle_picture


app_name = "my_farm"

urlpatterns = [

    path('', home, name='home'),
    path('group_data/<slug:group_name>/', group_data, name='group_data'),

    path('generate_report/', GenerateReportView.as_view(), name='generate_report'),
    path('livestock_movement_report/', LivestockMovementReportView.as_view(), name='report'),
    path('livestock_movement_report/last_reports/', LivestockMovementReportView.as_view(), {'last_reports': True},
         name='last_reports'),

    path('cattle_info/', cattle_info, name='cattle_info'),
    path('cattle/<int:cattle_id>/', cattle_detail, name='cattle_detail'),
    path('add_cattle/', add_cattle, name='add_cattle'),
    path('update_cattle/<int:cattle_id>/', update_cattle, name='update_cattle'),
    path('upload_cattle_picture/<int:cattle_id>/', upload_cattle_picture, name='upload_cattle_picture'),
    path('cattle/delete/<int:pk>/', CattleDeleteView.as_view(), name='delete_cattle'),
    path('confirmation_page/', delete_confirmation_page, name='delete_confirmation_page'),
    path('search_cattle/', search_cattle, name='search_cattle'),

    path('herds/', herd_list, name='herd_list'),
    path('herds/<int:herd_id>/', herd_detail, name='herd_detail'),
    path('herds/new_herd', add_herd, name='add_herd'),
    path('herd/<int:herd_id>/cattle/', cattle_list_by_herd, name='cattle_list_by_herd'),
    path('herd/update_herd/<int:herd_id>/', update_herd, name='update_herd'),
    path('herd/upload_herd_picture/<int:herd_id>/', upload_herd_picture, name='upload_herd_picture'),
    path('search_herd/', search_herd, name='search_herd'),

    path('fields/', field_list, name='field_list'),
    path('fields/<int:field_id>/', field_detail, name='field_detail'),
    path('fields/new_field', add_field, name='add_field'),
    path('fields/<int:field_id>/herd/', herd_list_by_field, name='herd_list_by_field'),
    path('fields/update_field/<int:field_id>/', update_field, name='update_field'),
    path('fields/upload_field_picture/<int:field_id>/', upload_field_picture, name='upload_field_picture'),
    path('fields/search_field/', search_field, name='search_field')


]
