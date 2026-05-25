from django.urls import path

from core.views import CartaoView

urlpatterns = [
    path('', CartaoView.as_view()),
]