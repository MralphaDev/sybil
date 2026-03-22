# entity_id_cex.py
from collections import defaultdict

def fund_backtracking(edges, wallets):
    """
    Backtrack each wallet to its uppermost funder.
    
    Args:
        edges: List of dicts with 'source', 'target', 'amount', 'timestamp'
        wallets: List of wallet IDs to backtrack
    
    Returns:
        dict: {wallet_id: uppermost_funder}
    """
    # Build a simple parent mapping
    parent_map = {}
    for edge in edges:
        target = edge["target"]
        source = edge["source"]
        parent_map[target] = source

    def trace_to_top(wallet):
        visited = set()
        current = wallet
        while current in parent_map and current not in visited:
            visited.add(current)
            current = parent_map[current]
        return current

    result = {wallet: trace_to_top(wallet) for wallet in wallets}
    return result


def group_by_upper_funder(cluster_subgroups, edges):
    """
    Groups subgroups that share the same uppermost funder
    """
    subgroup_to_funder = {}
    funder_to_subgroups = defaultdict(list)

    for sub_label, wallets in cluster_subgroups.items():
        backtrack_res = fund_backtracking(edges, wallets)
        # pick majority upper funder in this subgroup
        funders = list(backtrack_res.values())
        majority_funder = max(set(funders), key=funders.count)
        subgroup_to_funder[sub_label] = majority_funder
        funder_to_subgroups[majority_funder].append(sub_label)

    return subgroup_to_funder, funder_to_subgroups