from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _

class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, cpf, email, password=None, **extra_fields):
        if not cpf:
            raise ValueError('O usuário precisa ter um CPF.')
        if not email:
            raise ValueError('O usuário precisa ter um e-mail.')
            
        email = self.normalize_email(email)
        user = self.model(cpf=cpf, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, cpf, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        return self.create_user(cpf, email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    cpf = models.CharField(max_length=11, unique=True, verbose_name=_('CPF'), help_text=_('Apenas números'))
    email = models.EmailField(max_length=255, unique=True, verbose_name=_('email'))
    name = models.CharField(max_length=255, blank=True, null=True, verbose_name=_('name'))
    telefone = models.CharField(max_length=20, blank=True, null=True, verbose_name=_('Telefone'))
    foto = models.ImageField(upload_to='perfil_fotos/', null=True, blank=True, verbose_name=_('Foto de Perfil'))
    
    is_staff = models.BooleanField(default=False, verbose_name=_('staff status'))
    is_active = models.BooleanField(default=True, verbose_name=_('active'))
    criado_em = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = 'cpf'
    REQUIRED_FIELDS = ['email']

    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'

    def __str__(self):
        return f'{self.name or self.email} - {self.cpf}'