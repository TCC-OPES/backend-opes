from django.contrib import admin
from django.urls import include, path

from core.views import (
    AtualizarFotoPerfilView,
    CadastroView,
    CartaoView,
    DashboardView,
    FamiliaView,
    InvestimentoView,  # 1. Adicionado aqui
    LoginView,
    MetaFinanceiraView,
    MeView,
    TransacaoView,
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
    path('api/investimentos/', InvestimentoView.as_view(), name='investimentos'),
    path('api/investimentos/<int:pk>/', InvestimentoView.as_view(), name='investimento_detail'),
    path('api/openfinance/', include('openfinance.urls')),  
    path('api/cadastro/', CadastroView.as_view(), name='cadastro'),
]
