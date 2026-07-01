from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from core.models import User, Cartao, Familia, MembroFamilia, DespesaCompartilhada, MetaFinanceira, Transacao

class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {'fields': ('cpf', 'password')}),
        ('Informações Pessoais', {'fields': ('name', 'email', 'telefone', 'foto')}),
        ('Permissões', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Datas Importantes', {'fields': ('criado_em', 'last_login')}),
    )
    list_display = ('cpf', 'name', 'email', 'is_staff', 'criado_em')
    search_fields = ('cpf', 'name', 'email')
    ordering = ('cpf',)
    readonly_fields = ('criado_em', 'last_login')


admin.site.register(User, UserAdmin)
admin.site.register(Cartao)
admin.site.register(Familia)
admin.site.register(MembroFamilia)
admin.site.register(DespesaCompartilhada)
admin.site.register(MetaFinanceira)
admin.site.register(Transacao)