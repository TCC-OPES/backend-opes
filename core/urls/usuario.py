from django.urls import path
from core.views import CadastroView

urlpatterns = [
    path('cadastro/', CadastroView.as_view()),
]