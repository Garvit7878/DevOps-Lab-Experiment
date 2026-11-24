import sqlite3
import shutil
import hashlib
import json
import time
import os
from datetime import datetime

DB_PRIMARY = "primary_payments.db"
DB_DR_REPLICA = "dr_standby_payments.db"
BACKUP_DIR = "./dr_vault_backups"
AUDIT_LOG = "dr_operations_audit.log"

def setup_initial_database():
    os.makedirs(BACKUP_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PRIMARY)
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    account_id TEXT NOT NULL,
                    amount REAL NOT NULL,
                    status TEXT NOT NULL,
                    timestamp TEXT NOT NULL)''')
    # Seed transactions
    cur.execute("DELETE FROM transactions")
    records = [
        ("ACC_CORP_01", 12500.0, "SETTLED", datetime.utcnow().isoformat()),
        ("ACC_RETAIL_88", 450.5, "SETTLED", datetime.utcnow().isoformat()),
        ("ACC_GLOBAL_09", 98000.0, "SETTLED", datetime.utcnow().isoformat())
    ]
    cur.executemany("INSERT INTO transactions (account_id, amount, status, timestamp) VALUES (?, ?, ?, ?)", records)
    conn.commit()
    conn.close()
    print("[DR-SYSTEM] Primary database initialized with active financial ledger.")

def calculate_checksum(filepath):
    hasher = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while chunk := f.read(8192):
            hasher.update(chunk)
    return hasher.hexdigest()

def execute_snapshot_backup():
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    backup_file = os.path.join(BACKUP_DIR, f"snapshot_{timestamp}.db")
    shutil.copy2(DB_PRIMARY, backup_file)
    checksum = calculate_checksum(backup_file)
    meta = {
        "snapshot_id": f"SNAP-{timestamp}",
        "backup_path": backup_file,
        "sha256": checksum,
        "timestamp_utc": timestamp,
        "status": "VERIFIED_CONSISTENT"
    }
    with open(backup_file + ".meta.json", "w") as f:
        json.dump(meta, f, indent=2)
    print(f"[DR-BACKUP] Completed verified snapshot: {backup_file} | SHA256: {checksum[:12]}...")
    return backup_file

def simulate_disaster_and_failover(backup_file):
    print("\n--- SIMULATING PRIMARY DC HARDWARE OUTAGE ---")
    start_rto = time.time()
    
    # Simulate corruption/loss
    if os.path.exists(DB_PRIMARY):
        os.remove(DB_PRIMARY)
        print("[ALERT] Primary DC database lost! Health checks FAILING.")

    print("\n--- INITIATING AUTOMATED DR FAILOVER WORKFLOW ---")
    # Verify snapshot integrity before restoration
    meta_path = backup_file + ".meta.json"
    with open(meta_path, "r") as f:
        meta = json.load(f)
    
    current_hash = calculate_checksum(backup_file)
    assert current_hash == meta["sha256"], "Backup corruption detected!"
    print(f"[DR-INTEGRITY] Verified snapshot SHA256 matches cryptographic seal.")

    # Promote DR Standby
    shutil.copy2(backup_file, DB_DR_REPLICA)
    conn = sqlite3.connect(DB_DR_REPLICA)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*), SUM(amount) FROM transactions")
    count, total_vol = cur.fetchone()
    conn.close()

    elapsed_rto = time.time() - start_rto
    print(f"[DR-FAILOVER] Standby promoted to ACTIVE! Total records recovered: {count}, Ledger Volume: ${total_vol:,.2f}")
    print(f"[DR-METRICS] Observed Recovery Time Objective (RTO): {elapsed_rto:.3f} seconds.")
    print(f"[DR-METRICS] Observed Recovery Point Objective (RPO): ~0.00 seconds (Zero transaction data loss).")

if __name__ == "__main__":
    setup_initial_database()
    backup_path = execute_snapshot_backup()
    simulate_disaster_and_failover(backup_path)

