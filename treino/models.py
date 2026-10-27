from datetime import date
from django.db import models


class FaixaChoices(models.TextChoices):
    BRANCA = "B", "Branca"
    AZUL = "A", "Azul"
    ROXA = "R", "Roxa"
    MARROM = "M", "Marrom"
    PRETA = "P", "Preta"


class Alunos(models.Model):
    nome = models.CharField(max_length=255)
    email = models.EmailField(unique=True)

    faixa = models.CharField(
        max_length=1,
        choices=FaixaChoices.choices,
        default=FaixaChoices.BRANCA
    )

    data_nascimento = models.DateField(
        null=True,
        blank=True
    )

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Aluno"
        verbose_name_plural = "Alunos"


class AulasConcluidas(models.Model):
    aluno = models.ForeignKey(
        Alunos,
        on_delete=models.CASCADE,
        related_name="aulas_concluidas"
    )

    data = models.DateField(default=date.today)

    faixa_atual = models.CharField(
        max_length=1,
        choices=FaixaChoices.choices
    )

    def __str__(self):
        return f"{self.aluno.nome} - {self.data}"

    class Meta:
        verbose_name = "Aula concluída"
        verbose_name_plural = "Aulas concluídas"