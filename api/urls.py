from django.urls import path
from . import views

urlpatterns = [
    path('dataBun/', views.SubjectListView.as_view(), name='subject_list'),
    path('dataBun/<pk>/', views.SubjectDetailView.as_view(), name='subject_detail'),
    path('dataCtg/', views.SubjectListViewCtg.as_view(), name='subject_list_ctg'),
    path('dataCtg/<pk>/', views.SubjectDetailViewCtg.as_view(), name='subject_detail_ctg'),
    path('dataBar/', views.SubjectListViewBar.as_view(), name='subject_list_bar'),
    path('dataBar/<pk>/', views.SubjectDetailViewBar.as_view(), name='subject_detail_bar'),
]