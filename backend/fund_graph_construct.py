from datetime import datetime


def build_nodes(csv_data, suspicious_wallets, ACTION_MAP):

    nodes = []

    for wallet in suspicious_wallets:

        wallet_txs = [tx for tx in csv_data if tx["wallet_id"] == wallet]

        wallet_txs.sort(key=lambda x: x["timestamp"])

        tx_cnt = len(wallet_txs)

        avg_amt = (
            sum(tx["amount"] for tx in wallet_txs) / tx_cnt
            if tx_cnt else 0
        )

        #peers = len(set(tx["to"] for tx in wallet_txs))

        first_tx = wallet_txs[0] if wallet_txs else None

        #new_wallet = 1 if first_tx else 0

        t_min = (
            int(datetime.fromisoformat(first_tx["timestamp"]).timestamp() / 60)
            if first_tx else 0
        )

        first_amt = first_tx["amount"] if first_tx else 0

        variant = "->".join([
            ACTION_MAP.get(tx["method"], "U")
            for tx in wallet_txs
        ])

        node = {
            "id": wallet,
            "behavior_vector": [
                tx_cnt,
                #avg_amt,
                #peers,
                #new_wallet,
                t_min,
                first_amt
                
            ],
            "variant": variant
        }

        nodes.append(node)

    return nodes


def build_edges(csv_data, suspicious_wallets):

    edges = []

    for wallet in suspicious_wallets:

        wallet_txs = [
            tx for tx in csv_data
            #if tx["wallet_id"] == wallet
        ]

        if not wallet_txs:
            continue

        # 时间排序
        wallet_txs.sort(key=lambda x: x["timestamp"])

        first_funding = None

        for tx in wallet_txs:

            sender = tx["from"].lower()
            receiver = tx["to"].lower()
            amount = tx["amount"]

            # 只找真正 funding
            if (
                receiver == wallet
                and sender != wallet
                and amount > 0
            ):
                first_funding = tx
                break

        if first_funding:

            edges.append({
                "source": first_funding["from"],
                "target": wallet,
                "amount": first_funding["amount"],
                "timestamp": first_funding["timestamp"],
                "type": "first_funding"
            })

    return edges

    