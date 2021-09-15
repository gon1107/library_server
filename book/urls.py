from django.urls import path

from book import views

urlpatterns = [
    path('<int:pk>/', views.BookDetail.as_view()),
    path('', views.BookList.as_view()),
]