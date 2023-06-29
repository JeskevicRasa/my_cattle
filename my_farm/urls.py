from django.urls import path
# from .livestock_movement_report import LivestockMovementReportView
from .views import home, cattle_info, add_row, confirmation_page, update_cattle, search_cattle, \
    GenerateReportView, LivestockMovementReportView, CattleDeleteView

app_name = "my_farm"

urlpatterns = [
    path('', home, name='home'),
    path('cattle_info/', cattle_info, name='cattle_info'),
    path('add_row/', add_row, name='add_row'),
    path('update_cattle/<int:cattle_id>/', update_cattle, name='update_cattle'),
    # path('delete_row/<int:cattle_id>/', delete_row, name='delete_row'),
    path('cattle/delete/<int:cow_id>/', CattleDeleteView.as_view(), name='delete_cattle'),
    path('search_cattle/', search_cattle, name='search_cattle'),
    path('confirmation_page/', confirmation_page, name='confirmation_page'),
    path('generate_report/', GenerateReportView.as_view(), name='generate_report'),
    path('livestock_movement_report/', LivestockMovementReportView.as_view(), name='report'),
]


