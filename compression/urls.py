from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('results/', views.all_results, name='all_results'),
    path('results/<int:result_id>/', views.compression_results, name='compression_results'),
    path('download/<int:file_id>/', views.download_compressed_file, name='download_compressed_file'),
    path('progress/<int:file_id>/', views.compression_progress, name='compression_progress'),
]
