import csv
import random
import os
from datetime import datetime, timedelta

# Config
num_csvs = 200
min_clusters = 10
max_clusters = 20
folder_name = "wallet-gen"

# Create folder
os.makedirs(folder_name, exist_ok=True)

nametags = ["alice.bnb", "bob.bnb", "charlie.bnb", "999o999.bnb", "xyz.bnb", "demo.bnb"]

def random_tx_hash():
    return "0x" + "".join(random.choices("0123456789abcdef", k=64))

def random_address():
    return "0x" + "".join(random.choices("0123456789abcdef", k=40))

def random_amount():
    amount = round(random.uniform(0.00005, 0.001), 6)
    usd_value = round(amount * random.uniform(2000, 4000), 2)
    return f"{amount} BNB", f"${usd_value}"

def random_fee():
    return round(random.uniform(0.000002, 0.000005), 8)

base_time = datetime.utcnow()
used_addresses = set()

# Decide number of clusters
num_clusters = random.randint(min_clusters, max_clusters)

# Split CSVs roughly per cluster
cluster_sizes = []
remaining_csvs = num_csvs
for i in range(num_clusters):
    if i == num_clusters - 1:
        cluster_sizes.append(remaining_csvs)
    else:
        size = random.randint(10, 20)
        cluster_sizes.append(size)
        remaining_csvs -= size

csv_counter = 0

for cluster_id, cluster_size in enumerate(cluster_sizes, start=1):
    cluster_wallets = []

    # Create wallets for cluster
    for _ in range(cluster_size):
        while True:
            addr = random_address()
            if addr not in used_addresses:
                used_addresses.add(addr)
                cluster_wallets.append(addr)
                break

    # Generate transactions within cluster
    for i, to_addr in enumerate(cluster_wallets):
        if i == 0:
            # First wallet is "externally funded"
            from_addr = random_address()
            while from_addr in used_addresses:
                from_addr = random_address()
            used_addresses.add(from_addr)
        else:
            # Funded by earlier wallet in cluster (random choice)
            from_addr = random.choice(cluster_wallets[:i])

        tx_hash = random_tx_hash()
        blockno = random.randint(80000000, 90000000)
        dt = (base_time - timedelta(minutes=random.randint(0, 20000))).strftime("%Y/%m/%d %H:%M")
        amount, value = random_amount()
        fee = random_fee()

        # CSV file named after from_addr
        file_name = f"export-{from_addr}.csv"
        file_path = os.path.join(folder_name, file_name)

        with open(file_path, mode="w", newline="") as file:
            writer = csv.writer(file)

            # Header
            writer.writerow([
                "Transaction Hash", "Status", "Method", "Blockno", "DateTime (UTC)", 
                "From", "From_Nametag", "To", "To_Nametag", "Amount", "Value (USD)", "Txn Fee"
            ])

            # Single row
            writer.writerow([
                tx_hash,
                "Success",
                "Ai Sign",
                blockno,
                dt,
                from_addr,
                random.choice(nametags),
                to_addr,
                random.choice(nametags),
                amount,
                value,
                fee
            ])

        csv_counter += 1

print(f"✅ Generated {csv_counter} CSV files in '{folder_name}' folder with clustered patterns")

'''import csv
import random
import os
from datetime import datetime, timedelta

# Config
num_files = 350
folder_name = "wallet-gen"

# Create folder
os.makedirs(folder_name, exist_ok=True)

nametags = ["alice.bnb", "bob.bnb", "charlie.bnb", "999o999.bnb", "xyz.bnb", "demo.bnb"]

def random_tx_hash():
    return "0x" + "".join(random.choices("0123456789abcdef", k=64))

def random_address():
    return "0x" + "".join(random.choices("0123456789abcdef", k=40))

def random_amount():
    amount = round(random.uniform(0.00005, 0.001), 6)
    usd_value = round(amount * random.uniform(2000, 4000), 2)
    return f"{amount} BNB", f"${usd_value}"

def random_fee():
    return round(random.uniform(0.000002, 0.000005), 8)

base_time = datetime.utcnow()
used_addresses = set()

for _ in range(num_files):
    # Unique addresses
    while True:
        from_addr = random_address()
        if from_addr not in used_addresses:
            used_addresses.add(from_addr)
            break

    while True:
        to_addr = random_address()
        if to_addr not in used_addresses:
            used_addresses.add(to_addr)
            break

    tx_hash = random_tx_hash()
    blockno = random.randint(80000000, 90000000)
    dt = (base_time - timedelta(minutes=random.randint(0, 10000))).strftime("%Y/%m/%d %H:%M")
    amount, value = random_amount()
    fee = random_fee()

    # File named after from_addr
    file_name = f"export-{from_addr}.csv"
    file_path = os.path.join(folder_name, file_name)

    with open(file_path, mode="w", newline="") as file:
        writer = csv.writer(file)

        # Header
        writer.writerow([
            "Transaction Hash", "Status", "Method", "Blockno", "DateTime (UTC)", 
            "From", "From_Nametag", "To", "To_Nametag", "Amount", "Value (USD)", "Txn Fee"
        ])

        # Single row
        writer.writerow([
            tx_hash,
            "Success",
            "Ai Sign",
            blockno,
            dt,
            from_addr,
            random.choice(nametags),
            to_addr,
            random.choice(nametags),
            amount,
            value,
            fee
        ])

print(f"✅ Generated {num_files} CSV files in '{folder_name}' folder with filenames based on From address")'''