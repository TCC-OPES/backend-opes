from django.urls import path

from openfinance.views import ConnectTokenView, SalvarConexaoView, SincronizarTransacoesView

urlpatterns = [
    path("connect-token/", ConnectTokenView.as_view(), name="connect_token"),
    path("salvar-conexao/", SalvarConexaoView.as_view(), name="salvar_conexao"),
    path("sincronizar/", SincronizarTransacoesView.as_view(), name="sincronizar"),
]