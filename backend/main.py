import os
import numpy as np
from datetime import datetime
from pathlib import Path
import pandas as pd
from sklearn.metrics import silhouette_score
import re
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fund_graph_construct import build_nodes, build_edges
from clustering import find_connected_components
from behv_analysis import analyze_similarity
from behv_analysis import tx_distance, amt_distance, time_distance
from dbscan import run_dbscan_on_clusters
from behv_analysis import behavior_sim, variant_similarity, wallet_behavior_similarity
from entity_identification.syb_entity_id import identify_sybil_entities
from itertools import combinations

# ---------- FastAPI ----------
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# ---------- 配置 ----------
BASE_DIR = Path(__file__).resolve().parent
CSV_FOLDER = BASE_DIR / "wallets"

ACTION_MAP = {
    "Claim": "C",
    "Batch Claim Token": "B",
    "Transfer": "T",
    "Swap": "S",
    "Approve": "A",
    "Batch Transfer": "BT"
}

# ---------- 读取 CSV ----------
csv_data = []

for filename in os.listdir(str(CSV_FOLDER)):
    if not filename.endswith(".csv"):
        continue

    wallet_id = filename.replace("export-", "").replace(".csv", "").lower()
    
    try:
        df = pd.read_csv(CSV_FOLDER / filename)
        
        # --------- 清洗列名 ----------
        df.columns = df.columns.str.strip()          # 去掉前后空格
        df.columns = df.columns.str.replace("\ufeff", "")  # 去掉 BOM 隐藏字符（Excel CSV 常见）
        
        # 如果 CSV 有列但没数据，df 也可能为空
        if df.empty:
            raise ValueError("Empty CSV with columns but no data")
    except (pd.errors.EmptyDataError, ValueError):
        # 如果 CSV 为空，也添加一个占位记录，保证 wallet_id 被记录

            csv_data.append({
                "from": "none",
                "to": "none",
                "amount": 0.0,
                "timestamp": "0",  # ⚠️ 必须是字符串
                "method": "-",
                "wallet_id": wallet_id
            })
            continue

        # 先把时间列转换成 datetime
    df['timestamp_dt'] = pd.to_datetime(df.get("DateTime (UTC)", df.get("timestamp")), errors='coerce')
    df = df.sort_values('timestamp_dt')  # 排序 DataFrame
    for _, row in df.iterrows():

        timestamp_str = str(row.get("DateTime (UTC)", row.get("timestamp")))
        if pd.isna(timestamp_str) or str(timestamp_str).strip() == "":
            timestamp_str = "1970-01-01T00:00:00"

        try:
            ts = datetime.fromisoformat(timestamp_str)
        except ValueError:
            ts = datetime.strptime(timestamp_str, "%Y/%m/%d %H:%M")

        csv_data.append({
            "from": row["From"].lower(),
            "to": row["To"].lower(),
            #"amount": float(str(row["Amount"]).replace(" BNB", "").strip()),
            #"amount":float(str(row["Amount"]).replace(" BNB", "").replace(" ETH", "").strip()),
            "amount": float(re.sub(r"[^0-9.]", "", str(row["Amount"]))),
            "timestamp": ts.isoformat(),
            "method": row["Method"],
            "wallet_id": wallet_id
        })


# ---------- suspicious wallets (CSV addresses only) ----------
suspicious_wallets = set(tx["wallet_id"] for tx in csv_data)

# ---------- 行为分析 ----------
nodes = build_nodes(csv_data, suspicious_wallets, ACTION_MAP)
# ---------- 转成 wallet_id -> node 映射，方便查找 ----------
nodes_map = {
    n["id"]: {
        "behavior_vector": n["behavior_vector"],
        "variant": n["variant"]
    }
    for n in nodes
}

    
# ---------- edges ----------
edges = build_edges(csv_data, suspicious_wallets)

# ---------- clustering ----------
clusters = find_connected_components(nodes, edges)
num_clusters = len(clusters)

#print(f"Total ICCs found: {num_clusters}")
'''for i, cluster in enumerate(clusters):
    print(f"Cluster {i+1}: {cluster}")'''

# ---------- Similarities ----------
similarities = analyze_similarity(nodes)

# ---------- DBSCAN on each cluster ----------
# min_samples=3, eps_percentile=40 可以调节
dbscan_results = run_dbscan_on_clusters(nodes, clusters, similarities['weighted'], min_samples=2)

# 打印到 console
'''print("\n--- DBSCAN results within each cluster ---")
for c_idx, cluster_res in dbscan_results.items():
    subclusters = {}
    for wallet, label in cluster_res.items():
        subclusters.setdefault(label, []).append(wallet)
    print(f"Cluster {c_idx}: {len(subclusters)} subclusters -> {subclusters}")'''




