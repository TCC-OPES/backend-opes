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
        try:
            api_key = obter_api_key()
            item_id = request.data.get("itemId")
            token = criar_connect_token(api_key, item_id)
            return Response({"accessToken": token})
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class SalvarConexaoView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        item_id = request.data.get("itemId")
        if not item_id:
            return Response({"detail": "itemId é obrigatório."}, status=status.HTTP_400_BAD_REQUEST)

        conexao, _ = ConexaoBancaria.objects.get_or_create(
            item_id=item_id, defaults={"user": request.user}
        )
        return Response({"status": "sucesso", "item_id": conexao.item_id})


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

        api_key = obter_api_key()
        item = buscar_item(api_key, item_id)

        if item.get("status") != "UPDATED":
            return Response(
                {"detail": "A conexão ainda está sincronizando na Pluggy. Tente novamente em alguns instantes."},
                status=status.HTTP_409_CONFLICT,
            )

        contas = buscar_contas(api_key, item_id)
        novas_transacoes = 0

        for conta in contas:
            transacoes = buscar_transacoes(api_key, conta["id"])
            for t in transacoes:
                _, created = TransacaoImportada.objects.get_or_create(
                    external_id=t["id"],
                    defaults={
                        "conexao": conexao,
                        "descricao": t.get("description", "Sem descrição"),
                        "valor": t.get("amount", 0.0),
                        "data": t.get("date"),
                        "categoria": t.get("category"),
                        "tipo": t.get("type"),
                    },
                )
                if created:
                    novas_transacoes += 1

        return Response({"status": "sucesso", "novas_transacoes": novas_transacoes})