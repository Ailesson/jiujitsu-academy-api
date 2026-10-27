import pytest
from treino.models import Alunos


@pytest.fixture
def aluno(db):
    return Alunos.objects.create(
        nome="Ana Silva",
        email="ana@example.com",
        faixa="B",
        data_nascimento="2000-04-15",
    )
