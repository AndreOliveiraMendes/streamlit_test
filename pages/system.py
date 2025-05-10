import streamlit as st, textwrap
from pages.utils.system_util import generate_extended_matrix, generate_auxiliar_matrix, decode_step, scale_by_a_factor, value_format
from math import gcd, lcm
from itertools import combinations

def write_extended_matrix_markdown(matrix, extended_matrix_introduction = None):
    header_size = len(matrix[0])
    header = ''.join(['c']*(header_size - 1) + [':c'])
    content = '\\\\\n'.join(['&'.join(map(str, row)) for row in matrix])
    markdown = textwrap.dedent(f"""
    $$
    \\left[\\begin{{array}}{{{header}}}
    {content}
    \\end{{array}}\\right]
    $$
    """).replace("\t", "").replace("    ", "").replace("&s", "&s_")
    if extended_matrix_introduction:
        markdown = f"{extended_matrix_introduction}\n{markdown}"
    st.code(markdown, language="latex")

def write_sage_steps(matrix, num_stats, sage_code_introduction = None, ignore_comments = True):
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
            if (ref := aux_matrix[j][i]) == 0:
                continue
            if ref%pivot != 0:
                ref, pivot = scale_by_a_factor(aux_matrix, matrix_width, i, j, pivot, ref, aux_steps)
            factor = ref // pivot
            for k in range(matrix_width):
                aux_matrix[j][k] -= factor * aux_matrix[i][k]
            aux_steps.append(("subtract", i, j, factor))
    if not ignore_comments:
        aux_steps.append(("comment", "second step: back substitution"))
    for i in range(num_stats-1, -1, -1):
        pivot = aux_matrix[i][i]
        for j in range(i - 1, -1, -1):
            if(ref := aux_matrix[j][i]) == 0:
                continue
            if ref%pivot != 0:
                ref, pivot = scale_by_a_factor(aux_matrix, matrix_width, i, j, pivot, ref, aux_steps)
            factor = aux_matrix[j][i] // aux_matrix[i][i]
            for k in range(matrix_width):
                aux_matrix[j][k] -= factor * aux_matrix[i][k]
            aux_steps.append(("subtract", i, j, factor))
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

def get_variable(value:str, var:str, remove_multiplier = False):
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

def sort_variable(var):
    return (-1 if var[1][0] >= 0 else 1, var[0])

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
        pure_common = lcm(*[val[1][1] for val in equation["pure"]])
        if len(equation["pure"]) > 1:
            pure_part_open, pure_part_close = "p(", ")+"
            if pure_common > 1:
                pure_part_open = f"\\frac{{p}}{{{pure_common}}}("
            latex_code += pure_part_open
            latex_code += ''.join(value_format(var[1][0]) + var[0] for var in sorted(equation["pure"], key=sort_variable))
            latex_code += pure_part_close
        elif (q := equation['pure'][0][1][1]) != 1:
            latex_code += f"\\frac{{{value_format(equation['pure'][0][1][0])}p}}{{{q}}}"
        else:
            latex_code += f"{value_format(equation['pure'][0][0])}p"
        mixed_common = lcm(*[val[1][1] for val in equation["mixed"]])
        stats_common = lcm(*[val[1][1] for val in equation["stats"]])
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
extended_sage_code_introduction = st.text_input("Sage Code Introduction", value="the sage code is given by:", help="texto de apresentação do codigo sage.")
if st.button("gerar codigo"):
    extended_matrix = generate_extended_matrix(num_stats)
    with st.expander("Extended Matrix"):
        write_extended_matrix_markdown(extended_matrix, extended_matrix_introduction)
    reduced_matrix = None
    with st.expander("Sage Code"):
        reduced_matrix = write_sage_steps(extended_matrix, num_stats, extended_sage_code_introduction, False)
    with st.expander("System Solution"):
        write_system_solution(reduced_matrix, num_stats)
    