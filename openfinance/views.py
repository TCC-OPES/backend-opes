from decimal import Decimal, InvalidOperation

import requests
from django.db import transaction
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from openfinance.models import ConexaoBancaria, TransacaoImportada
from openfinance.pluggy import (
    buscar_contas,
    buscar_item,
    buscar_transacoes,
    criar_connect_token,
    obter_api_key,
)


class ConnectTokenView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        item_id = request.data.get("itemId")
        if item_id and not ConexaoBancaria.objects.filter(item_id=item_id, user=request.user).exists():
            return Response({"detail": "Conexão não encontrada."}, status=status.HTTP_404_NOT_FOUND)
        try:
            api_key = obter_api_key()
            token = criar_connect_token(api_key, request.user.pk, item_id)
            return Response({"accessToken": token})
        except (requests.RequestException, ValueError, KeyError):
            return Response({"detail": "Não foi possível iniciar a conexão bancária."}, status=status.HTTP_502_BAD_GATEWAY)


class SalvarConexaoView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        item_id = request.data.get("itemId")
        if not item_id:
            return Response({"detail": "itemId é obrigatório."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            item = buscar_item(obter_api_key(), item_id)
        except (requests.RequestException, ValueError, KeyError):
            return Response({"detail": "Não foi possível confirmar a conexão bancária."}, status=status.HTTP_502_BAD_GATEWAY)

        if str(item.get("clientUserId")) != str(request.user.pk):
            return Response({"detail": "Esta conexão não pertence ao usuário."}, status=status.HTTP_403_FORBIDDEN)

        conexao = ConexaoBancaria.objects.filter(item_id=item_id).first()
        if conexao and conexao.user_id != request.user.pk:
            return Response({"detail": "Esta conexão já pertence a outro usuário."}, status=status.HTTP_403_FORBIDDEN)
        if not conexao:
            conexao = ConexaoBancaria(item_id=item_id, user=request.user)
        conector = item.get("connector") or {}
        conexao.instituicao_nome = conector.get("name") or conexao.instituicao_nome
        conexao.save()
        return Response({"status": "sucesso", "item_id": conexao.item_id})


class ConexoesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response([
            {"item_id": conexao.item_id, "instituicao_nome": conexao.instituicao_nome}
            for conexao in ConexaoBancaria.objects.filter(user=request.user).order_by("-criado_em")
        ])


class SincronizarTransacoesView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        item_id = request.data.get("itemId")
        if not item_id:
            return Response({"detail": "itemId é obrigatório."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            conexao = ConexaoBancaria.objects.get(item_id=item_id, user=request.user)
        except ConexaoBancaria.DoesNotExist:
            return Response({"detail": "Conexão não encontrada."}, status=status.HTTP_404_NOT_FOUND)

        try:
            api_key = obter_api_key()
            item = buscar_item(api_key, item_id)
        except (requests.RequestException, ValueError, KeyError):
            return Response({"detail": "Não foi possível consultar a instituição."}, status=status.HTTP_502_BAD_GATEWAY)

        if str(item.get("clientUserId")) != str(request.user.pk):
            return Response({"detail": "Esta conexão não pertence ao usuário."}, status=status.HTTP_403_FORBIDDEN)

        if item.get("status") != "UPDATED":
            return Response(
                {"detail": "A conexão ainda está sincronizando na Pluggy. Tente novamente em alguns instantes."},
                status=status.HTTP_409_CONFLICT,
            )

        try:
            contas = buscar_contas(api_key, item_id)
            registros = [t for conta in contas for t in buscar_transacoes(api_key, conta["id"])]
        except (requests.RequestException, ValueError, KeyError):
            return Response({"detail": "Falha ao consultar as transações bancárias."}, status=status.HTTP_502_BAD_GATEWAY)
        novas_transacoes = 0

        try:
            with transaction.atomic():
                for t in registros:
                    valor = abs(Decimal(str(t["amount"])))
                    tipo = t.get("type")
                    if tipo not in ("CREDIT", "DEBIT"):
                        continue
                    categoria = t.get("category")
                    if isinstance(categoria, dict):
                        categoria = categoria.get("name")
                    _, created = TransacaoImportada.objects.update_or_create(
                        external_id=t["id"],
                        defaults={
                            "conexao": conexao,
                            "descricao": (t.get("description") or "Sem descrição")[:255],
                            "valor": valor,
                            "data": t["date"],
                            "categoria": (categoria or "Sem categoria")[:100],
                            "tipo": "receita" if tipo == "CREDIT" else "despesa",
                        },
                    )
                    if created:
                        novas_transacoes += 1
        except (KeyError, InvalidOperation, ValueError):
            return Response({"detail": "A instituição retornou uma transação inválida."}, status=status.HTTP_502_BAD_GATEWAY)

        return Response({"status": "sucesso", "novas_transacoes": novas_transacoes})
