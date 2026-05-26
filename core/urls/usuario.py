from django.urls import path
# Importações diretas e seguras para o Django não se perder
from core.views.usuario import CadastroView, AtualizarFotoPerfilView
from core.views import LoginView, MeView

urlpatterns = [
    # Rotas originais do seu sistema que fazem o login funcionar
    path('cadastro/', CadastroView.as_view()),
    path('login/', LoginView.as_view()),
    path('me/', MeView.as_view()),
    
    # Nova rota da foto de perfil
    path('perfil/foto/', AtualizarFotoPerfilView.as_view()),
]