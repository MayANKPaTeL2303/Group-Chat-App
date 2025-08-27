# urls.py
from django.urls import path
from . import views

urlpatterns = [
    # ===== EXISTING TEMPLATE VIEWS (Keep for backward compatibility) =====
    path('', views.home, name='home'),
    path('create/', views.create_room, name='create_room'),
    path('join/', views.join_room, name='join_room'),
    path('chat/<str:room_code>/', views.chat_room, name='chat_room'),
    path('browse-rooms/', views.browse_rooms, name='browse_rooms'),
    path('summarize/', views.summarize_chat, name='summarize_chat'),
    path('update-user-activity/', views.update_user_activity, name='update_user_activity'),

]