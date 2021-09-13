from django.urls import path

from book import views

urlpatterns = [
    path('<int:pk>/', views.book_detail),
    path('', views.book_list),
]