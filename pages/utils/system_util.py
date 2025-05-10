from itertools import combinations
from math import lcm
def generate_extended_matrix(num_stats):
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

def generate_auxiliar_matrix(num_stats):
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

def value_format(value, extra=""):
    result = ""
    if isinstance(value, int):
        result = ('+' if value > 0 else '-') + (str(abs(value)) + extra if abs(value) != 1 else '')
    else:
        result = ('+' if not '-' in value else '-') + (value + extra if value != '1' else '')
    return result.replace("--", "+")

def decode_step(step):
    if step[0] == "swap":
        i, j = step[1], step[2]
        return "M[{i}], M[{j}] = M.row({j}), M.row({j})"
    elif step[0] == "subtract":
        i, j, factor = step[1], step[2], step[3]
        return f"M[{j}] = M.row({j}){value_format(-factor, '*')}M.row({i})"
    elif step[0] == "multiply":
        i, factor = step[1], step[2]
        return f"M[{i}] = f{value_format(factor, '*')}M.row({i})"
    elif step[0] == "comment":
        comment = step[1]
        return f"# {comment}"
    elif step[0] == "divide":
        i, factor = step[1], step[2]
        return f"M[{i}] = {'-' if factor < 0 else ''}M.row({i}){'/' + str(abs(factor)) if abs(factor) != 1 else ''}"
    else:
        raise NotImplementedError(f"Unknown step type: {step[0]}")
    
def scale_by_a_factor(matrix, matrix_width, i, j, pivot, ref, steps):
    common_ground = lcm(ref, pivot)
    scale_ref = common_ground // ref
    scale_pivot = common_ground // pivot
    steps.append(("multiply", i, scale_pivot))
    steps.append(("multiply", j, scale_ref))
    for k in range(matrix_width):
        matrix[i][k] *= scale_pivot
        matrix[j][k] *= scale_ref
    return common_ground, common_ground