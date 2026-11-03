from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.models import Familia, MembroFamilia, ConviteFamilia
from core.serializers.familia import (
    FamiliaSerializer, MembroFamiliaSerializer, ConviteFamiliaSerializer,
    EnviarConviteFamiliaSerializer,
)


def familias_do_usuario(usuario):
    return Familia.objects.filter(
        Q(criador=usuario) | Q(membros__usuario=usuario)
    ).distinct()


def familia_acessivel(usuario, familia_id):
    return get_object_or_404(familias_do_usuario(usuario), pk=familia_id)


def administrador(usuario, familia):
    return familia.criador_id == usuario.pk or MembroFamilia.objects.filter(
        familia=familia, usuario=usuario, papel='admin'
    ).exists()


class FamiliaView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        familias = familias_do_usuario(request.user).prefetch_related(
            'membros__usuario', 'despesas__pago_por'
        ).order_by('-criado_em')
        return Response(FamiliaSerializer(familias, many=True).data)

    @transaction.atomic
    def post(self, request):
        serializer = FamiliaSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        familia = serializer.save(criador=request.user)
        MembroFamilia.objects.get_or_create(
            familia=familia, usuario=request.user, defaults={'papel': 'admin'}
        )
        return Response(FamiliaSerializer(familia).data, status=status.HTTP_201_CREATED)


class FamiliaMembrosView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, familia_id):
        familia = familia_acessivel(request.user, familia_id)
        membros = MembroFamilia.objects.filter(familia=familia).select_related('usuario')
        return Response(MembroFamiliaSerializer(membros, many=True).data)

    def post(self, request, familia_id):
        familia = familia_acessivel(request.user, familia_id)
        if not administrador(request.user, familia):
            return Response({'detail': 'Somente administradores podem convidar membros.'},
                            status=status.HTTP_403_FORBIDDEN)
        serializer = EnviarConviteFamiliaSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email'].strip()
        usuario = get_user_model().objects.filter(email__iexact=email, is_active=True).first()
        if not usuario:
            return Response({'detail': 'Conta não encontrada ou indisponível.'},
                            status=status.HTTP_404_NOT_FOUND)
        if usuario.pk == request.user.pk:
            return Response({'detail': 'Você já faz parte desta família.'},
                            status=status.HTTP_400_BAD_REQUEST)
        if usuario.pk == familia.criador_id or MembroFamilia.objects.filter(
            familia=familia, usuario=usuario
        ).exists():
            return Response({'detail': 'Este usuário já faz parte da família.'},
                            status=status.HTTP_409_CONFLICT)
        if ConviteFamilia.objects.filter(
            familia=familia, usuario=usuario, status=ConviteFamilia.PENDENTE
        ).exists():
            return Response({'detail': 'Já existe um convite pendente para este e-mail.'},
                            status=status.HTTP_409_CONFLICT)
        try:
            with transaction.atomic():
                convite = ConviteFamilia.objects.create(
                    familia=familia, usuario=usuario, convidado_por=request.user,
                    papel=serializer.validated_data['papel']
                )
        except IntegrityError:
            return Response({'detail': 'Já existe um convite pendente para este e-mail.'},
                            status=status.HTTP_409_CONFLICT)
        return Response(ConviteFamiliaSerializer(convite).data,
                        status=status.HTTP_201_CREATED)


class FamiliaMembroDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def delete(self, request, familia_id, membro_id):
        familia = familia_acessivel(request.user, familia_id)
        membro = get_object_or_404(
            MembroFamilia.objects.select_for_update(), pk=membro_id, familia=familia
        )
        if not administrador(request.user, familia) and membro.usuario_id != request.user.pk:
            return Response({'detail': 'Sem permissão para remover este membro.'},
                            status=status.HTTP_403_FORBIDDEN)
        if membro.usuario_id == familia.criador_id:
            return Response({'detail': 'O criador da família não pode ser removido.'},
                            status=status.HTTP_400_BAD_REQUEST)
        # O criador permanece administrador, mesmo após outros membros saírem.
        membro.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class MeusConvitesFamiliaView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        convites = ConviteFamilia.objects.filter(
            usuario=request.user, status=ConviteFamilia.PENDENTE
        ).select_related('familia', 'convidado_por', 'usuario')
        return Response(ConviteFamiliaSerializer(convites, many=True).data)


class ResponderConviteFamiliaView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request, convite_id):
        convite = get_object_or_404(
            ConviteFamilia.objects.select_for_update().select_related('familia'),
            pk=convite_id, usuario=request.user
        )
        if convite.status != ConviteFamilia.PENDENTE:
            return Response({'detail': 'Este convite já foi respondido ou cancelado.'},
                            status=status.HTTP_409_CONFLICT)
        acao = request.data.get('acao')
        if acao not in ('aceitar', 'recusar'):
            return Response({'acao': ['Use "aceitar" ou "recusar".']},
                            status=status.HTTP_400_BAD_REQUEST)
        if acao == 'aceitar':
            if MembroFamilia.objects.filter(
                familia=convite.familia, usuario=request.user
            ).exists():
                return Response({'detail': 'Você já pertence a esta família.'},
                                status=status.HTTP_409_CONFLICT)
            MembroFamilia.objects.create(
                familia=convite.familia, usuario=request.user, papel=convite.papel
            )
            convite.status = ConviteFamilia.ACEITO
        else:
            convite.status = ConviteFamilia.RECUSADO
        convite.respondido_em = timezone.now()
        convite.save(update_fields=['status', 'respondido_em'])
        return Response(ConviteFamiliaSerializer(convite).data)


class CancelarConviteFamiliaView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def delete(self, request, familia_id, convite_id):
        familia = familia_acessivel(request.user, familia_id)
        if not administrador(request.user, familia):
            return Response({'detail': 'Somente administradores podem cancelar convites.'},
                            status=status.HTTP_403_FORBIDDEN)
        convite = get_object_or_404(
            ConviteFamilia.objects.select_for_update(),
            pk=convite_id, familia=familia, status=ConviteFamilia.PENDENTE
        )
        convite.status = ConviteFamilia.CANCELADO
        convite.respondido_em = timezone.now()
        convite.save(update_fields=['status', 'respondido_em'])
        return Response(status=status.HTTP_204_NO_CONTENT)


class FamiliaConvitesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, familia_id):
        familia = familia_acessivel(request.user, familia_id)
        if not administrador(request.user, familia):
            return Response({'detail': 'Somente administradores podem ver convites enviados.'},
                            status=status.HTTP_403_FORBIDDEN)
        convites = ConviteFamilia.objects.filter(
            familia=familia, status=ConviteFamilia.PENDENTE
        ).select_related('familia', 'convidado_por', 'usuario')
        return Response(ConviteFamiliaSerializer(convites, many=True).data)
