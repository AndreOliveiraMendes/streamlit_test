import streamlit as st
from itertools import product

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

    #t1*, t2*, t3*, t4*, t12, t13, t14, t23, t24*, t34*
    for combo in product(*[stats_tiers[i] for i in range(1, 5)]):
        t1, t2, t3, t4 = combo
        s1, s2, s3, s4 = stats.values()
        mixed_stats_total_tier = {
            i: (stats[i] - ps * combo[i - 1]) // ms for i in range(1, 5)
        }
        possibilities = [
            list(range(min(7, mixed_stats_total_tier[i], mixed_stats_total_tier[j]) + 1))
            for i, j in [(2, 4), (3, 4)]
        ]
        for free_mixed_tiers in product(*possibilities):
            t24, t34 = free_mixed_tiers
            t12 = ps*(t3+t4-t1-t2)+(s1+s2-s3-s4)
            t13 = ps*(t2+t4-t1-t3)+(s1+s3-s2-s4)
            t14 = -ps*t4+s4
            t23 = ps*(t1-t2-t3-t4)+(s2+s3+s4-s1)
            mod = 2*ms
            if t12%mod != 0 or t13%mod != 0 or t14%ms != 0 or t23%mod != 0: #check for possible non integer tiers
                continue
            t12 = t12//mod + ms*t34
            t13 = t13//mod + ms*t24
            t14 = t14//ms - ms*(t24+t34)
            t23 = t23//mod - ms*(t24+t34)
            possible_tiers = [t12, t13, t14, t23, t24, t34]
            if any(t > 7 for t in possible_tiers):
                continue
            tier = list(combo) + possible_tiers
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