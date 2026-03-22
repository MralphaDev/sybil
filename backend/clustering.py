# clustering.py
from collections import defaultdict

def find_connected_components(nodes, edges):
    """
    找所有独立连通分量 (Independent Connected Components)
    
    Args:
        nodes: list of node dicts, 每个 node 需要有 "id"
        edges: list of edge dicts, 每个 edge 需要有 "source" 和 "target"
    
    Returns:
        clusters: list of clusters, 每个 cluster 是 wallet id list
    """

    # 1. 构造邻接表（无向图处理）
    neighbors = defaultdict(set)
    for node in nodes:
        neighbors[node["id"]] = set()
    
    for edge in edges:
        src = edge["source"]
        tgt = edge["target"]
        neighbors[src].add(tgt)
        neighbors[tgt].add(src)  # 当作无向边

    # 2. DFS 找连通分量
    visited = set()
    clusters = []

    for wallet in neighbors.keys():
        if wallet not in visited:
            cluster = []
            stack = [wallet]  # DFS 用 stack
            while stack:
                node = stack.pop()
                if node not in visited:
                    visited.add(node)
                    cluster.append(node)
                    for neighbor in neighbors[node]:
                        if neighbor not in visited:
                            stack.append(neighbor)
            clusters.append(cluster)

    return clusters