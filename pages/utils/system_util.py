from itertools import combinations
from math import lcm
from typing import Tuple, Literal, Union

Step = Union[
    Tuple[Literal["swap"], int, int],
    Tuple[Literal["subtract"], int, int, int],
    Tuple[Literal["multiply"], int, int],
    Tuple[Literal["comment"], str],
    Tuple[Literal["divide"], int, int]
]
"""
tipo customizado para anotar "step"
"""

def generate_extended_matrix(num_stats: int) -> list[list[str]]:
    """
    gera a matrix estendida do sistema de equações decorente do problem "n-{1,2}"
    
    Parâmetros:

    - num_stats (int): o numero de atributos do sistema

    Retorna:

    - list[list[str]]: uma matrix de n linhas e n + n*(n-1)/2 + 1 colunas que representa simbolicamente a matrix extendida
    """
    matrix = []
    num_mixed = num_stats * (num_stats - 1)//2
    for i in range(1, num_stats + 1):
        row = []
        mixed_index = combinations(range(1, num_stats + 1), 2)
        for j, combo in zip(range(1, num_mixed + 1), mixed_index):
            j, k = combo
            if i == j or i == k:
                row.append("m")
            else:
                row.append("0")
        for j in range(1, num_stats + 1):
            if i == j:
                row.append("p")
            else:
                row.append("0")
        row.append("s" + str(i))
        matrix.append(row)
    return matrix

def generate_auxiliar_matrix(num_stats: int) -> list[list[int]]:
    """
    gera a matrix auxiliar do sistema de equações decorente do problem "n-{1,2}"
    
    Parâmetros:

    - num_stats (int): o numero de atributos do sistema

    Retorna:

    - list[list[int]]: uma matrix de n linhas e n + n*(n-1)/2 + n colunas para auxilio da extração da logica de escalonamento do sistema
    """
    matrix = []
    num_mixed = num_stats * (num_stats - 1)//2
    for i in range(1, num_stats + 1):
        row = []
        mixed_index = combinations(range(1, num_stats + 1), 2)
        for j, combo in zip(range(1, num_mixed + 1), mixed_index):
            j, k = combo
            if i == j or i == k:
                row.append(1)
            else:
                row.append(0)
        for j in range(1, num_stats + 1):
            if i == j:
                row.append(1)
            else:
                row.append(0)
        for j in range(1, num_stats + 1):
            if i == j:
                row.append(1)
            else:
                row.append(0)
        matrix.append(row)
    return matrix

def value_format(value: int | str, extra: str = "") -> str:
    """
    Formata um valor inteiro ou string para exibição nos passos do SageMath,
    especialmente quando há multiplicações (com exceções como fator 1 ou -1).
    
    Parâmetros:
    - value (int ou str): o valor a ser tratado
    - extra (str): sufixo adicional, como '*' ou outro, opcional

    Retorna:
    - str: uma string formatada para uso simbólico
    """
    sign, body = "", ""
    if isinstance(value, int):
        sign = '+' if value > 0 else '-'
        body = str(abs(value)) + extra if abs(value) != 1 else ''
    else:
        sign = '-' if '-' in value else '+'
        clean_value = value.replace('-', '')
        body = '' if value in ['1', '-1'] else clean_value + extra
    return sign + body

