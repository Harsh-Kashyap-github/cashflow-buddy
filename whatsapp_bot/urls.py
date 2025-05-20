from django.urls import path
from .views import whatsAppBotResponce

urlpatterns = [
    path('whatsapp/',whatsAppBotResponce,name='whatsapp_bot_responce')
]
