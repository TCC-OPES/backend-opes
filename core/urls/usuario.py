from django.urls import path
from core.views import CadastroView, LoginView, MeView

urlpatterns = [
    path('cadastro/', CadastroView.as_view()),
    path('login/', LoginView.as_view()),
    path('me/', MeView.as_view()),
]