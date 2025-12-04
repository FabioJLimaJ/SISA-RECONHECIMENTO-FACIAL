from django.db import models

# Create your models here.

class Aluno(models.Model):
    img = models.ImageField(upload_to='rostos/', null=True, blank=True)
    encoding = models.BinaryField(null=True, blank=True) 
    nome = models.CharField(max_length=255)
    faculdade = models.CharField(max_length=255)
    ra = models.IntegerField(null=True, blank=True)
    curso = models.CharField(max_length=255)
    turno = models.CharField(max_length=20)
    emitido = models.DateField(null=True,)


class Relatorio(models.Model):
    nome = models.CharField(max_length=255)
    faculdade = models.CharField(max_length=255)
    curso = models.CharField(max_length=255)
    turno = models.CharField(max_length=20)
    status = models.BooleanField()
    face_ou_cartao = models.BooleanField()
    data = models.DateTimeField(auto_now_add=True)
