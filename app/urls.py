from core.views.recorrencia import RecorrenciaView, OcorrenciaView, ConfirmarOcorrenciaView
from rest_framework_simplejwt.views import TokenRefreshView
from django.http import JsonResponse
from django.contrib import admin
from django.urls import include, path

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)
from core.views import (
    AtualizarFotoPerfilView,
    CadastroView,
    CartaoView,
    DashboardView,
    FamiliaView,
    InvestimentoView,
    LoginView,
    MetaFinanceiraView,
    MeView,
    TransacaoView,
)


urlpatterns = [
    # Administração
    path('api/health/', lambda request: JsonResponse({'status': 'ok', 'features': ['recorrencias', 'calendario', 'simulador'], 'api_version': 'opes-financeiro-v2'}), name='api-health'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/recorrencias/', RecorrenciaView.as_view(), name='recorrencias'),
    path('api/recorrencias/<int:pk>/', RecorrenciaView.as_view(), name='recorrencia-detail'),
    path('api/recorrencias/ocorrencias/', OcorrenciaView.as_view(), name='recorrencias-ocorrencias'),
    path('api/recorrencias/ocorrencias/<int:pk>/confirmar/', ConfirmarOcorrenciaView.as_view(), name='recorrencia-confirmar'),
    path('admin/', admin.site.urls),

    # Documentação da API - Swagger / OpenAPI
    path(
        'api/schema/',
        SpectacularAPIView.as_view(),
        name='schema'
    ),
    path(
        'api/docs/',
        SpectacularSwaggerView.as_view(url_name='schema'),
        name='swagger-ui'
    ),
    path(
        'api/doc/',
        SpectacularSwaggerView.as_view(url_name='schema'),
        name='swagger-ui-alias'
    ),
    path(
        'api/redoc/',
        SpectacularRedocView.as_view(url_name='schema'),
        name='redoc'
    ),

    # Autenticação e usuários
    path('api/cadastro/', CadastroView.as_view(), name='cadastro'),
    path('api/login/', LoginView.as_view(), name='login'),
    path('api/me/', MeView.as_view(), name='me'),
    path(
        'api/user/foto/',
        AtualizarFotoPerfilView.as_view(),
        name='atualizar_foto'
    ),

    # Cartões
    path(
        'api/cartoes/',
        CartaoView.as_view(),
        name='cartoes'
    ),
    path(
        'api/cartoes/<int:pk>/',
        CartaoView.as_view(),
        name='cartao-detail'
    ),

    # Dashboard
    path(
        'api/dashboard/',
        DashboardView.as_view(),
        name='dashboard'
    ),

    # Famílias
    path(
        'api/familias/',
        FamiliaView.as_view(),
        name='familias'
    ),

    # Metas financeiras
    path(
        'api/metas/',
        MetaFinanceiraView.as_view(),
        name='metas'
    ),
    path(
        'api/metas/<int:pk>/',
        MetaFinanceiraView.as_view(),
        name='meta_detail'
    ),

    # Transações
    path(
        'api/transacoes/',
        TransacaoView.as_view(),
        name='transacoes'
    ),

    # Investimentos
    path(
        'api/investimentos/',
        InvestimentoView.as_view(),
        name='investimentos'
    ),
    path(
        'api/investimentos/<int:pk>/',
        InvestimentoView.as_view(),
        name='investimento_detail'
    ),

    # Open Finance
    path(
        'api/openfinance/',
        include('openfinance.urls')
    ),
    path('api/transacoes/',
        TransacaoView.as_view(), name='transacoes'),

    path(
    'api/transacoes/<int:pk>/',
    TransacaoView.as_view(),
    name='transacao-detail'
),
    path('api/user/foto/', AtualizarFotoPerfilView.as_view(), name='atualizar_foto'),
    path('api/cartoes/', CartaoView.as_view(), name='cartoes'),
    path('api/dashboard/', DashboardView.as_view(), name='dashboard'),
    path('api/familias/', FamiliaView.as_view(), name='familias'),
    path('api/metas/', MetaFinanceiraView.as_view(), name='metas'),
    path('api/metas/<int:pk>/', MetaFinanceiraView.as_view(), name='meta_detail'),
    path('api/transacoes/', TransacaoView.as_view(), name='transacoes'),
    path('api/investimentos/', InvestimentoView.as_view(), name='investimentos'),
    path('api/investimentos/<int:pk>/', InvestimentoView.as_view(), name='investimento_detail'),
    path('api/cadastro/', CadastroView.as_view(), name='cadastro'),
]
