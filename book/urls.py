from django.urls import path

from book import views

urlpatterns = [
    path('<int:pk>/', views.single_book_page),
    path('', views.index),
]