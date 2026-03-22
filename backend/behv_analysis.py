# behv_analysis.py
import numpy as np
from Levenshtein import ratio as levenshtein_ratio

# ---------------------------
# 行为相似度函数
# ---------------------------
def tx_sim(tx_i, tx_j, alpha=0.05):
    if max(tx_i, tx_j) <= 10:
        return max(0, 1 - alpha * abs(tx_i - tx_j))
    else:
        return min(1, min(tx_i, tx_j) / max(tx_i, tx_j))

def amt_sim(amt_i, amt_j):
    if max(amt_i, amt_j) <= 0.002:
        return 1
    else:
        return min(1, min(amt_i, amt_j) / max(amt_i, amt_j))

def time_sim(ti, tj):
    delta = abs(ti - tj)
    if delta <= 5:
        return 1
    else:
        return max(0, 1 - 0.1 * ((delta - 5)/5))

def behavior_sim(w1, w2, weights=(0.3, 0.35, 0.35)):
    """
    w1, w2: dict, 包含 'behavior_vector': [tx_cnt, t_min, first_amt]
    """
    f1 = tx_sim(w1["behavior_vector"][0], w2["behavior_vector"][0])
    f2 = amt_sim(w1["behavior_vector"][2], w2["behavior_vector"][2])
    f3 = time_sim(w1["behavior_vector"][1], w2["behavior_vector"][1])
    return weights[0]*f1 + weights[1]*f2 + weights[2]*f3

# ---------------------------
# compute_behavior_similarity
# ---------------------------
def compute_behavior_similarity(nodes, weights=(0.3, 0.35, 0.35)):
    """
    使用 DBSCAN 示例的行为相似度计算方法，返回 pairwise similarity dict
    """
    similarity = {}
    n = len(nodes)
    ids = [node['id'] for node in nodes]

    for i in range(n):
        for j in range(i+1, n):
            w1 = nodes[i]
            w2 = nodes[j]
            sim = behavior_sim(w1, w2, weights=weights)
            similarity[f"{ids[i]}-{ids[j]}"] = float(sim)

    return similarity

# ---------------------------
# Variant 相似度（原样）
# ---------------------------
def compute_variant_similarity(nodes):
    similarity = {}
    n = len(nodes)
    variants = {node['id']: node['variant'] for node in nodes}

    for i in range(n):
        for j in range(i + 1, n):
            w1, w2 = nodes[i]['id'], nodes[j]['id']
            v1, v2 = variants[w1], variants[w2]
            sim_ratio = levenshtein_ratio(v1, v2)
            similarity[f"{w1}-{w2}"] = float(sim_ratio)

    return similarity

# ---------------------------
# 综合分析
# ---------------------------
def analyze_similarity(nodes, variant_weight=0.5, weights=(0.3, 0.35, 0.35)):
    """
    综合行为 + variant 相似度
    """
    behavior_sim_dict = compute_behavior_similarity(nodes, weights=weights)
    variant_sim_dict = compute_variant_similarity(nodes)

    weighted_sim = {}
    for key in behavior_sim_dict.keys():
        weighted_sim[key] = float(
            variant_weight * variant_sim_dict[key] + (1 - variant_weight) * behavior_sim_dict[key]
        )

    return {
        "behavior": behavior_sim_dict,
        "variant": variant_sim_dict,
        "weighted": weighted_sim
    }