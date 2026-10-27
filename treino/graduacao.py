import math

ORDER_BELT = {
    "Branca": 0,
    "Azul": 1,
    "Roxa": 2,
    "Marrom": 3,
    "Preta": 4,
}


def calcular_aulas_necessarias(nivel: int) -> int | None:
    if not isinstance(nivel, int) or isinstance(nivel, bool):
        raise ValueError("O nível deve ser um número inteiro.")

    if nivel not in ORDER_BELT.values():
        raise ValueError("Nível de faixa inválido.")

    if nivel == ORDER_BELT["Preta"]:
        return None

    d = 1.47
    k = 30 / math.log(d)

    aulas = k * math.log(nivel + d)

    return round(aulas)