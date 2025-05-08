from itertools import product
from math import lcm, ceil

def extended_gcd(a, b):
    if b == 0:
        return a, 1, 0
    d, x1, y1 = extended_gcd(b, a % b)
    return d, y1, x1 - (a // b) * y1

def solve_linear(p, m, s):
    d, x0, y0 = extended_gcd(p, m)
    if s % d != 0:
        raise ValueError("No solution exists for the given equation.")
    scale = s // d
    x = x0 * scale
    y = y0 * scale
    dx = lcm(p, m) // p
    dy = lcm(p, m) // m
    return (x, y, dx, dy)  # or return (x, y) if only one is needed

def limit_y(s, m):
    return min(7*3, s//m)

def get_tiers(stats:dict[int, int, int, int], ps:int, ms:int) -> list[list[int]]:
    """
    Gera todas as combinações possíveis de tiers para os atributos STR, DEX, INT e LUK.

    Cada combinação é representada como uma lista de 10 inteiros:
    - Os primeiros 4 representam os tiers puros: STR, DEX, INT e LUK.
    - Os últimos 6 representam os tiers mistos: STR/DEX, STR/INT, STR/LUK, DEX/INT, DEX/LUK, INT/LUK.

    A função considera os valores de ps (escala de bônus puro) e ms (escala de bônus misto) para calcular
    todas as configurações válidas que resultam nos valores finais fornecidos em `stats`.

    Parâmetros:
        stats (dict): Dicionário com os valores finais dos atributos, indexado de 1 a 4.
        ps (int): Valor do tier puro (pure scale).
        ms (int): Valor do tier misto (mixed scale).

    Retorna:
        list[list[int]]: Lista de combinações válidas, cada uma como lista de 10 inteiros.

    Exceções:
        ValueError: Se o dicionário de stats não contiver exatamente 4 valores ou se os valores não forem inteiros.
        ValueError: Se ps ou ms não forem inteiros ou estiverem fora do intervalo permitido (0 a 20).
        ValueError: Se os valores dos atributos forem negativos ou se ps e ms forem ambos zero.
    """
    if len(stats) != 4:
        raise ValueError("O dicionário de stats deve conter exatamente 4 valores.")
    if any(not isinstance(stats[i], int) for i in range(1, 5)):
        raise ValueError("Os valores dos atributos devem ser inteiros.")
    if not isinstance(ps, int) or not isinstance(ms, int):  
        raise ValueError("Os valores de ps e ms devem ser inteiros.")
    if any(stats[i] < 0 for i in range(1, 5)):
        raise ValueError("Os valores dos atributos devem ser não negativos.")
    if ps < 0 or ps > 20:
        raise ValueError("O valor de ps deve estar entre 0 e 20.")
    if ms < 0 or ms > 20:
        raise ValueError("O valor de ms deve estar entre 0 e 20.")
    if ps == 0 and ms == 0:
        raise ValueError("Os valores de ps e ms não podem ser ambos zero.")
    tiers = []
    if ms == 0:
        tier = []
        for i in range(1, 5):
            if stats[i] % ps != 0:
                return tiers
            tier.append(stats[i]//ps)
        tier = tier + [0]*6
        tiers.append(tier)
        return tiers

    STR, DEX, INT, LUK = 1, 2, 3, 4
    stats_tiers = {STR: [], DEX: [], INT: [], LUK: []}
    for i in range(1, 5):
        try:
            x, y, dx, dy = solve_linear(ps, ms, stats[i])
            yL = limit_y(stats[i], ms)
            if x > 7:
                t = ceil((x - 7) / dx)
                x = x - t * dx
                y = y + t * dy
                while x >= 0:
                    if 0 <= y <= yL:
                        stats_tiers[i].append(x)
                    x -= dx
                    y += dy
            elif x < 0:
                t = ceil(-x / dx)
                x = x + t * dx
                y = y - t * dy
                while x <= 7:
                    if 0 <= y <= yL:
                        stats_tiers[i].append(x)
                    x += dx
                    y -= dy
            else:
                if 0 <= y <= yL:
                    stats_tiers[i].append(x)
                if x - dx >= 0:
                    xl = x - dx
                    yl = y + dy
                    while xl >= 0:
                        if 0 <= yl <= yL:
                            stats_tiers[i].append(xl)
                        xl -= dx
                        yl += dy
                if x + dx <= yL:
                    xr = x + dx
                    yr = y - dy
                    while xr <= 7:
                        if 0 <= yr <= yL:
                            stats_tiers[i].append(xr)
                        xr += dx
                        yr -= dy
        except ValueError:
            return []
    if any(len(v) == 0 for v in stats_tiers.values()):
        return tiers
    for combo in product(*[stats_tiers[i] for i in range(1, 5)]):
        t1, t2, t3, t4 = combo
        mixed_stats_total_tier = {
            i: (stats[i] - ps * combo[i - 1]) // ms for i in range(2, 5)
        }
        possibilities = [
            range(min(mixed_stats_total_tier[i], mixed_stats_total_tier[j], 7)+1) for i, j in [(DEX, LUK), (INT, LUK)]
        ]
        for t24, t34 in product(*possibilities):
            aux_t12 = ps*(t3+t4-t1-t2)+(stats[STR]+stats[DEX]-stats[INT]-stats[LUK])
            aux_t13 = ps*(t2+t4-t1-t3)+(stats[STR]+stats[INT]-stats[DEX]-stats[LUK])
            aux_t14 = -ps*t4+stats[LUK]
            aux_t23 = ps*(t1-t2-t3-t4)+(stats[DEX]+stats[INT]+stats[LUK]-stats[STR])
            if not aux_t12%(2*ms) == 0 or not aux_t13%(2*ms) == 0 or not aux_t14%(ms) == 0 or not aux_t23%(2*ms) == 0:
                continue
            t12 = aux_t12//(2*ms)+t34
            t13 = aux_t13//(2*ms)+t24
            t14 = aux_t14//ms-(t24+t34)
            t23 = aux_t23//(2*ms)-(t24+t34)
            tier = [t1, t2, t3, t4, t12, t13, t14, t23, t24, t34]
            if all(0 <= t <= 7 for t in tier):
                tiers.append(tier)
    return tiers

def count_groups_used(tier:list[int]) -> int:
    """
    Conta o número de grupos distintos usados em uma configuração de tiers.

    Os grupos são definidos como:
    - Puro: STR, DEX, INT, LUK (índices 0 a 3)
    - Misto: STR/DEX, STR/INT, STR/LUK, DEX/INT, DEX/LUK, INT/LUK (índices 4 a 9)

    A função retorna o número de grupos distintos usados na configuração.

    Parâmetros:
        tier (list[int]): Lista de 10 inteiros representando a configuração de tiers.
    
    Retorna:
        int: Número de grupos distintos usados na configuração.

    Exceções:
        ValueError: Se a lista de tiers não contiver exatamente 10 valores ou se os valores não forem inteiros.
        ValueError: Se os valores dos tiers estiverem fora do intervalo permitido (0 a 7).
    """
    if len(tier) != 10:
        raise ValueError("A configuração de tiers deve conter exatamente 10 valores.")
    if any(not isinstance(t, int) for t in tier):
        raise ValueError("Todos os valores dos tiers devem ser inteiros.")
    if any(t < 0 or t > 7 for t in tier):
        raise ValueError("Os valores dos tiers devem estar entre 0 e 7.")
    return sum(1 for v in tier if v > 0)

def calcular_ps_ms_por_nivel(nivel:int) -> tuple[int, int]:
    """
    Calcula os valores de ps e ms com base no nível do equipamento.
    Os valores são determinados de acordo com as seguintes regras:
    - Nível < 200: ps = nível // 20 + 1, ms = nível // 40 + 1
    - Nível < 250: ps = 11 (ou 12 se nível >= 230), ms = 6
    - Nível >= 250: ps = 12, ms = 7

    Parâmetros:
        nivel (int): Nível do equipamento.
    
    Retorna:
        tuple[int, int]: Valores de ps e ms correspondentes ao nível do equipamento.

    Exceções:
        ValueError: Se o nível não for um inteiro ou estiver fora do intervalo de 0 a 300.
    """
    if not isinstance(nivel, int):
        raise ValueError("O nível deve ser um número inteiro.")
    if nivel < 0 or nivel > 300:
        raise ValueError("O nível deve estar entre 0 e 300.")
    ps, ms = 0, 0
    if nivel < 200:
        ps = nivel // 20 + 1
        ms = nivel // 40 + 1
    elif nivel < 250:
        ps = 11 if nivel < 230 else 12
        ms = 6
    else:
        ps, ms = 12, 7
    return ps, ms

def get_max_theorical_value(lv:int) -> int:
    """
    Calcula o valor máximo teórico que pode ser alcançado com os atributos primários (STR, DEX, INT, LUK)
    com base no nível do equipamento.

    O valor máximo é calculado como:
    max_value = 7 * ps + 3 * 7 * ms

    onde ps é o valor do tier puro e ms é o valor do tier misto.
    Os valores de ps e ms são determinados pela função `calcular_ps_ms_por_nivel`.
    O nível do equipamento deve ser um inteiro entre 0 e 300.
    A função retorna o valor máximo teórico que pode ser alcançado com os atributos primários.

    Parâmetros:
        lv (int): Nível do equipamento.
    
    Retorna:
        int: Valor máximo teórico que pode ser alcançado com os atributos primários.

    Exceções:
        ValueError: Se o nível não for um inteiro ou estiver fora do intervalo de 0 a 300.
    """
    if not isinstance(lv, int):
        raise ValueError("O nível deve ser um número inteiro.")
    if lv < 0 or lv > 300:
        raise ValueError("O nível deve estar entre 0 e 300.")
    ps, ms = calcular_ps_ms_por_nivel(lv)
    return 7*ps + 3*7*ms