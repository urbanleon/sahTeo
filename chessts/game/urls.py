from django.urls import path

from . import views

urlpatterns = [
    path('', views.play, name='play'),
    path('getMove/', views.getMove, name='get-move')
]