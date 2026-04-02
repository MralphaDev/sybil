# behv_analysis.py
import numpy as np
from Levenshtein import ratio as levenshtein_ratio

# ---------------------------
# behv_analysis_improved.py
# 改良版行为相似度函数（continuous decay + 可调 scale）
# ---------------------------

import numpy as np
from Levenshtein import ratio as levenshtein_ratio

def tx_sim(tx_i, tx_j):
    return min(1, min(tx_i, tx_j) / max(tx_i, tx_j))

# ---------------------------
# 交易金额相似度
# ---------------------------
def amt_sim(amt_i, amt_j):
    if max(amt_i, amt_j) <= 0.002:
        return 1
    else:
        return min(1, min(amt_i, amt_j) / max(amt_i, amt_j))


def time_sim(ti, tj, scale=2.2):
    """
    时间间隔相似度
    - delta <= 5 → similarity = 1
    - delta >= 15 → similarity ≈ 0
    - 中间平滑指数衰减
    """
    delta = abs(ti - tj)
    if delta <= 5:
        return 1
    return np.exp(-(delta - 5)/scale)


# ---------------------------
# 行为向量相似度
# ---------------------------
def behavior_sim(w1, w2, weights=(1/3, 1/3, 1/3)):
    """
    综合行为向量相似度
    w1, w2: dict, 包含 'behavior_vector': [tx_cnt, t_min, first_amt]
    weights: 对应 tx_cnt, first_amt, t_min 的权重
    """
    f1 = tx_sim(w1["behavior_vector"][0], w2["behavior_vector"][0])
    f2 = amt_sim(w1["behavior_vector"][2], w2["behavior_vector"][2])
    f3 = time_sim(w1["behavior_vector"][1], w2["behavior_vector"][1])
    
    # 加权平均
    sim = weights[0]*f1 + weights[1]*f2 + weights[2]*f3
    return sim

def variant_similarity(wallet1_data, wallet2_data):
    """
    计算两个钱包 variant 字符串的相似度
    Args:
        wallet1_data, wallet2_data: dict，包含 'variant' 字段
    Returns:
        float: 0~1，相似度
    """
    v1 = wallet1_data.get("variant", "")
    v2 = wallet2_data.get("variant", "")
    if not v1 or not v2:
        return 0.0  # 缺失 variant 时返回 0
    return float(levenshtein_ratio(v1, v2))

# ---------------------------
# compute_behavior_similarity
# ---------------------------
def compute_behavior_similarity(nodes, weights=(1/3, 1/3, 1/3)):
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


def wallet_behavior_similarity(wallet1_data, wallet2_data, variant_weight=0.5, weights=(1/3,1/3,1/3)):
    """
    对比两个钱包综合相似度（行为向量 + variant）
    Args:
        wallet1_data, wallet2_data: dict，包含 'behavior_vector' 和 'variant'
        variant_weight: variant权重
        weights: 行为向量加权
    Returns:
        float: 0~1 相似度
    """
    b_sim = behavior_sim(wallet1_data, wallet2_data, weights)
    v_sim = variant_similarity(wallet1_data, wallet2_data)
    return variant_weight * v_sim + (1 - variant_weight) * b_sim

def tx_distance(w1, w2):
    return 1 - tx_sim(w1["behavior_vector"][0], w2["behavior_vector"][0])

def amt_distance(w1, w2):
    return 1 - amt_sim(w1["behavior_vector"][2], w2["behavior_vector"][2])

def time_distance(w1, w2):
    return 1 - time_sim(w1["behavior_vector"][1], w2["behavior_vector"][1])


# ---------------------------
# 综合分析
# ---------------------------
def analyze_similarity(nodes, variant_weight=0.5, weights=(1/3, 1/3, 1/3)):
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
    
    
