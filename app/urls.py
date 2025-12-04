from . import views
from django.urls import path

urlpatterns = [
    path('', views.index, name='index'),
    path('login', views.pagLogin, name='login'),
    path('logar', views.logar, name='logar'),
    path('cadastro', views.cadastro, name='cadastro'),
    path('cadastrar/', views.cadastrar, name='cadastrar'),
    path('leitura_cartao', views.leitura_cartao, name='leitura_cartao'),
    path('verificar/', views.encontrarAluno, name='verificar'),
    path('relatorios', views.relatorios, name='relatorios'),
    path('estudantes', views.estudantes, name='estudantes'),
    path('exportar', views.exportar_csv, name='exportCsv'),
    path('reconhecimento_facial', views.reconhecimento, name='reconhecimento_facial'),
    path('verificar_rosto/', views.verificar_rosto, name='verificar_rosto'),
]