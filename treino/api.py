
from datetime import date

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404

from ninja import Router
from ninja.errors import HttpError

from .models import Alunos, AulasConcluidas
from .schemas import (
    AlunoCriacaoSchema,
    AlunoAtualizacaoSchema,
    AlunosSchema,
    ProgressoAlunoSchema,
    AulaRealizadaSchema,
)
from .graduacao import (
    ORDER_BELT,
    calcular_aulas_necessarias,
)


treino_router = Router()


def validar_aluno(aluno):

    if aluno.data_nascimento:
        hoje = date.today()

        if aluno.data_nascimento > hoje:
            raise HttpError(400, "Data de nascimento inválida.")

        idade = hoje.year - aluno.data_nascimento.year - (
            (hoje.month, hoje.day)
            < (aluno.data_nascimento.month, aluno.data_nascimento.day)
        )

        if idade < 18 and aluno.faixa in ("A", "R", "M", "P"):
            raise HttpError(
                400,
                "O aluno é menor de idade e não pode "
                "ser graduado para essa faixa."
            )

    try:
        aluno.full_clean()
    except ValidationError as erro:
        raise HttpError(400, str(erro))


@treino_router.post("/", response={201: AlunosSchema})
def criar_aluno(request, aluno_schema: AlunoCriacaoSchema):

    dados = aluno_schema.model_dump()

    aluno = Alunos(**dados)

    if  Alunos.objects.filter(email=aluno.email).exists():
        raise HttpError(409, "E-mail já cadastrado.")

    validar_aluno(aluno)

    try:
        with transaction.atomic():
            aluno.save()
    except IntegrityError:
        raise HttpError(409, "E-mail já cadastrado.")

    return 201, aluno


@treino_router.get("/alunos/", response=list[AlunosSchema])
def listar_alunos(request):

    return Alunos.objects.all()


@treino_router.get(
    "/progresso_aluno/",
    response=ProgressoAlunoSchema
)
def progresso_aluno(request, email_aluno: str):

    aluno = get_object_or_404(
        Alunos,
        email=email_aluno
    )

    total_aulas = AulasConcluidas.objects.filter(
        aluno=aluno
    ).count()

    faixa_atual = aluno.get_faixa_display()

    nivel = ORDER_BELT[faixa_atual]

    aulas_necessarias = calcular_aulas_necessarias(nivel)

    aulas_na_faixa = AulasConcluidas.objects.filter(
        aluno=aluno,
        faixa_atual=aluno.faixa
    ).count()

    if aulas_necessarias is None:
        aulas_faltantes = None
    else:
        aulas_faltantes = max(
            aulas_necessarias - aulas_na_faixa,
            0
        )

    return {
        "email": aluno.email,
        "nome": aluno.nome,
        "faixa": aluno.faixa,
        "total_aulas": total_aulas,
        "aulas_necessarias_para_proxima_faixa": aulas_faltantes,
    }


@treino_router.post("/aula_realizada/", response=str)
def aula_realizada(
    request,
    aula_realizada: AulaRealizadaSchema
):

    dados = aula_realizada.model_dump()

    qtd = dados["qtd"]

    aluno = get_object_or_404(
        Alunos,
        email=dados["email_aluno"]
    )

    aulas = [
        AulasConcluidas(
            aluno=aluno,
            faixa_atual=aluno.faixa
        )
        for _ in range(qtd)
    ]

    AulasConcluidas.objects.bulk_create(aulas)

    return f"{qtd} aulas registradas para {aluno.nome}."


@treino_router.patch(
    "/alunos/{aluno_id}",
    response=AlunosSchema
)
def atualizar_aluno(
    request,
    aluno_id: int,
    aluno_data: AlunoAtualizacaoSchema
):
    aluno = get_object_or_404(
        Alunos,
        id=aluno_id
    )

    dados = aluno_data.model_dump(exclude_unset=True)

    for campo, valor in dados.items():
        if campo != "data_nascimento" and valor is None:
            raise HttpError(
                400,
                f"O campo {campo} não pode ser nulo."
            )
        
    email = dados.get("email", aluno.email)

    if Alunos.objects.filter(
        email=email
    ).exclude(id=aluno.id).exists():
        raise HttpError(
            409,
            "E-mail já cadastrado."
        )
    
    for campo, valor in dados.items():
        setattr(aluno, campo, valor)


    validar_aluno(aluno)

    try:
        with transaction.atomic():
            aluno.save()
    except IntegrityError:
        raise HttpError(
            409,
            "E-mail já cadastrado."
        )

    return aluno

