from django.urls import path

from single_pages import views

urlpatterns=[
    path('book_detail/', views.book_detail),
    path('', views.landing),
]