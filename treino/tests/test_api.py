import json
from datetime import date

import pytest
from django.test import Client
from treino.models import Alunos, AulasConcluidas


@pytest.fixture
def api_client():
    return Client()


def enviar_json(client, metodo, rota, dados):
    return getattr(client, metodo)(
        rota,
        data=json.dumps(dados),
        content_type="application/json",
    )


def dados_aluno(**alteracoes):
    dados = {
        "nome": "Bruno Costa",
        "email": "bruno@example.com",
        "faixa": "B",
        "data_nascimento": "2000-01-10",
    }
    dados.update(alteracoes)
    return dados


@pytest.mark.django_db
def test_criar_aluno(api_client):
    resposta = enviar_json(api_client, "post", "/api/", dados_aluno())
    assert resposta.status_code == 201
    assert resposta.json()["email"] == "bruno@example.com"
    assert Alunos.objects.filter(email="bruno@example.com").exists()


@pytest.mark.django_db
def test_criar_aluno_duplicado(api_client, aluno):
    resposta = enviar_json(
        api_client, "post", "/api/", dados_aluno(email=aluno.email)
    )
    assert resposta.status_code == 409
    assert Alunos.objects.filter(email=aluno.email).count() == 1


@pytest.mark.django_db
def test_criar_menor_com_faixa_azul_rejeitado(api_client):
    resposta = enviar_json(
        api_client,
        "post",
        "/api/",
        dados_aluno(data_nascimento=date.today().isoformat(), faixa="A"),
    )
    assert resposta.status_code == 400
    assert not Alunos.objects.filter(email="bruno@example.com").exists()


@pytest.mark.django_db
def test_listar_alunos(api_client, aluno):
    resposta = api_client.get("/api/alunos/")
    assert resposta.status_code == 200
    assert any(item["email"] == aluno.email for item in resposta.json())


@pytest.mark.django_db
def test_progresso_sem_aulas(api_client, aluno):
    resposta = api_client.get("/api/progresso_aluno/", {"email_aluno": aluno.email})
    assert resposta.status_code == 200
    dados = resposta.json()
    assert dados["total_aulas"] == 0
    assert dados["aulas_necessarias_para_proxima_faixa"] == 30


@pytest.mark.django_db
def test_progresso_faixa_preta(api_client, aluno):
    aluno.faixa = "P"
    aluno.save(update_fields=["faixa"])
    resposta = api_client.get("/api/progresso_aluno/", {"email_aluno": aluno.email})
    assert resposta.status_code == 200
    assert resposta.json()["aulas_necessarias_para_proxima_faixa"] is None


@pytest.mark.django_db
def test_progresso_aluno_inexistente(api_client):
    resposta = api_client.get(
        "/api/progresso_aluno/", {"email_aluno": "inexistente@example.com"}
    )
    assert resposta.status_code == 404


@pytest.mark.django_db
def test_registrar_aulas(api_client, aluno):
    resposta = enviar_json(
        api_client,
        "post",
        "/api/aula_realizada/",
        {"email_aluno": aluno.email, "qtd": 5},
    )
    assert resposta.status_code == 200
    assert AulasConcluidas.objects.filter(aluno=aluno, faixa_atual="B").count() == 5


@pytest.mark.django_db
@pytest.mark.parametrize("qtd", [0, -1, 101, None])
def test_quantidade_invalida(api_client, aluno, qtd):
    resposta = enviar_json(
        api_client,
        "post",
        "/api/aula_realizada/",
        {"email_aluno": aluno.email, "qtd": qtd},
    )
    assert resposta.status_code == 422
    assert AulasConcluidas.objects.filter(aluno=aluno).count() == 0


@pytest.mark.django_db
def test_registrar_aulas_aluno_inexistente(api_client):
    resposta = enviar_json(
        api_client,
        "post",
        "/api/aula_realizada/",
        {"email_aluno": "inexistente@example.com", "qtd": 1},
    )
    assert resposta.status_code == 404


@pytest.mark.django_db
def test_atualizacao_parcial_preserva_outros_campos(api_client, aluno):
    resposta = enviar_json(
        api_client, "patch", f"/api/alunos/{aluno.pk}", {"nome": "Ana Atualizada"}
    )
    assert resposta.status_code == 200
    aluno.refresh_from_db()
    assert aluno.nome == "Ana Atualizada"
    assert aluno.email == "ana@example.com"
    assert aluno.faixa == "B"


@pytest.mark.django_db
def test_atualizacao_aluno_inexistente(api_client):
    resposta = enviar_json(
        api_client, "patch", "/api/alunos/99999", {"nome": "Novo Nome"}
    )
    assert resposta.status_code == 404


@pytest.mark.django_db
def test_atualizacao_impede_modificar_id(api_client, aluno):
    resposta = enviar_json(
        api_client, "patch", f"/api/alunos/{aluno.pk}", {"id": 99999}
    )
    assert resposta.status_code == 200  # campos extras podem ser ignorados pelo schema
    aluno.refresh_from_db()
    assert aluno.pk != 99999


@pytest.mark.django_db
def test_atualizacao_email_duplicado(api_client, aluno):
    outro = Alunos.objects.create(nome="Outro", email="outro@example.com", faixa="B")
    resposta = enviar_json(
        api_client, "patch", f"/api/alunos/{outro.pk}", {"email": aluno.email}
    )
    assert resposta.status_code == 409
    outro.refresh_from_db()
    assert outro.email == "outro@example.com"
