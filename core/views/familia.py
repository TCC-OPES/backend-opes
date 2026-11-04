from django.db.models import Q
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.models import ConviteFamilia, Familia, MembroFamilia, User
from core.serializers import ConviteFamiliaSerializer, FamiliaSerializer, MembroFamiliaSerializer


class FamiliaView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        familias = Familia.objects.filter(
            Q(criador=request.user) | Q(membros__usuario=request.user)
        ).distinct().order_by('id')
        serializer = FamiliaSerializer(familias, many=True)
        return Response(serializer.data)

    def post(self, request):
        nome = (request.data.get('nome') or '').strip()
        if not nome:
            return Response({'nome': ['Informe o nome da família.']}, status=400)

        familia = Familia.objects.create(nome=nome, criador=request.user)
        MembroFamilia.objects.create(familia=familia, usuario=request.user, papel='admin')
        return Response(FamiliaSerializer(familia).data, status=201)


class FamiliaMembrosView(APIView):
    permission_classes = [IsAuthenticated]

    def _get_familia(self, request, familia_id, require_admin=False):
        try:
            familia = Familia.objects.get(id=familia_id)
        except Familia.DoesNotExist:
            raise NotFound('Família não encontrada.')

        is_member = familia.criador == request.user or familia.membros.filter(usuario=request.user).exists()
        if not is_member:
            raise PermissionDenied('Você não pertence a esta família.')

        if require_admin and not (
            familia.criador == request.user or familia.membros.filter(usuario=request.user, papel='admin').exists()
        ):
            raise PermissionDenied('Você precisa ser administrador da família.')

        return familia

    def get(self, request, familia_id):
        familia = self._get_familia(request, familia_id)
        membros = familia.membros.select_related('usuario').all().order_by('id')
        return Response(MembroFamiliaSerializer(membros, many=True).data)

    def post(self, request, familia_id):
        familia = self._get_familia(request, familia_id, require_admin=True)
        email = (request.data.get('email') or '').strip()
        papel = (request.data.get('papel') or 'membro').strip().lower()

        if not email:
            return Response({'email': ['Informe o e-mail da pessoa.']}, status=400)

        if papel not in {'membro', 'dependente'}:
            return Response({'papel': ['Função inválida.']}, status=400)

        usuario = User.objects.filter(email__iexact=email).first()
        if not usuario:
            return Response({'email': ['Usuário não encontrado.']}, status=404)

        if usuario == request.user or familia.membros.filter(usuario=usuario).exists():
            return Response({'erro': 'Este usuário já participa da família ou é você mesmo.'}, status=400)

        convite_existente = ConviteFamilia.objects.filter(
            familia=familia,
            convidado=usuario,
            status='pendente'
        ).exists()
        if convite_existente:
            return Response({'erro': 'Já existe um convite pendente para esse e-mail.'}, status=400)

        convite = ConviteFamilia.objects.create(
            familia=familia,
            convidado=usuario,
            convidado_por=request.user,
            papel=papel,
            status='pendente'
        )
        return Response(ConviteFamiliaSerializer(convite).data, status=201)


class FamiliaMembroDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, familia_id, pk):
        try:
            familia = Familia.objects.get(id=familia_id)
        except Familia.DoesNotExist:
            raise NotFound('Família não encontrada.')

        is_member = familia.criador == request.user or familia.membros.filter(usuario=request.user).exists()
        if not is_member:
            raise PermissionDenied('Você não pertence a esta família.')

        membro = familia.membros.filter(id=pk).first()
        if not membro:
            raise NotFound('Membro não encontrado.')

        is_admin = familia.criador == request.user or familia.membros.filter(usuario=request.user, papel='admin').exists()
        if request.user != membro.usuario and not is_admin:
            raise PermissionDenied('Você não pode remover este membro.')

        membro.delete()
        return Response(status=204)


class FamiliaConvitesEnviadosView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, familia_id):
        try:
            familia = Familia.objects.get(id=familia_id)
        except Familia.DoesNotExist:
            raise NotFound('Família não encontrada.')

        if familia.criador != request.user and not familia.membros.filter(usuario=request.user, papel='admin').exists():
            raise PermissionDenied('Você precisa ser administrador para visualizar os convites desta família.')

        convites = ConviteFamilia.objects.filter(
            familia=familia,
            status='pendente'
        ).order_by('-criado_em')
        return Response(ConviteFamiliaSerializer(convites, many=True).data)


class FamiliaConviteDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, familia_id, pk):
        try:
            familia = Familia.objects.get(id=familia_id)
        except Familia.DoesNotExist:
            raise NotFound('Família não encontrada.')

        if familia.criador != request.user and not familia.membros.filter(usuario=request.user, papel='admin').exists():
            raise PermissionDenied('Você precisa ser administrador para cancelar este convite.')

        convite = familia.convites.filter(id=pk).first()
        if not convite:
            raise NotFound('Convite não encontrado.')

        convite.status = 'cancelado'
        convite.save(update_fields=['status'])
        return Response({'status': 'cancelado'}, status=200)


class FamiliasConvitesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        convites = ConviteFamilia.objects.filter(
            convidado=request.user,
            status='pendente'
        ).order_by('-criado_em')
        return Response(ConviteFamiliaSerializer(convites, many=True).data)


class ResponderConviteView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            convite = ConviteFamilia.objects.get(id=pk)
        except ConviteFamilia.DoesNotExist:
            raise NotFound('Convite não encontrado.')

        if convite.convidado != request.user:
            raise PermissionDenied('Este convite não foi enviado para você.')

        acao = (request.data.get('acao') or '').strip().lower()
        if acao not in {'aceitar', 'recusar'}:
            return Response({'erro': 'Ação inválida.'}, status=400)

        if acao == 'aceitar':
            MembroFamilia.objects.get_or_create(
                familia=convite.familia,
                usuario=request.user,
                defaults={'papel': convite.papel}
            )
            convite.status = 'aceito'
            convite.save(update_fields=['status'])
            return Response({'mensagem': 'Você entrou na família!'}, status=200)

        convite.status = 'recusado'
        convite.save(update_fields=['status'])
        return Response({'mensagem': 'Convite recusado.'}, status=200)
