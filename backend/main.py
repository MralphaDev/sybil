import os
from datetime import datetime
from pathlib import Path
import pandas as pd
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fund_graph_construct import build_nodes, build_edges
from clustering import find_connected_components
from behv_analysis import analyze_similarity
from dbscan import run_dbscan_on_clusters
from entity_identification.syb_entity_id import identify_sybil_entities

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

    df = pd.read_csv(CSV_FOLDER / filename)
    
     # --------- 清洗列名 ----------
    df.columns = df.columns.str.strip()          # 去掉前后空格
    df.columns = df.columns.str.replace("\ufeff", "")  # 去掉 BOM 隐藏字符（Excel CSV 常见）
    
        # 如果 CSV 为空，也添加一个占位记录，保证 wallet_id 被记录
    if df.empty:
        csv_data.append({
            "from": None,
            "to": None,
            "amount": 0.0,
            "timestamp": None,
            "method": None,
            "wallet_id": wallet_id
        })
        continue


    for _, row in df.iterrows():

        timestamp_str = str(row.get("DateTime (UTC)", row.get("timestamp")))
        

        try:
            ts = datetime.fromisoformat(timestamp_str)
        except ValueError:
            ts = datetime.strptime(timestamp_str, "%Y/%m/%d %H:%M")

        csv_data.append({
            "from": row["From"].lower(),
            "to": row["To"].lower(),
            "amount": float(str(row["Amount"]).replace(" BNB", "").strip()),
            "timestamp": ts.isoformat(),
            "method": row["Method"],
            "wallet_id": wallet_id
        })


# ---------- suspicious wallets (CSV addresses only) ----------
suspicious_wallets = set(tx["wallet_id"] for tx in csv_data)

# ---------- 行为分析 ----------
nodes = build_nodes(csv_data, suspicious_wallets, ACTION_MAP)

# ---------- edges ----------
edges = build_edges(csv_data, suspicious_wallets)

# ---------- clustering ----------
clusters = find_connected_components(nodes, edges)
num_clusters = len(clusters)

print(f"Total ICCs found: {num_clusters}")
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




# ---------- API ----------
@app.get("/graph")

def get_graph():
 # 对 dbscan_results 做处理，保证 label 连续，从 0 开始，同时单独列出噪声
    api_dbscan = {}

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
        
         # Identify sybil entities based on backtracking
        sybil_entities = identify_sybil_entities(api_dbscan, edges)
    return {
        "nodes": nodes,
        "edges": edges,
        "clusters": clusters,
        "num_clusters": num_clusters,
        "similarities": similarities,
        "dbscan": api_dbscan,  # 新增 dbscan 结果
        "sybil_entities": sybil_entities   # 新增 sybil entity 结果
    }