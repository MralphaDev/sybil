import os
from datetime import datetime

import pandas as pd
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# ---------- FastAPI 初始化 ----------
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# ---------- 配置 ----------
CSV_FOLDER = "E:\\桌面\\sybil\\backend\\wallets"
ACTION_MAP = {
    "Claim": "C",
    "Batch Claim Token": "B",
    "Transfer": "T",
    "Swap": "S",
    "Approve": "A"
}

# ---------- 读取 CSV 数据 ----------
example_data = []

for filename in os.listdir(CSV_FOLDER):
    if not filename.endswith(".csv"):
        continue

    wallet_id = filename.replace("export-", "").replace(".csv", "").lower()
    df = pd.read_csv(os.path.join(CSV_FOLDER, filename))

    for _, row in df.iterrows():
        timestamp_str = str(row.get("DateTime (UTC)", row.get("timestamp")))
        try:
            ts = datetime.fromisoformat(timestamp_str)
        except ValueError:
            ts = datetime.strptime(timestamp_str, "%Y/%m/%d %H:%M")


        example_data.append({
            "from": row["From"].lower(),
            "to": row["To"].lower(),
            "amount": float(str(row["Amount"]).replace(" BNB", "").strip()),
            "timestamp": ts.isoformat(),
            "method": row["Method"],
            "wallet_id": wallet_id
        })

# ---------- 收集所有 unique wallet ----------
all_wallets = set(
    tx["wallet_id"] for tx in example_data
) | set(tx["from"] for tx in example_data) | set(tx["to"] for tx in example_data)

# ---------- 初始化 nodes ----------
nodes = {w: {"id": w, "behavior_vector": None, "variant": None} for w in all_wallets}

# ---------- 填充 CSV wallet 的行为向量和 variant ----------
for wallet_id in set(tx["wallet_id"] for tx in example_data):
    wallet_txs = [tx for tx in example_data if tx["wallet_id"] == wallet_id]
    wallet_txs.sort(key=lambda x: x["timestamp"])

    tx_cnt = len(wallet_txs)
    avg_amt = sum(tx["amount"] for tx in wallet_txs) / tx_cnt if tx_cnt else 0
    peers = len(set(tx["to"] for tx in wallet_txs))

    first_tx = wallet_txs[0] if wallet_txs else None
    new = 1 if first_tx else 0
    t_min = int(datetime.fromisoformat(first_tx["timestamp"]).timestamp() / 60) if first_tx else 0
    a = first_tx["amount"] if first_tx else 0

    variant_str = "->".join([ACTION_MAP.get(tx["method"], "U") for tx in wallet_txs])

    nodes[wallet_id]["behavior_vector"] = [tx_cnt, avg_amt, peers, new, t_min, a]
    nodes[wallet_id]["variant"] = variant_str

# ---------- 生成 edges ----------
edges = [
    {
        "source": tx["from"],
        "target": tx["wallet_id"],
        "amount": tx["amount"],
        "timestamp": tx["timestamp"],
        "type": "funding"  # 直接 funding
    }
    for tx in example_data
    
]
'''for tx in example_data:
    edges.append({
        "source": tx["from"],
        "target": tx["to"],
        "amount": tx["amount"],
        "timestamp": tx["timestamp"],
        "method": tx["method"],
        "type": "transfer"
    })'''


# ---------- FastAPI endpoint ----------
@app.get("/graph")
def get_graph():
    return {"nodes": list(nodes.values()), "edges": edges}
