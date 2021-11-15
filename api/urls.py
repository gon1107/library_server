from django.urls import path

from api import views

urlpatterns = [
    path('dht/', views.DHTView.as_view()),
    path('test/', views.TestView.as_view()),
]