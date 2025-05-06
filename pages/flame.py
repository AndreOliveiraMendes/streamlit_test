from itertools import product, combinations

def get_tiers(stats, ps, ms):
    stats_tiers, tiers = {1: [], 2: [], 3: [], 4: []}, []
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
            list(range(min(mixed_stats_total_tier[i], mixed_stats_total_tier[j]) + 1))
            for i, j in combinations(range(1, 5), 2)
        ]
        for possible_tiers in product(*possibilities):
            s = {}
            s[1] = combo[0] * ps + sum(possible_tiers[i] for i in [0, 1, 2]) * ms
            s[2] = combo[1] * ps + sum(possible_tiers[i] for i in [0, 3, 5]) * ms
            s[3] = combo[2] * ps + sum(possible_tiers[i] for i in [1, 3, 5]) * ms
            s[4] = combo[3] * ps + sum(possible_tiers[i] for i in [2, 4, 5]) * ms
            if all(s[i] == stats[i] for i in range(1, 5)):
                tier = list(combo) + list(possible_tiers)
                tiers.append(tier)
    return tiers

def count_groups_used(tier):
    return sum(1 for v in tier if v > 0)