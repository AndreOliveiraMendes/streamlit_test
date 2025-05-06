import streamlit as st
from itertools import product, combinations

st.title("Small Helper Calculator for MapleStory Bonus Stat")

st.sidebar.markdown("[🧠 Ajuda (Wiki)](https://maplestorywiki.net/w/Bonus_Stats)")

def get_tiers(stats, ps, ms):
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

    stats_tiers = {1: [], 2: [], 3: [], 4: []}
    for i in range(1, 5):
        for t in range(8):
            if stats[i] - ps * t >= 0 and (stats[i] - ps * t) % ms == 0:
                stats_tiers[i].append(t)
    if any(len(v) == 0 for v in stats_tiers.values()):
        return tiers

    for combo in product(*[stats_tiers[i] for i in range(1, 5)]):
        mixed_stats_total_tier = {
            i: (stats[i] - ps * combo[i - 1]) // ms for i in range(1, 5)
        }
        possibilities = [
            list(range(min(7, mixed_stats_total_tier[i], mixed_stats_total_tier[j]) + 1))
            for i, j in combinations(range(1, 5), 2)
        ]
        for possible_tiers in product(*possibilities):
            s = {}
            s[1] = combo[0] * ps + sum(possible_tiers[i] for i in [0, 1, 2]) * ms
            s[2] = combo[1] * ps + sum(possible_tiers[i] for i in [0, 3, 4]) * ms
            s[3] = combo[2] * ps + sum(possible_tiers[i] for i in [1, 3, 5]) * ms
            s[4] = combo[3] * ps + sum(possible_tiers[i] for i in [2, 4, 5]) * ms
            if all(s[i] == stats[i] for i in range(1, 5)):
                tier = list(combo) + list(possible_tiers)
                tiers.append(tier)
    return tiers

def count_groups_used(tier):
    return sum(1 for v in tier if v > 0)

theorical_max = 20*7

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