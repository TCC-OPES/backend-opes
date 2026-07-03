from django.contrib import admin
from core.models import User, Cartao, Familia, MembroFamilia, DespesaCompartilhada, MetaFinanceira, Transacao
from django.contrib.auth.hashers import make_password

class UserAdmin(admin.ModelAdmin):
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

    def save_model(self, request, obj, form, change):
        if not change or 'password' in form.changed_data:
            obj.password = make_password(obj.password)
        super().save_model(request, obj, form, change)


admin.site.register(User, UserAdmin)
admin.site.register(Cartao)
admin.site.register(Familia)
admin.site.register(MembroFamilia)
admin.site.register(DespesaCompartilhada)
admin.site.register(MetaFinanceira)
admin.site.register(Transacao)