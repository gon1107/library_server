from django.urls import path

from book import views

urlpatterns = [
    path('delete_rental/<int:pk>/', views.delete_rental),
    path('<int:pk>/create_rental/', views.RentalCreate.as_view()),
    path('search/<str:q>/', views.BookSearch.as_view()),
    path('delete_review/<int:pk>/', views.delete_review),
    path('update_review/<int:pk>/', views.ReviewUpdate.as_view()),
    path('update_book/<int:pk>/', views.BookUpdate.as_view()),
    path('create_book/', views.BookCreate.as_view()),
    path('tag/<str:slug>/', views.tag_page),
    path('category/<str:slug>/', views.category_page),
    path('<int:pk>/new_review/', views.new_review),
    path('<int:pk>/', views.BookDetail.as_view()),
    path('', views.BookList.as_view()),
]