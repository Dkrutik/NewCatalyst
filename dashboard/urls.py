from django.urls import path,include
from . import views

urlpatterns = [
    path('', views.login),
    path('upload-data/', views.upload_data_view, name='upload-data'),
    path('query-builder/', views.query_builder, name='query-builder'),
    path('users/', views.users, name='users'),
    path('api/upload/<str:task_id>/',views.ChunkedUploadView.as_view(), name = 'upload_api'),
    path('api/fetch/industries/', views.industries_get, name='industries_get'),
    path('api/fetch/companies/', views.query_data, name='industries_get'),
]
