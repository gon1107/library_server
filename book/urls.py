from django.urls import path

from book import views

urlpatterns = [
    path('tag/<str:slug>/', views.tag_page),
    path('category/<str:slug>/', views.category_page),
    path('<int:pk>/', views.BookDetail.as_view()),
    path('', views.BookList.as_view()),
]