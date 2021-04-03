from django.urls import path
from . import views

app_name = 'literakiapp'

urlpatterns = [
    path('', views.index, name='index'),
    path('create/', views.create_game, name='create_game'),
    path('<str:game_token>/', views.game, name='game'),
]
