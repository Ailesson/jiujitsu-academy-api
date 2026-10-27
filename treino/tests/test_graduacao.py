import pytest
from treino.graduacao import calcular_aulas_necessarias


@pytest.mark.parametrize(
    "nivel, esperado",
    [(0, 30), (1, 70), (2, 97), (3, 117), (4, None)],
)
def test_quantidade_aulas_por_faixa(nivel, esperado):
    assert calcular_aulas_necessarias(nivel) == esperado


@pytest.mark.parametrize("nivel", [-1, 5, 10, 1.5, True, "2"])
def test_nivel_invalido(nivel):
    with pytest.raises(ValueError):
        calcular_aulas_necessarias(nivel)
