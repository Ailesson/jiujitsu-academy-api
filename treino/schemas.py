from datetime import date

from ninja import ModelSchema, Schema
from pydantic import EmailStr, Field

from .models import Alunos


class AlunoCriacaoSchema(ModelSchema):
    email: EmailStr

    class Meta:
        model = Alunos
        fields = [
            "nome",
            "email",
            "faixa",
            "data_nascimento",
        ]


class AlunosSchema(ModelSchema):
    class Meta:
        model = Alunos
        fields = [
            "id",
            "nome",
            "email",
            "faixa",
            "data_nascimento",
        ]


class ProgressoAlunoSchema(Schema):
    email: EmailStr
    nome: str
    faixa: str
    total_aulas: int
    aulas_necessarias_para_proxima_faixa: int | None


class AulaRealizadaSchema(Schema):
    qtd: int = Field(default=1, ge=1, le=100)
    email_aluno: EmailStr

class AlunoAtualizacaoSchema(Schema):
    nome: str | None = None
    email: EmailStr | None = None
    faixa: str | None = None
    data_nascimento: date | None = None