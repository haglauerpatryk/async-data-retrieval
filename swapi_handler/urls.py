from django.urls import path
from . import views

app_name = "swapi_handler"

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('dataset_details/<int:dataset_id>/', views.dataset_details, name='dataset_details'),
    path('api/fetch_data/<int:dataset_id>/', views.fetch_data, name='fetch_data'),
    path('column_selection/<int:dataset_id>/', views.column_selection, name='column_selection'),
    path('api/count_occurrences/<int:dataset_id>/', views.count_occurrences, name='count_occurrences'),
    path('convert_and_download_csv/', views.convert_and_download_csv, name='convert_and_download_csv'),
]