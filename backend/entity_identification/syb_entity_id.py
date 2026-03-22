# syb_entity_id.py
from .entity_id_cex import fund_backtracking, group_by_upper_funder

def identify_sybil_entities(dbscan_clusters, edges):
    """
    Identify sybil entities across clusters using upper funder backtracking.
    """
    all_results = {}

    for cluster_idx, cluster_data in dbscan_clusters.items():
        subgroups = cluster_data["subgroups"]
        noise = cluster_data["noise"]

        subgroup_to_funder, funder_to_subgroups = group_by_upper_funder(subgroups, edges)

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

    return all_results