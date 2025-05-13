import streamlit as st, textwrap
from pages.utils.system_util import generate_extended_matrix, generate_auxiliar_matrix, decode_step, apply_row_elimination, convert_matrix
from math import gcd, lcm
from itertools import combinations

def write_extended_matrix_markdown(matrix:list[list[str]], extended_matrix_introduction: str = "") -> str:
    markdown = extended_matrix_introduction
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
    if markdown:
        markdown += "\n"
    markdown += code
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

def sort_variable(var:list[str, list[int]]) -> tuple[int, str]:
    return (-1 if var[1][0] >= 0 else 1, var[0])

def write_equation_formater(num: int) -> str:
    return str(num) if num not in [-1, 1] else f"{'' if num == 1 else '-'}"

def get_value(i: int, v: list[str, list[int, int]], m:int = 1) -> str:
    sign = ''
    if v[1][0] >= 0:
        sign += '+' if i > 0 else ''
    else:
        sign += '-'
    body = f"{write_equation_formater(abs(v[1][0]*(m//v[1][1])))}{v[0]}"
    return sign + body

def write_equation(equation: list, multiplier:str, first_sign: bool = False):
    res = ""
    if len(equation) == 0:
        return res
    all_negative = all(v[1][0] < 0 for v in equation)
    if all_negative:
        equation = [[v[0], [-v[1][0], v[1][1]]] for v in equation]
    common = lcm(*[v[1][1] for v in equation])
    sign = "-" if all_negative else ("+" if first_sign else "")
    if common == 1:
        if len(equation) == 1:
            v = equation[0]
            body = f"{write_equation_formater(v[1][0])}{multiplier.replace('1', '')}{v[0]}"
            res = sign + body
        else:
            right = ''.join(get_value(i, v) for i, v in enumerate(sorted(equation, key=sort_variable)))
            body = f"{multiplier.replace('1', '')}({right})"
            res = sign + body
    else:
        if len(equation) == 1:
            v = equation[0]
            uper = f"{write_equation_formater(v[1][0])}{multiplier.replace('1', '')}{v[0]}"
            lower = f"{v[1][1]}"
            body = f"\\frac{{{uper}}}{{{lower}}}"
            res = sign + body
        else:
            uper = f"{multiplier}"
            lower = f"{common}"
            right = ''.join(get_value(i, v, common) for i, v in enumerate(sorted(equation, key=sort_variable)))
            body = f"\\frac{{{uper}}}{{{lower}}}({right})"
            res = sign + body
    return res

def write_system_solution(matrix:list[list[str]], num_stats:int, solution_introduction:str = "") -> str:
    converted = convert_matrix(matrix, num_stats)
    markdown = solution_introduction
    if markdown:
        markdown += "\n\n"
    latex_code = "$$\\begin{cases}\n"
    for i, row in enumerate(converted):
        depedent, equations = row["depedent"], row["equations"]
        latex_code += depedent[0] + "="
        latex_code += write_equation(equations["pure"], "p")
        latex_code += write_equation(equations["mixed"], "m", True)
        latex_code += write_equation(equations["stats"], "1", True)
        latex_code += ("\\\\" if i < num_stats - 1 else "") + "\n"
    latex_code += "\\end{cases}$$"
    markdown += latex_code
    st.code(markdown, language="latex")
    return latex_code

def write_system_verification(matrix:list[list[str]], num_stats:int, verification_introduction:str = "") -> str:
    converted = convert_matrix(matrix, num_stats, True)
    markdown = verification_introduction
    if markdown:
        markdown += "\n\n"
    head = ''.join(['c'] + ['c']*sum(len(eq) for eq in converted[0]))
    latex_code = f"\\left\\begin{{array}}{{{head}}}\n"

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
extended_matrix_visualization = st.checkbox("visualizar resultado final?",key=0)
extended_sage_code_introduction = st.text_input("Sage Code Introduction", value="the sage code is given by:", help="texto de apresentação do codigo sage.")
solution_introduction = st.text_input("solution inntroduction", value="the solution is given by:", help="texto de apresentação da solução do sistema")
solution_visualization = st.checkbox("visualizar resultado final?",key=1)
verification_introduction = st.text_input("verification introduction", value="you can verify the solution using the following things", help="texto de apresentação da verificação")
if st.button("gerar codigo"):
    extended_matrix = generate_extended_matrix(num_stats)
    with st.expander("Extended Matrix"):
        code = write_extended_matrix_markdown(extended_matrix, extended_matrix_introduction)
        if extended_matrix_visualization:
            code = code.replace("$$", "")
            st.latex(code)

    reduced_matrix = None
    with st.expander("Sage Code"):
        reduced_matrix = write_sage_steps(extended_matrix, num_stats, extended_sage_code_introduction, False)

    with st.expander("System Solution"):
        code = write_system_solution(reduced_matrix, num_stats, solution_introduction)
        if solution_visualization:
            code = code.replace("$$", "")
            st.latex(code)
    
    with st.expander("verification"):
        write_system_verification(reduced_matrix, num_stats, verification_introduction)