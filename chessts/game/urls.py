from django.urls import path
from . import views

urlpatterns = [
    path('', views.play, name='board'),  # previously: views.index
    path('play/restart/', views.restart_game, name='restart'),
    path('play/switch/', views.switch_sides, name='switch'),
    path('play/score/', views.score_view, name='score'),
    path('play/autoplay/', views.auto_play, name='autoplay'),
    path("undo/", views.undo_move, name="undo"),
]
