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
    DashboardView,
    InvestimentoView  # 1. Adicionado aqui
)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    path('api/cadastro/', CadastroView.as_view(), name='cadastro'),
    path('api/login/', LoginView.as_view(), name='login'),
    path('api/me/', MeView.as_view(), name='me'),
    path('api/user/foto/', AtualizarFotoPerfilView.as_view(), name='atualizar_foto'),
    
    path('api/cartoes/', CartaoView.as_view(), name='cartoes'),
    path('api/dashboard/', DashboardView.as_view(), name='dashboard'),
    path('api/familias/', FamiliaView.as_view(), name='familias'),
    path('api/metas/', MetaFinanceiraView.as_view(), name='metas'),
    path('api/metas/<int:pk>/', MetaFinanceiraView.as_view(), name='meta_detail'),
    path('api/transacoes/', TransacaoView.as_view(), name='transacoes'),
    
    # 2. Rotas de Investimentos (Listar/Criar e Atualizar/Deletar por ID)
    path('api/investimentos/', InvestimentoView.as_view(), name='investimentos'),
    path('api/investimentos/<int:pk>/', InvestimentoView.as_view(), name='investimento_detail'),
]