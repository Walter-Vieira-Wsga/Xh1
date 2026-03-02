from django.db import models
from django.conf import settings


class Vendor(models.Model):
    ESTADO_CHOICES = (
        ('SP', 'São Paulo'),
        ('RJ', 'Rio de Janeiro'),
        ('MG', 'Minas Gerais'),
        ('PR', 'Parana'),
    )

    SITUACAO_EMPRESA_CHOICES = (
        ('1', 'Ativa'),
        ('2', 'Suspensa'),
        ('3', 'Inapta'),
        ('4', 'Baixada'),
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='vendor'
    )
    company_name = models.CharField(max_length=255, verbose_name='Razão Social: ')
    cnpj = models.CharField(max_length=18, unique=True, verbose_name='CNPJ: ')
    cnpj_situacao = models.CharField(max_length=1,choices=SITUACAO_EMPRESA_CHOICES,default="1", verbose_name='Situação: ')
    logo = models.ImageField(upload_to='vendors/logos/', blank=True, null=True, verbose_name='Logotipo: ')
    description = models.TextField(blank=True, verbose_name='Descrição: ')
    cnpj_rua = models.CharField(max_length=255, verbose_name='ENdereço: ')
    cnpj_muncipio = models.CharField(max_length=50, verbose_name='Municipio: ')
    cnpj_estado = models.CharField(max_length=2,choices=ESTADO_CHOICES,default="FR",)
    cnpj_cep = models.CharField(max_length=9, verbose_name='CEP: ')
    cnpj_cnae_principal = models.CharField(max_length=9, verbose_name='CNAE Principal: ')
    cpf_responsavel_principal = models.CharField(max_length=11, verbose_name='CPF Responsável: ')
    cpf_responsavel_socio = models.CharField(max_length=11, blank=True, default="", verbose_name='CPF Sócio: ')
    opcao_mei = models.BooleanField(default=False, verbose_name='Opção MEI: ')
    opcao_simples = models.BooleanField(default=False, verbose_name='Opção Simples Nacional: ')
    email = models.EmailField(verbose_name='email: ')
    telefone1 = models.CharField(max_length=25, verbose_name='Telefone 1:')
    telefone2 = models.CharField(max_length=25, blank=True, default="", verbose_name='Telefone 2: ')
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.company_name