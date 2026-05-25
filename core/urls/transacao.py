from django.urls import path
from core.views import TransacaoView

urlpatterns = [
    path('', TransacaoView.as_view()),
]