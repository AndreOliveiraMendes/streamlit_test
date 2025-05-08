import streamlit as st
from itertools import combinations
from pages.utils.flame_util import get_tiers, count_groups_used, get_max_theorical_value, calcular_ps_ms_por_nivel

MAX_LEVEL = 300
DEFAULT_PURE_SCALE = 12
DEFAULT_MIXED_SCALE = 7

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

st.title("Maplestory Helper - Flame Calculator")

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

theorical_max = get_max_theorical_value(MAX_LEVEL)

st.caption(f"⚠️ Valor máximo teórico por atributo primário: {theorical_max} (nível {MAX_LEVEL})")

col1, col2 = st.columns(2)
with col1:
    str_val = st.number_input("STR", min_value=0, max_value=theorical_max, step=1, value=0)
    int_val = st.number_input("INT", min_value=0, max_value=theorical_max, step=1, value=0)
with col2:
    dex_val = st.number_input("DEX", min_value=0, max_value=theorical_max, step=1, value=0)
    luk_val = st.number_input("LUK", min_value=0, max_value=theorical_max, step=1, value=0)

STR, DEX, INT, LUK = 1, 2, 3, 4
stats = {STR: str_val, DEX: dex_val, INT: int_val, LUK: luk_val}

if not "ps" in st.session_state:
    st.session_state.ps = DEFAULT_PURE_SCALE
if not "ms" in st.session_state:
    st.session_state.ms = DEFAULT_MIXED_SCALE

col3, col4 = st.columns(2)
with col3:
    ps = st.number_input("Valor de cada Tier Puro (ex: 12)", min_value=1, max_value=20, step=1, key="ps")
with col4:
    ms = st.number_input("Valor de cada Tier Misto (ex: 7)", min_value=0, max_value=20, step=1, key="ms")

st.number_input("Nível do equipamento (ex: 250)",on_change=atualizar_por_nivel, min_value=0, max_value=300, step=1, key="nivel", help="insira o nivel do equipamento ou deixe 0 se deseja inserir manualmente os valores de referencia dos atributos puro e misto")
max_groups = st.number_input("Número máximo de grupos distintos de 1 a 4.", min_value=1, max_value=4, value=4)
if st.button("Calcular Configurações Possíveis"):
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