def decode_step(step: Step) -> str:
    """
    decodifica os passos gerados pela matrix auxiliar em linguagem compativel com editores simbolicos como o sagemath, os passos implementados são:
    - ("swap", i: int, j: int): operação de troca entre as linhas i e j
    - ("subtract", i: int, j: int, fator: int): operação de subtração da linha j pela linha i multiplicada de um fator inteiro
    - ("multiply", i: int, fator: int): operação de multiplifação da linha i por um fator
    - ("comment", msg: str): insere uma linha de comentario
    - ("divide", fator: int): analogo a "multiply", porem efetua a divisão
    
    Parâmetros:

    - step (tuple): uma tupla indicando um passo, explicado acima

    Retorna:

    - str: uma string correspodente ao passo traduzido em linguagem compativel com editores simbolicos como o sagemath
    """
    if step[0] == "swap":
        i, j = step[1], step[2]
        return f"M[{i}], M[{j}] = M.row({j}), M.row({j})"
    elif step[0] == "subtract":
        i, j, factor = step[1], step[2], step[3]
        return f"M[{j}] = M.row({j}){value_format(-factor, '*')}M.row({i})"
    elif step[0] == "multiply":
        i, factor = step[1], step[2]
        return f"M[{i}] = {value_format(factor, '*')}M.row({i})"
    elif step[0] == "comment":
        comment = step[1]
        return f"# {comment}"
    elif step[0] == "divide":
        i, factor = step[1], step[2]
        return f"M[{i}] = {'-' if factor < 0 else ''}M.row({i}){'/' + str(abs(factor)) if abs(factor) != 1 else ''}"
    else:
        raise NotImplementedError(f"Unknown step type: {step[0]}")

def scale_by_a_factor(matrix: list[list[int]], i: int, j: int, steps: list[Step], matrix_width: int | None = None, pivot: int | None = None, ref: int | None = None) -> tuple[int, int]:
    """
    efetua a sincronização da linha i com a linha j da matrix auxiliar a fim de evitar a divisão e eventuais problemas de precisão numerica
    
    Parâmetros:

    - matrix (list[list[int]]): a matrix auxiliar
    - i (int): o indice da primeira linha, 0-indexado
    - j (int): o indice da segunda linha, 0-indexado
    - steps (list[tuple]): uma lista a qual sera populada com os passos equivalente gerado nessa operação
    - matrix_width (int ou None): um inteiro representando a largura da linha, sendo calculada com base na primeira linha caso não informado
    - pivot (int ou None): o elemento pivo da linha i, sendo calculado como o elemento de indice i da linha i caso não informado
    - ref (int ou None): o elemento de referencia da linha j, sendo calculado como o elemento de indice i da linha j caso não informado

    Retorna:

    - tuple[int, int]: uma tupla de elementos iguais (o minimo multiplo comun do pivo e do elemento de referencia), com substituir ambos o pivo e a referencia simultaneamente)
    """
    matrix_width = len(matrix[i]) if matrix_width is None else matrix_width
    pivot = matrix[i][i] if pivot is None else pivot
    ref = matrix[j][i] if ref is None else ref
    common_ground = lcm(ref, pivot)
    scale_ref = common_ground // ref
    scale_pivot = common_ground // pivot
    steps.append(("multiply", i, scale_pivot))
    steps.append(("multiply", j, scale_ref))
    for k in range(matrix_width):
        matrix[i][k] *= scale_pivot
        matrix[j][k] *= scale_ref
    return common_ground, common_ground

def apply_row_elimination(matrix: list[list[int]], i: int, j: int, steps: list[Step], matrix_width: int | None = None, pivot: int | None = None) -> None:
    """
    aplica o processo de eliminação da linha j pela linha i, funciona tanto na subida quando na descida
    
    Parâmetros:

    - matrix (list[list[int]]): a matrix auxiliar
    - i (int): o indice da primeira linha, 0-indexado
    - j (int): o indice da segunda linha, 0-indexado
    - steps (list[tuple]): uma lista a qual sera populada com os passos equivalente gerado nessa operação
    - matrix_width (int ou None): um inteiro representando a largura da linha, sendo calculada com base na primeira linha caso não informado
    - pivot (int ou None): o elemento pivo da linha i, sendo calculado como o elemento de indice i da linha i caso não informado

    Retorna:

    - None: não há retorno, apenas a população da lista steps com os passos equivalentes
    """
    matrix_width = len(matrix[i]) if matrix_width is None else matrix_width
    pivot = matrix[i][i] if pivot is None else pivot
    ref = matrix[j][i]
    if ref == 0:
        return
    if ref%pivot != 0:
        ref, pivot = scale_by_a_factor(matrix, i, j, steps, matrix_width, pivot, ref)
    factor = matrix[j][i] // matrix[i][i]
    for k in range(matrix_width):
        matrix[j][k] -= factor * matrix[i][k]
    steps.append(("subtract", i, j, factor))