from .entity_id_no_cex import group_by_upper_funder
from .entity_id_cex import analyze_subgroup_clusters_global

def identify_sybil_entities(dbscan_clusters, nodes, edges, variant_weight=0.5, eps=0.1, min_samples=2, global_dbscan=False):

    all_results = {}

    # ---------------------------
    # 全局 DBSCAN
    # ---------------------------
    if global_dbscan:
        global_result = analyze_subgroup_clusters_global(
            dbscan_clusters,
            nodes,
            variant_weight=variant_weight,
            eps=eps,
            min_samples=min_samples
        )
    else:
        global_result = None

    # ---------------------------
    # 1. 原始 sybil
    # ---------------------------
    for cluster_idx, cluster_data in dbscan_clusters.items():
        subgroups = cluster_data["subgroups"]
        noise = cluster_data["noise"]

        subgroup_to_funder, funder_to_subgroups = group_by_upper_funder(subgroups, edges)

        all_results[cluster_idx] = {
            "subgroup_to_funder": subgroup_to_funder,
            "funder_to_subgroups": funder_to_subgroups,
            "noise": noise,
        }

    # ---------------------------
    # 2. NEW: aggregated relations
    # ---------------------------
    aggregated_relations = []

    if global_result:
        subgroup_dbscan = global_result.get("subgroup_dbscan", {})

        # label -> 所有 subgroup key
        label_to_all = {}
        for sg_key, label in subgroup_dbscan.items():
            if label == -1:
                continue
            label_to_all.setdefault(label, []).append(sg_key)

        # 遍历 all_results（这里才是对的）
        for cluster_idx, data in all_results.items():
            funder_to_subgroups = data["funder_to_subgroups"]

            for funder, subgroups_list in funder_to_subgroups.items():
                if not subgroups_list:
                    continue

                related_outer = []

                for sg in subgroups_list:
                    sg_key = f"{cluster_idx}_{sg}"
                    label = subgroup_dbscan.get(sg_key, -1)

                    if label == -1:
                        continue

                    for other in label_to_all.get(label, []):
                        if other == sg_key:
                            continue

                        other_cluster, other_sg = other.split("_")

                        if int(other_cluster) != int(cluster_idx):
                            related_outer.append({
                                "from": sg,
                                "to_cluster": int(other_cluster),
                                "to_subgroup": int(other_sg)
                            })

                # 去重
                related_outer = list({
                    (d["from"], d["to_cluster"], d["to_subgroup"]): d
                    for d in related_outer
                }.values())

                aggregated_relations.append({
                    "cluster": cluster_idx,
                    "funder": funder,
                    "subgroups": subgroups_list,
                    "related_outer": related_outer
                })

    return all_results, global_result, aggregated_relations

'''# syb_entity_id.py
from .entity_id_no_cex import group_by_upper_funder

def identify_sybil_entities(dbscan_clusters, nodes, edges):
    """
    Identify sybil entities across clusters using upper funder backtracking.
    """
    all_results = {}
    
# 假设 dbscan_clusters 是一个列表或 NumPy 数组
    #print("dbscan_clusters[0]:", dbscan_clusters[0])

    for cluster_idx, cluster_data in dbscan_clusters.items():
        
        subgroups = cluster_data["subgroups"]
        noise = cluster_data["noise"]

        subgroup_to_funder, funder_to_subgroups = group_by_upper_funder(subgroups, edges)

        print("result:",dbscan_clusters[0])
        # Nice console output
        print(f"\n=== Cluster {cluster_idx} Sybil Entity Analysis ===")
        for funder, sub_labels in funder_to_subgroups.items():
            wallets_in_group = sum([subgroups[s] for s in sub_labels], [])
            print(f"Upper Funder: {funder}")
            print(f"  Subgroups: {sub_labels}")
            print(f"  Wallets: {wallets_in_group}\n")

        # save for API / graph endpoint
        all_results[cluster_idx] = {
            "subgroup_to_funder": subgroup_to_funder,
            "funder_to_subgroups": funder_to_subgroups,
            "noise": noise
        }

    return all_results'''