import streamlit as st
from itertools import combinations
from pages.flame import get_tiers, count_groups_used

st.title("Small Helper Calculator for MapleStory Bonus Stat")

st.markdown("Insira os valores finais de cada atributo bônus:")

theorical_max = 20

col1, col2 = st.columns(2)
with col1:
    str_val = st.number_input("STR", min_value=0, max_value=4*theorical_max, step=1, value=0)
    int_val = st.number_input("INT", min_value=0, max_value=4*theorical_max, step=1, value=0)
with col2:
    dex_val = st.number_input("DEX", min_value=0, max_value=4*theorical_max, step=1, value=0)
    luk_val = st.number_input("LUK", min_value=0, max_value=4*theorical_max, step=1, value=0)

stats = {1: str_val, 2: dex_val, 3: int_val, 4: luk_val}

ps = st.number_input("Valor de cada Tier Puro (ex: 4)", min_value=1, max_value = 20, step=1, value=4)
ms = st.number_input("Valor de cada Tier Misto (ex: 2)", min_value=1, max_value = 20, step=1, value=2)
max_groups = st.number_input("Número máximo de grupos distintos de 1 a 4 (0 = ilimitado)", min_value=0, max_value=4, value=4)

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
            for label, value in zip(pair_labels, values):
                if value > 0:
                    st.write(f"({'MISTO' if '/' in label else 'PURO'}) **{label}**: {value}")