from .entity_id_no_cex import group_by_upper_funder, fund_backtracking
from .entity_id_cex import analyze_subgroup_clusters_global
from behv_analysis import wallet_behavior_similarity


def identify_sybil_entities(
    dbscan_clusters,
    nodes,
    edges,
    variant_weight=0.5,
    eps=0.2,
    min_samples=2,
    global_dbscan=False,
    TH_VOTE=2,
    SIMILARITY_THRESHOLD=85,
    similarity_votes_required=1
):  
    # 需要关注的 noise 地址
    watchlist = {
        #"0x6505a6796114f2d33594a813eb7de70252cfffa5",
       # "0x8388e08cf351e49cd42367139095a87f4c59493d",
        #"0xa05eb62941a8c849be32e7ead82791d71babc970",
       # "0x2b9872fe1cf487c153cdcc5674314a2d8d466817",
       # "0xfb229c1933ad1b6e5b5fec7fcce33b77e1542305",
       # "0xf2c9b8fc47edcc4d7d5b476b36066aa8ae56f2d5",
       # "0x9621ef6fd1fe043b6c6e417aa8176850341445b6"
       "0xfad0e965d95606b8cec10a0ad5b6a9bb55ff321b",
       "0xecb43b8131b8a1f0cc49bbf621cb8fdd8d94020b",
       "0x042372edfc96bab5abd04bf2d2d1f3dd32de9958",
       "0xe5c04669a8d135f66834c5581e4b2e415ae6a639",
       "0x1a4bf851bd14027fcf9ae18244be018393d6067d",
       "0x92c25d8cd64a805efbf26f6b348e96db339c81ea",
       "0x30f33154588c36c5270f82ba1d6a70b41a26b2c7"
       
    }

    
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
    # 构建钱包数据映射表
    # ---------------------------
    # ✅ FIX 1: 全部 lower
    wallet_data_map = {node["id"].lower(): node for node in nodes}

    for cluster_idx, cluster_data in dbscan_clusters.items():
        subgroups = cluster_data["subgroups"]
        noise = cluster_data["noise"]

        subgroup_to_funder, funder_to_subgroups = group_by_upper_funder(subgroups, edges)

        # ---------------------------
        # 当前cluster非noise钱包
        # ---------------------------
        cluster_wallets = []
        for wallets in subgroups.values():
            cluster_wallets.extend(wallets)

        # ---------------------------
        # 构建 source -> list(target)
        # ---------------------------
        edges_by_source = {}
        for e in edges:
            src = e["source"].lower()
            tgt = e["target"].lower()
            edges_by_source.setdefault(src, []).append(tgt)
        
        edges_by_target = {}
        for e in edges:
            src = e["source"].lower()
            tgt = e["target"].lower()
            edges_by_target.setdefault(tgt, []).append(src)
    
        # ---------------------------
        # recovered_noise 判定
        # ---------------------------
        recovered_noise = []

        for noise_addr in noise:
            votes = 0
            noise_lower = noise_addr.lower()
            detail_log = []  # 用于收集打印信息

            # ---------------------------
            # 1️⃣ Backtrack 投票
            # ---------------------------
            top_funder_map = fund_backtracking(edges, [noise_addr])

            # ✅ FIX 2: 防止 key 不存在
            noise_top_funder = top_funder_map.get(noise_addr)
            if noise_top_funder and noise_top_funder in funder_to_subgroups:
                # 基础分
                base_score = 0.5

                # 🔹 检查是否是交易所 / hub 钱包
                # 如果 source 在 edges_by_source 里有 outgoing edge，就认为是 hub
                is_hub = noise_top_funder.lower() in edges_by_source #NEED TO FIX THIS LATER!! CUZ SOME HUB CANNOT BE BACKTRACKED FURTHER LOGICALLY BUT EDGE RELATIONSHIP PRESERVES

                if is_hub:
                    # 降低分数
                    backtrack_score = base_score * 0.4 # 0.2
                     # 🔹 funder 支持多个 subgroup 加分
                    subgroups_list = funder_to_subgroups.get(noise_top_funder, [])
                    num_subgroups = len(subgroups_list) if subgroups_list else 0
                    if num_subgroups > 1:
                        extra = min(1 - backtrack_score, 0.2 * (num_subgroups - 1))
                        backtrack_score += extra

                else:
                    # 普通 funder
                    backtrack_score = base_score

                    # 🔹 funder 支持多个 subgroup 加分
                    subgroups_list = funder_to_subgroups.get(noise_top_funder, [])
                    num_subgroups = len(subgroups_list) if subgroups_list else 0
                    
                    if num_subgroups > 1:
                        # 将多 subgroup 加分按比例加入，不超过 1
                        extra = min(1 - backtrack_score, 0.2 * (num_subgroups - 1))
                        backtrack_score += extra

                votes += backtrack_score
                detail_log.append(f"Backtrack: top_funder={noise_top_funder}, is_hub={is_hub}, num_subgroups={num_subgroups if not is_hub else 0}, score={backtrack_score:.2f}")

            # ---------------------------
            # 2️⃣ 行为 + variant 投票
            # ---------------------------
            noise_node = wallet_data_map.get(noise_lower)
            sim_score = 0

            if noise_node:
                sim_list = []
                for wallet in cluster_wallets:
                    wallet_node = wallet_data_map.get(wallet.lower())
                    if not wallet_node:
                        continue
                    # 计算行为相似度
                    sim = wallet_behavior_similarity(
                        noise_node,
                        wallet_node,
                        variant_weight=variant_weight
                    )
                    sim_list.append(sim)

                # 按相似度降序累加，保证高相似度先贡献分值
                sim_list.sort(reverse=True)

                for sim in sim_list:
                    if sim >= 0.9:
                        sim_score += 0.5
                    elif sim >= 0.8:
                        sim_score += 0.25
                    # cap 1
                    if sim_score >= 1:
                        sim_score = 1
                        break

            votes += sim_score
            detail_log.append(f"Behavior: sim_score={sim_score:.2f}")

            # ---------------------------
            # 3️⃣ funding 投票（核心修复）
            # ---------------------------
            # ---------------------------
            # 🧠 Sybil Detection Note (Star / Tree Pattern)
            # ---------------------------
            # 在女巫识别中（尤其是 star / tree 分发结构）：
            #
            # 1️⃣ incoming fund（cluster → noise）= 强控制信号
            #    - 表示该钱包是由 cluster 内钱包直接派生 / 资助
            #    - 强相关：通常属于同一实体控制（核心特征）
            #
            # 2️⃣ outgoing fund（noise → cluster）= 次级行为信号
            #    - 可能是资金归集、交互或随机转账
            #    - 不一定代表控制关系
            #
            # 👉 因此权重设计：
            #    incoming > outgoing
            #
            # 推荐：
            #    incoming  = 1.0
            #    outgoing  = 0.5
            #
            # 🧠 进阶优化（可选）：
            #    - 不仅判断是否存在关系，还可以统计连接数量（density）
            #    - 多个 incoming 来源 = 更强的女巫信号
            #
            # 核心原则：
            #    控制关系 > 行为关系
            # ---------------------------
            funded_wallets = []

            # ---------------------------
            # Outgoing: noise -> cluster subgroups
            # ---------------------------
            for sg, wallets in subgroups.items():
                for wallet in wallets:
                    if wallet.lower() in edges_by_source.get(noise_lower, []):
                        votes += 0.5  # 每笔 funding +0.5
                        funded_wallets.append(wallet)

            # ---------------------------
            # Incoming: cluster subgroups -> noise
            # ---------------------------
            for sg, wallets in subgroups.items():
                for wallet in wallets:
                    if wallet.lower() in edges_by_target.get(noise_lower, []):
                        votes += 1  # 控制信号，固定 +1
                        break  # first-funding graph, 只会有一个
            
            # ---------------------------
            # 5️⃣ 输出关注 wallet 的详细投票信息
            # ---------------------------
            '''if noise_addr in watchlist:
                print(f"\n=== Noise Wallet: {noise_addr} ===")
                for line in detail_log:
                    print("  " + line)
                print(f"  Total votes: {votes:.2f}")
                print("============================")'''


            # ---------------------------
            # 4️⃣ 判定
            # ---------------------------
            if votes >= TH_VOTE:
                recovered_noise.append(noise_addr)

        # ---------------------------
        # 保存结果
        # ---------------------------
        all_results[cluster_idx] = {
            "subgroup_to_funder": subgroup_to_funder,
            "funder_to_subgroups": funder_to_subgroups,
            "noise": noise,
            "recovered_noise": recovered_noise
        }

    # ---------------------------
    # aggregated relations（未动）
    # ---------------------------
    aggregated_relations = []

    if global_result:
        subgroup_dbscan = global_result.get("subgroup_dbscan", {})

        label_to_all = {}
        for sg_key, label in subgroup_dbscan.items():
            if label == -1:
                continue
            label_to_all.setdefault(label, []).append(sg_key)

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