from django.urls import path

from single_pages import views

urlpatterns = [
    path('search/', views.search),
    path('info/', views.info),
    path('', views.index),
]