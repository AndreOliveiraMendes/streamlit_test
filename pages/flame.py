import streamlit as st
from itertools import product, combinations

st.title("Small Helper Calculator for MapleStory Bonus Stat")

st.sidebar.title("Links de Referência e Utilitarios")

st.sidebar.markdown("[🧠 Ajuda (Wiki)](https://maplestorywiki.net/w/Bonus_Stats)")

st.sidebar.markdown("[📊 Calculadora de Bonus Stats](https://www.whackybeanz.com/calc/equips/setup)")

with st.expander("Como funciona"):
    st.write(
        """
        O MapleStory tem um sistema de bônus de atributos que pode ser dividido em dois tipos: **puro** e **misto**.
        - **Puro**: o bônus é aplicado diretamente a um único atributo.
        - **Misto**: o bônus é dividido entre dois atributos.

        O valor aplicado a cada um depende do nível do equipamento, que determina o valor de cada tier puro e misto.

        Insira os valores finais de STR, DEX, INT e LUK que você deseja verificar. A calculadora mostrará todas as possíveis combinações de bônus que resultam nesses valores, considerando os tiers puros e mistos.

        O nível do equipamento é opcional, mas pode ser usado para definir automaticamente os valores de cada tier.
        """
    )

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
        for t in range(8):
            if stats[i] - ps * t >= 0 and (stats[i] - ps * t) % ms == 0:
                stats_tiers[i].append(t)
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

def atualizar_por_nivel() -> None:
    """
    Atualiza os valores de ps e ms com base no nível do equipamento.
    A função é chamada quando o nível do equipamento é alterado na interface do usuário.
    O nível é obtido do estado da sessão do Streamlit.
    Os valores de ps e ms são calculados usando a função `calcular_ps_ms_por_nivel`.
    Os valores de ps e ms são armazenados no estado da sessão do Streamlit.

    Parâmetros:
        None
    
    Retorna:
        None
    """
    ps, ms = calcular_ps_ms_por_nivel(st.session_state.nivel)
    st.session_state.ps = ps
    st.session_state.ms = ms

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

max_lv = 300
theorical_max = get_max_theorical_value(max_lv)

st.caption(f"⚠️ Valor máximo teórico por atributo primário: {theorical_max} (nível {max_lv})")

col1, col2 = st.columns(2)
with col1:
    str_val = st.number_input("STR", min_value=0, max_value=theorical_max, step=1, value=0)
    int_val = st.number_input("INT", min_value=0, max_value=theorical_max, step=1, value=0)
with col2:
    dex_val = st.number_input("DEX", min_value=0, max_value=theorical_max, step=1, value=0)
    luk_val = st.number_input("LUK", min_value=0, max_value=theorical_max, step=1, value=0)

STR, DEX, INT, LUK = 1, 2, 3, 4
stats = {STR: str_val, DEX: dex_val, INT: int_val, LUK: luk_val}

col3, col4 = st.columns(2)
with col3:
    ps = st.number_input("Valor de cada Tier Puro (ex: 12)", min_value=1, max_value=20, step=1, key="ps")
with col4:
    ms = st.number_input("Valor de cada Tier Misto (ex: 7)", min_value=0, max_value=20, step=1, key="ms")
st.number_input("Nível do equipamento (ex: 250)",on_change=atualizar_por_nivel, min_value=0, max_value=300, step=1, key="nivel", help="insira o nivel do equipamento ou deixe 0 se deseja inserir manualmente os valores de referencia dos atributos puro e misto")
max_groups = st.number_input("Número máximo de grupos distintos de 1 a 4. o valor 0 sera considerado 4.", min_value=0, max_value=4, value=4)
if st.button("Calcular Configurações Possíveis"):
    if max_groups == 0 or max_groups > 4:
        max_groups = 4
    tiers = get_tiers(stats, ps, ms)
    filtered = list(filter(lambda t: count_groups_used(t) <= max_groups, tiers))

    if not filtered:
        st.error("Nenhuma combinação possível com os valores fornecidos.")
    else:
        st.success(f"Foram encontradas {len(filtered)} combinações possíveis.")
        pair_labels = ["STR", "DEX", "INT", "LUK"] + [f"{a}/{b}" for a, b in combinations(["STR", "DEX", "INT", "LUK"], 2)]
        for i, tier in enumerate(sorted(filtered, key=lambda t: count_groups_used(t)), 1):
            opt = count_groups_used(tier)
            st.subheader(f"{i}ª configuração — usa {opt} grupo(s) de flame:")
            values = [t * (ps if idx < 4 else ms) for idx, t in enumerate(tier)]
            for label, value, t in zip(pair_labels, values, tier):
                if value > 0:
                    st.write(f"({'MISTO' if '/' in label else 'PURO'}) **{label}**: {value} (tier {t})")
                    #st.markdown(f"""**({'MISTO' if '/' in label else 'PURO'})** <abbr title="Tier {t}">**{label}**: {value}</abbr>""", unsafe_allow_html=True)