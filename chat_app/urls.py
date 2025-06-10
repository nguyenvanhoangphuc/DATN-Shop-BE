from django.urls import path
from .views import chat_proxy

urlpatterns = [
    path("chat", chat_proxy, name="chat-proxy"),
]