@app.get("/graph")
def get_graph():
    api_dbscan = {}
    subg_vectors_map = {}  # 存每个 cluster 的 subg 的 vectors/variants/cohesion

    for c_idx, cluster_res in dbscan_results.items():
        # 重编号子群 label 从 0 开始
        non_noise_labels = sorted(l for l in set(cluster_res.values()) if l != -1)
        label_map = {old:new for new, old in enumerate(non_noise_labels)}

        cluster_output = {"subgroups": {}, "noise": []}

        for wallet, label in cluster_res.items():
            if label == -1:
                cluster_output["noise"].append(wallet)
            else:
                new_label = label_map[label]
                cluster_output["subgroups"].setdefault(new_label, []).append(wallet)

        api_dbscan[c_idx] = cluster_output

        # ----------------------
        # 计算每个子群 cohesion
        subg_vectors_map[c_idx] = {}
        for subg_label, wallets in cluster_output["subgroups"].items():
            if len(wallets) < 2:
                subg_vectors_map[c_idx][subg_label] = {
                    "vectors": [nodes_map[w]["behavior_vector"] for w in wallets if w in nodes_map],
                    "cohesion": None
                }
                continue

            valid_wallets = [w for w in wallets if w in nodes_map]

            sims = []
            for w1, w2 in combinations(valid_wallets, 2):
                sim = wallet_behavior_similarity(nodes_map[w1], nodes_map[w2], variant_weight=0.5)
                sims.append(sim)
            cohesion = float(np.mean(sims)) if sims else None

            subg_vectors_map[c_idx][subg_label] = {
                "wallets": valid_wallets,
                #"wallets": wallets,
                #"vectors": [nodes_map[w]["behavior_vector"] for w in wallets if w in nodes_map],
                #"variants": [nodes_map[w]["variant"] for w in wallets if w in nodes_map],
                "cohesion": cohesion

            }

        # ----------------------
        # 计算 cluster 内所有 subg 对的距离（四类）
        subg_labels = list(cluster_output["subgroups"].keys())
        subgroup_distances = {
            "composite": {},
            "time": {},
            "tx": {},
            "fund": {},
            "variant": {}
        }

        for sg1, sg2 in combinations(subg_labels, 2):
            wallets1 = subg_vectors_map[c_idx][sg1]["wallets"]
            wallets2 = subg_vectors_map[c_idx][sg2]["wallets"]
            if not wallets1 or not wallets2:
                continue

            comp_sims = []
            time_dists = []
            tx_dists = []
            amt_dists = []
            variant_dists = []

            for w1 in wallets1:
                for w2 in wallets2:
                    comp_sim = wallet_behavior_similarity(nodes_map[w1], nodes_map[w2], variant_weight=0.5)
                    comp_sims.append(comp_sim)

                    time_dists.append(time_distance(nodes_map[w1], nodes_map[w2]))
                    tx_dists.append(tx_distance(nodes_map[w1], nodes_map[w2]))
                    amt_dists.append(amt_distance(nodes_map[w1], nodes_map[w2]))
                    variant_dists.append(1 - variant_similarity(nodes_map[w1], nodes_map[w2]))

            avg_comp = 1.0 - float(np.mean(comp_sims)) if comp_sims else 0.0
            avg_time = float(np.mean(time_dists)) if time_dists else 0.0
            avg_tx = float(np.mean(tx_dists)) if tx_dists else 0.0
            avg_amt = float(np.mean(amt_dists)) if amt_dists else 0.0
            avg_variant = float(np.mean(variant_dists)) if variant_dists else 0.0

            key = f"{sg1}-{sg2}"
            subgroup_distances["composite"][key] = avg_comp
            subgroup_distances["time"][key] = avg_time
            subgroup_distances["tx"][key] = avg_tx
            subgroup_distances["fund"][key] = avg_amt
            subgroup_distances["variant"][key] = avg_variant

        # ✅ 必须在 loop 外
        subg_vectors_map[c_idx]["subgroup_distances"] = subgroup_distances

        # ----------------------
        # ✅ 正确计算每个 subgroup 的 average（论文表格）
        subg_avg_metrics = {}

        for sg in subg_labels:
            comp_vals = []
            time_vals = []
            tx_vals = []
            fund_vals = []
            variant_vals = []

            for other in subg_labels:
                if sg == other:
                    continue

                key1 = f"{sg}-{other}"
                key2 = f"{other}-{sg}"
                key = key1 if key1 in subgroup_distances["composite"] else key2

                if key not in subgroup_distances["composite"]:
                    continue

                comp_vals.append(subgroup_distances["composite"][key])
                time_vals.append(subgroup_distances["time"][key])
                tx_vals.append(subgroup_distances["tx"][key])
                fund_vals.append(subgroup_distances["fund"][key])
                variant_vals.append(subgroup_distances["variant"][key])

            subg_avg_metrics[sg] = {
                "composite": float(np.mean(comp_vals)) if comp_vals else 0.0,
                #"time": float(np.mean(time_vals)) if time_vals else 0.0,
                #"tx": float(np.mean(tx_vals)) if tx_vals else 0.0,
                #"fund": float(np.mean(fund_vals)) if fund_vals else 0.0,
                #"variant": float(np.mean(variant_vals)) if variant_vals else 0.0,
            }

        subg_vectors_map[c_idx]["subgroup_avg"] = subg_avg_metrics

        # ----------------------
        # 移除临时 wallets 字段
        for sg_label in cluster_output["subgroups"].keys():
            subg_vectors_map[c_idx][sg_label].pop("wallets", None)

    # Identify sybil entities
    sybil_entities, global_result, aggregated_relations = identify_sybil_entities(
        api_dbscan,
        nodes,
        edges,
        variant_weight=0.5,
        eps=0.1,
        min_samples=2,
        global_dbscan=True
    )

    return {
        "nodes": nodes,
        "edges": edges,
        "clusters": clusters,
        "num_clusters": num_clusters,
        #"similarities": similarities,
        "dbscan": api_dbscan,
        "sybil_entities": sybil_entities,
        "global_result": global_result,
        "aggregated_relations": aggregated_relations,
        "subg_vectors": subg_vectors_map,
    }