from django.urls import path

from book import views

urlpatterns = [
    path('update_book/<int:pk>/', views.BookUpdate.as_view()),
    path('create_book/', views.BookCreate.as_view()),
    path('tag/<str:slug>/', views.tag_page),
    path('category/<str:slug>/', views.category_page),
    path('<int:pk>/', views.BookDetail.as_view()),
    path('', views.BookList.as_view()),
]