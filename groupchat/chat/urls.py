from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('create/', views.create_room, name='create_room'),
    path('join/', views.join_room, name='join_room'),
    path('chat/<str:room_code>/', views.chat_room, name='chat_room'),
    path('summarize/', views.summarize_chat, name='summarize_chat'),
]
