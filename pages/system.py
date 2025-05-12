import streamlit as st, textwrap
from pages.utils.system_util import generate_extended_matrix, generate_auxiliar_matrix, decode_step, apply_row_elimination
from math import gcd, lcm
from itertools import combinations

def write_extended_matrix_markdown(matrix:list[list[str]], extended_matrix_introduction: str | None = None) -> str:
    header_size = len(matrix[0])
    header = ''.join(['c']*(header_size - 1) + [':c'])
    content = '\\\\\n'.join(['&'.join(map(str, row)) for row in matrix])
    code = textwrap.dedent(f"""
    $$
    \\left[\\begin{{array}}{{{header}}}
    {content}
    \\end{{array}}\\right]
    $$
    """).replace("\t", "").replace("    ", "").replace("&s", "&s_")
    if extended_matrix_introduction:
        markdown = f"{extended_matrix_introduction}\n{code}"
    st.code(markdown, language="latex")
    return code

def write_sage_steps(matrix:list[list[int]], num_stats:int, sage_code_introduction: str | None = None, ignore_comments: bool = True) -> list[list[str]]:
    variables = ['p', 'm'] + [f's{i}' for i in range(1, num_stats + 1)]
    sage_variables_definition = f"var('{' '.join(variables)}')"
    aux = ',\n    '.join([f"[{', '.join(row)}]" for row in matrix])
    sage_matrix_definition = f"M = matrix([\n    {aux}\n])"
    aux_matrix = generate_auxiliar_matrix(num_stats )
    aux_steps = []
    matrix_width = len(aux_matrix[0])
    if not ignore_comments:
        aux_steps.append(("comment", "fist step: upper triangularization"))
    for i in range(num_stats):
        if aux_matrix[i][i] == 0:
            for j in range(i, num_stats):
                if aux_matrix[j][i] != 0:
                    aux_matrix[i], aux_matrix[j] = aux_matrix[j], aux_matrix[i]
                    aux_steps.append(("swap", i, j))
        pivot = aux_matrix[i][i]
        if pivot == 0:
            raise NotImplementedError("the function can't handle this case yet")
        for j in range(i + 1, num_stats):
            apply_row_elimination(aux_matrix, i, j, aux_steps, matrix_width, pivot)
    if not ignore_comments:
        aux_steps.append(("comment", "second step: back substitution"))
    for i in range(num_stats-1, -1, -1):
        pivot = aux_matrix[i][i]
        for j in range(i - 1, -1, -1):
            apply_row_elimination(aux_matrix, i, j, aux_steps, matrix_width, pivot)
    if not ignore_comments:
        aux_steps.append(("comment", "third step: normalization"))
    for i in range(num_stats):
        pivot = aux_matrix[i][i]
        factor = pivot
        for k in range(matrix_width):
            negative = False
            p = aux_matrix[i][k]
            if (p > 0 and factor < 0) or (p < 0 and factor > 0):
                negative = True
            p, q = abs(p), abs(factor)
            d = gcd(p, q)
            p //= d
            q //= d
            aux_matrix[i][k] = ("-" if negative else '') + (f"{p}" if q == 1 else f"{p}/{q}")
        if factor != 1:
            aux_steps.append(("divide", i, factor))
    sage_step = [decode_step(step) for step in aux_steps]
    sage_step = '\n'.join(sage_step)
    final_sage_code = ""
    if sage_code_introduction is not None:
        final_sage_code += f"{sage_code_introduction}\n\n"
    final_sage_code += f"```sage\n{sage_variables_definition}\n{sage_matrix_definition}\n{sage_step}\nM\n```"
    st.code(final_sage_code, language="markdown")
    return aux_matrix

def get_variable(value:str, var:str, remove_multiplier: bool = False) -> tuple[list, str]:
    kind = "pure" if "p" in var else ("mixed" if "m" in var else "stats")
    if remove_multiplier:
        var = var.replace("p", "").replace("m", "")
    parts = list(value.split("/"))
    num, den = 0, 0
    if len(parts) == 2:
        num, den = map(int, parts)
    else:
        num, den = int(parts[0]), 1
    
    return [var, [num, den]], kind

def sort_variable(var:list[str, list[int]]) -> int:
    return (-1 if var[1][0] >= 0 else 1, var[0])

def write_equation(equation: list, multiplier:str, first_sign: bool = False):
    st.write(f"writing equation for {multiplier}")
    common = lcm(*[v[1][1] for v in equation])
    all_negative = all(v[1][1] for v in equation)
    if all_negative:
        equation = [[v[0], [-v[1][0], v[1][1]]] for v in equation]

def write_system_solution(matrix, num_stats, solution_introduction = None):
    total = len(matrix[0])
    head = [f"mt_{{{i + 1},{j + 1}}}" for i, j in combinations(range(num_stats), 2)] \
        + [f"pt_{{{i + 1}}}" for i in range(num_stats)] \
        + [f"s_{{{i + 1}}}" for i in range(num_stats)]
    latex_code = ""
    if solution_introduction is not None:
        latex_code += f"{solution_introduction}\n\n"
    latex_code += "$$\\begin{cases}\n"
    for i in range(num_stats):
        depedent, _ = get_variable(matrix[i][i], head[i])
        equation = {"pure":[], "mixed":[], "stats":[]}
        for j in range(num_stats, total):
            free, kind = get_variable(matrix[i][j], head[j], True)
            if kind in ["pure", "mixed"]:
                free[1][0] *= -1
            if free[1][0] != 0:
                equation[kind].append(free)
        latex_code += depedent[0] + "="
        write_equation(equation["pure"], "p")
        write_equation(equation["mixed"], "m", True)
        write_equation(equation["stats"], "1", True)
        latex_code += "\\\\\n"
    latex_code += "$$"
    st.code(latex_code, language="latex")

st.title("System")

with st.expander("Sobre"):
    st.write(
        r"""
        Este sistema gera o código Markdown para uma generalização de um sistema com *n* atributos (stats).

        Ele constrói a matriz estendida de um sistema de equações lineares, dado por:

        $$\displaystyle s_i = pt_i + m \sum_{j \neq i} t_{i,j}$$

        As equações podem ser resolvidas utilizando ferramentas como o [SageMathCell](https://sagecell.sagemath.org).
        """
    )

num_stats = st.number_input("Number of Stats", min_value=2, max_value=10, step=1, value=5, help="Número de atributos (stats) no sistema.")
extended_matrix_introduction = st.text_input("Extended Matrix Introduction", value="the extended matrix is given by:", help="texto de apresentação da matriz estendida.")
extended_matrix_visualization = st.checkbox("visualizar resultado final?")
extended_sage_code_introduction = st.text_input("Sage Code Introduction", value="the sage code is given by:", help="texto de apresentação do codigo sage.")
if st.button("gerar codigo"):
    extended_matrix = generate_extended_matrix(num_stats)
    with st.expander("Extended Matrix"):
        code = write_extended_matrix_markdown(extended_matrix, extended_matrix_introduction)
        if extended_matrix_visualization:
            st.write(code)

    reduced_matrix = None
    with st.expander("Sage Code"):
        reduced_matrix = write_sage_steps(extended_matrix, num_stats, extended_sage_code_introduction, False)
    with st.expander("System Solution"):
        write_system_solution(reduced_matrix, num_stats)
    