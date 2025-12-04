from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count
from bs4 import BeautifulSoup
from .models import Aluno, Relatorio
import requests
import json
import csv
import base64
import os
import numpy as np
import cv2
import face_recognition
from datetime import datetime
from django.contrib import messages
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
# Create your views here.


def index(request):
    return render(request, 'leitura_cartao.html');

def pagLogin(request):
    if request.user.is_authenticated:
        return redirect('index')

    return render(request, 'login.html')

def logar(request):
    if request.method == 'POST':
        usuario = request.POST.get('usuario')
        senha = request.POST.get('senha')
        userBanco = authenticate(request, username=usuario, password=senha)
        if userBanco is not None:
            login(request, userBanco)
            return redirect('/')
        else:
            messages.error(request, 'Nome ou senha inválidos.')

    return render(request, 'login.html')


def cadastro(request):
    return render(request, 'cadastro.html')


@csrf_exempt
def cadastrar(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        url = data.get('url')

        
        if not url:
            print("Nenhum URL recebido")
            return JsonResponse({'mensagem': 'Nenhum URL enviado'})

        print(f"QR Code detectado: {url}")

        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
               
            dados = {}
            for tr in soup.find_all("tr"):
                tds = tr.find_all("td")
                if len(tds) == 2:
                    chave = tds[0].get_text(strip=True)
                    valor = tds[1].get_text(strip=True)
                    dados[chave] = valor              

            if Aluno.objects.filter(nome=dados.get('Para', '')).exists():
                print("Aluno já cadastrado")
                return JsonResponse({'mensagem': 'Aluno já cadastrado!'})

            else:
                
                data_str = dados.get("Emitido em", "").strip('“”')
                data_formatada = datetime.strptime(data_str, "%d/%m/%y").date()

                usuario = Aluno(
                    nome=dados.get('Para', ''),
                    faculdade=dados.get('Faculdade', ''),
                    curso=dados.get('Curso', ''),
                    turno=dados.get('Turno', ''),
                    emitido=data_formatada
                )
                usuario.save()
                print("Página acessada com sucesso:")
                

                for chave, valor in dados.items():
                    print(f"  {chave}: {valor}")
                return JsonResponse({'mensagem': 'Aluno cadastrado com sucesso!'})

        except Exception as e:
            print(f"Erro ao processar o URL: {e}")
            return JsonResponse({'mensagem': str(e)})

    return JsonResponse({'mensagem': 'Método não permitido'}, status=405)


def leitura_cartao(request):
    return render(request, 'leitura_cartao.html')


@csrf_exempt
def encontrarAluno (request):
    if request.method == 'POST':
        data = json.loads(request.body)
        url = data.get('url')

        if not url:
            print(" Nenhum URL recebido")
            return JsonResponse({'mensagem': 'Nenhum URL enviado'})
        print(f"📡 QR Code detectado: {url}")

        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')

            dados = {}

            for tr in soup.find_all("tr"):
                tds = tr.find_all("td")
                if len(tds) == 2:
                    chave = tds[0].get_text(strip=True)
                    valor = tds[1].get_text(strip=True)
                    dados[chave] = valor
            if not Aluno.objects.filter(nome=dados.get('Para', '')).exists():
                 

                relatorio = Relatorio(
                    nome=dados.get('Para', ''),
                    faculdade=dados.get('Faculdade', ''),
                    turno=dados.get('Turno', ''),
                    status = False,
                    face_ou_cartao = True,
                    curso=dados.get('Curso', ''),
                )
                relatorio.save()
            
                return JsonResponse({'mensagem': "Aluno não encontrado"})

                
            else:
                
                relatorio = Relatorio(
                    nome=dados.get('Para', ''),
                    faculdade=dados.get('Faculdade', ''),
                    turno=dados.get('Turno', ''),
                    status = True,
                    face_ou_cartao = True,
                    curso=dados.get('Curso', ''),
                )
                relatorio.save()

                return JsonResponse({'mensagem': "Liberado"})

        except Exception as e:
            print(f" Erro ao acessar o URL: {e}")
            return JsonResponse({'mensagem': str(e)})
        
    return render(request, 'leitura_cartao.html')


def relatorios(request):
    relatorio = Relatorio.objects.all().values().order_by('-data')
    total = Relatorio.objects.count()
    liberados = Relatorio.objects.filter(status=True).count()
    negados = Relatorio.objects.filter(status=False).count()
    face = Relatorio.objects.filter(face_ou_cartao=False).count()
    cartao = Relatorio.objects.filter(face_ou_cartao=True).count()

    return render(request, 'relatorios.html', {'relatorio': relatorio, 'total':total, 'liberados':liberados, 'negados':negados, 'face':face, 'cartao':cartao})


def estudantes(request):
    estudantes = Aluno.objects.all().values()
    total = Aluno.objects.count()
    ads = Aluno.objects.filter(curso='Curso Superior de Tecnologia em -  Análise e Desenvolvimento de Sistemas').count()
    dsm = Aluno.objects.filter(curso='Curso Superior de Tecnologia em -  Desenvolvimento de Software Multiplataforma').count()
    comex = Aluno.objects.filter(curso='Curso Superior de Tecnologia em -  Comércio Exterior').count()
    pq = Aluno.objects.filter(curso='Curso Superior de Tecnologia em -  Processos Químicos').count()
    ge = Aluno.objects.filter(curso='Curso Superior de Tecnologia em -  Gestão Empresarial').count()
    return render(request, 'estudantes.html', {'estudantes':estudantes, 'total':total, 'ads':ads, 'dsm':dsm, 'comex':comex, 'pq':pq, 'ge':ge})


def exportar_csv(request):
    dados = request.GET.get('x')
    response = HttpResponse(content_type='text/csv')
    if dados == 'estudantes':
        response['Content-Disposition'] = 'attachment; filename="alunos.csv"'
        writer = csv.writer(response)
        writer.writerow(['Nome: ', 'Curso: ', 'Faculdade: ', 'Turno: '])
        for item in Aluno.objects.all():
            writer.writerow([item.nome, item.curso, item.faculdade, item.turno])
    else:
        response['Content-Disposition'] = 'attachment; filename="relatorio.csv"'
        writer = csv.writer(response)
        writer.writerow(['Nome:', 'Curso: ', 'Faculdade: ', 'Turno: ', 'Data'])
        for item in Relatorio.objects.all():
            writer.writerow([item.nome, item.curso, item.faculdade, item.turno, item.data])

    return response

def reconhecimento(request):
    return render(request, 'reconhecimento_facial.html')

@csrf_exempt
def verificar_rosto(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'Método não permitido.'}, status=405)

    try:
        data = json.loads(request.body)
        image_data_url = data['image_data']

        format, imgstr = image_data_url.split(';base64,') 
        decoded_image = base64.b64decode(imgstr)
        np_arr = np.frombuffer(decoded_image, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        alunos = Aluno.objects.exclude(img__isnull=True).exclude(img__exact='')
        if not alunos.exists():
            return JsonResponse({'status': 'Erro: Nenhum aluno com imagem encontrada no banco.'}, status=500)

        known_encodings = []
        lista_alunos = []

        for aluno in alunos:
            try:
                imagem_aluno = face_recognition.load_image_file(aluno.img.path)
                encoding = face_recognition.face_encodings(imagem_aluno)

                if encoding:
                    known_encodings.append(encoding[0])
                    lista_alunos.append(aluno)
            except Exception as e:
                print(f"Erro ao processar imagem do aluno {aluno.id}: {e}")
                continue

        face_locations = face_recognition.face_locations(img)
        face_encodings = face_recognition.face_encodings(img, face_locations)

        status_message = "Rosto não reconhecido. Acesso negado."
        match_found = False
        aluno_reconhecido = None

        for face_encoding in face_encodings:
            results = face_recognition.compare_faces(known_encodings, face_encoding, tolerance=0.45)

            if True in results:
                index = results.index(True)
                aluno_reconhecido = lista_alunos[index]
                match_found = True
                status_message = f"Verificado! Bem-vindo, {aluno_reconhecido.nome}."

                Relatorio.objects.create(
                    nome=aluno_reconhecido.nome,
                    faculdade=aluno_reconhecido.faculdade,
                    turno=aluno_reconhecido.turno,
                    status=True,
                    face_ou_cartao=False,
                    curso=aluno_reconhecido.curso,
                )
                break

        return JsonResponse({
            'status': status_message,
            'match': match_found,
            'success': True,
            'aluno_nome': aluno_reconhecido.nome if match_found else None
        })

    except json.JSONDecodeError:
        return JsonResponse({'status': 'Erro ao decodificar JSON.'}, status=400)

    except Exception as e:
        print(f"Erro interno no backend: {e}")
        return JsonResponse({'status': f'Erro interno no servidor: {str(e)}'}, status=500)