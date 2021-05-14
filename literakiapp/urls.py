from django.urls import path
from . import views

app_name = 'literakiapp'

urlpatterns = [
    path('', views.index, name='index'),
    path('create/', views.create_game, name='create_game'),

    path('game/<str:game_token>/', views.game, name='game'),

    path('game/<str:game_token>/change_name', views.change_name, name='change_name'),
    path('game/<str:game_token>/ready', views.ready, name='ready'),
    path('game/<str:game_token>/leave', views.leave, name='leave'),
    path('game/<str:game_token>/kick_player', views.kick_player, name='kick_player'),

    path('game/<str:game_token>/place_letters', views.place_letters, name='place_letters'),
    path('game/<str:game_token>/exchange_letters', views.exchange_letters, name='exchange_letters'),
    path('game/<str:game_token>/vote', views.vote, name='vote'),
]
