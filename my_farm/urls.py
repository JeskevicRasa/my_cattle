from django.urls import path
# from .livestock_movement_report import LivestockMovementReportView
from .views import home, cattle_info, add_row, confirmation_page, update_cattle, search_cattle, \
    GenerateReportView, LivestockMovementReportView, CattleDeleteView, one_cattle_info, upload_picture, generate_pdf

app_name = "my_farm"

urlpatterns = [
    path('', home, name='home'),
    path('cattle_info/', cattle_info, name='cattle_info'),
    path('one_cattle_info/<int:cattle_id>/', one_cattle_info, name='one_cattle_info'),
    path('upload_picture/<int:cattle_id>/', upload_picture, name='upload_picture'),
    path('add_row/', add_row, name='add_row'),
    path('update_cattle/<int:cattle_id>/', update_cattle, name='update_cattle'),
    path('cattle/delete/<int:pk>/', CattleDeleteView.as_view(), name='delete_cattle'),
    path('search_cattle/', search_cattle, name='search_cattle'),
    path('confirmation_page/', confirmation_page, name='confirmation_page'),
    path('generate_report/', GenerateReportView.as_view(), name='generate_report'),
    path('livestock_movement_report/', LivestockMovementReportView.as_view(), name='report'),
    path('livestock_movement_report/last_reports/', LivestockMovementReportView.as_view(), {'last_reports': True},
         name='last_reports'),
    path('generate_pdf/', generate_pdf, name='generate_pdf'),
]
