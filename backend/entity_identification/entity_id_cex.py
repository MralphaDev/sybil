import numpy as np
from sklearn.cluster import DBSCAN
from Levenshtein import ratio as levenshtein_ratio
from behv_analysis import behavior_sim

def analyze_subgroup_clusters_global(dbscan_clusters, nodes, variant_weight=0.5, eps=0.2, min_samples=2):
    """
    对所有 cluster 的 subgroups 做全局 DBSCAN
    1. 每个 subgroup 聚合行为向量
    2. subgroup 间 pairwise 综合相似度（行为 + variant 平均）
    3. 全局 DBSCAN
    4. 打印每个 subgroup 行为向量 + 每类包含的 subgroup
    """
    wallet_map = {node['id']: node for node in nodes}
    all_subgroups = []

    # ---------------------------
    # 1. 把所有 cluster 的 subgroup 抽出来
    # ---------------------------
    for cluster_idx, cluster_data in dbscan_clusters.items():
        subgroups = cluster_data["subgroups"]
        for sub_id, wallet_list in subgroups.items():
            vectors = np.array([wallet_map[w]['behavior_vector'] for w in wallet_list if w in wallet_map])
            if len(vectors) == 0:
                continue
            agg_vector = vectors.mean(axis=0).tolist()
            all_subgroups.append({
                "id": f"{cluster_idx}_{sub_id}",  # 全局唯一 id
                "behavior_vector": agg_vector,
                "wallets": wallet_list
            })

    n = len(all_subgroups)
    if n == 0:
       # print("[Global] No valid subgroups for analysis.")
        return {}

    # ---------------------------
    # 2. 计算综合相似度
    # ---------------------------
    weighted_sim = {}
    for i in range(n):
        for j in range(i + 1, n):
            w1, w2 = all_subgroups[i], all_subgroups[j]

            # 行为相似度
            b_sim = behavior_sim(w1, w2)

            # variant pairwise wallet 平均
            wallets_i, wallets_j = w1['wallets'], w2['wallets']
            sims = [levenshtein_ratio(wallet_map[wi]['variant'], wallet_map[wj]['variant'])
                    for wi in wallets_i for wj in wallets_j]
            avg_variant_sim = float(np.mean(sims)) if sims else 0

            weighted_sim[f"{w1['id']}-{w2['id']}"] = float(variant_weight * avg_variant_sim + (1 - variant_weight) * b_sim)

    # ---------------------------
    # 3. 转距离矩阵
    # ---------------------------
    sim_matrix = np.ones((n, n))
    id_to_idx = {all_subgroups[i]['id']: i for i in range(n)}
    for key, sim in weighted_sim.items():
        i_id, j_id = key.split("-")
        i_idx = id_to_idx[i_id]
        j_idx = id_to_idx[j_id]
        sim_matrix[i_idx, j_idx] = sim
        sim_matrix[j_idx, i_idx] = sim

    dist_matrix = 1 - sim_matrix

    # ---------------------------
    # 4. DBSCAN
    # ---------------------------
    db = DBSCAN(eps=eps, min_samples=min_samples, metric='precomputed')
    labels = db.fit_predict(dist_matrix)
    labels = [int(x) for x in labels]

    # ---------------------------
    # 5. 打印输出
    # ---------------------------
    '''print("\n[Global] All Subgroup Aggregated Behavior Vectors:")
    for sub in all_subgroups:
        print(f"  Subgroup {sub['id']}: {sub['behavior_vector']}")'''

    label_to_subgroups = {}
    for idx, label in enumerate(labels):
        label_to_subgroups.setdefault(label, []).append(all_subgroups[idx]['id'])

    #print("\n[Global] DBSCAN Subgroup Clusters:")
    '''for label, subs in label_to_subgroups.items():
        print(f"  Cluster {label}: {subs}")'''

    # ---------------------------
    # 6. 返回结果
    # ---------------------------
    subgroup_dbscan_result = {all_subgroups[i]['id']: labels[i] for i in range(n)}
    return {
        "agg_subgroups": all_subgroups,
        "subgroup_dbscan": subgroup_dbscan_result
    }