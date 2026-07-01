from django.contrib import admin
from django.urls import path
from core.views import (
    CadastroView,
    AtualizarFotoPerfilView,
    LoginView,
    MeView,
    TransacaoView,
    CartaoView,
    FamiliaView,
    MetaFinanceiraView,
    DashboardView
)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Rotas de Autenticação e Usuário
    path('api/cadastro/', CadastroView.as_view(), name='cadastro'),
    path('api/login/', LoginView.as_view(), name='login'),
    path('api/me/', MeView.as_view(), name='me'),
    path('api/user/foto/', AtualizarFotoPerfilView.as_view(), name='atualizar_foto'),
    
    # Rotas do Sistema
    path('api/cartoes/', CartaoView.as_view(), name='cartoes'),
    path('api/dashboard/', DashboardView.as_view(), name='dashboard'),
    path('api/familias/', FamiliaView.as_view(), name='familias'),
    path('api/metas/', MetaFinanceiraView.as_view(), name='metas'),
    path('api/transacoes/', TransacaoView.as_view(), name='transacoes'),
]