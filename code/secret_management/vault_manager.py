"""
Enterprise Secret Management Simulation
Demonstrates HashiCorp Vault / External Secrets Operator paradigm:
- Encrypted credential storage at rest & in transit
- RBAC Token Authentication and dynamic secret generation
- In-memory injection without plaintext disk exposure
- Dynamic automated secret rotation without application downtime
"""
import base64
import hashlib
import hmac
import json
import time

class EnterpriseVaultServer:
    def __init__(self, master_key="Enterprise-Vault-Master-Salt-2026"):
        self.master_key = master_key
        self.secret_store = {}
        self.token_acl = {"ci-runner-token-xyz": ["read:payment-db", "read:stripe-api"]}

    def _encrypt(self, secret_text):
        # Simulated AES/HMAC encryption envelope
        signature = hmac.new(self.master_key.encode(), secret_text.encode(), hashlib.sha256).hexdigest()
        b64 = base64.b64encode(secret_text.encode()).decode()
        return f"enc:v1:{b64}:{signature[:16]}"

    def _decrypt(self, cipher_envelope):
        parts = cipher_envelope.split(":")
        b64_val = parts[2]
        return base64.b64decode(b64_val).decode()

    def store_secret(self, path, key_value_dict):
        encrypted_dict = {k: self._encrypt(v) for k, v in key_value_dict.items()}
        self.secret_store[path] = encrypted_dict
        print(f"[VAULT] Path '{path}' stored securely. Encrypted ciphertext sealed.")

    def fetch_secret(self, client_token, path):
        if client_token not in self.token_acl:
            raise PermissionError("[VAULT 403] Invalid or revoked client token.")
        if f"read:{path.split('/')[-1]}" not in self.token_acl[client_token]:
            raise PermissionError(f"[VAULT 403] Token lacks policy authorization for path '{path}'.")
        
        raw_encrypted = self.secret_store.get(path, {})
        decrypted = {k: self._decrypt(v) for k, v in raw_encrypted.items()}
        print(f"[VAULT AUDIT] Path '{path}' accessed by token '{client_token[:12]}...'. Audit logged.")
        return decrypted

    def rotate_secret(self, path, new_key_value_dict):
        print(f"\n[VAULT ROTATION] Initiating automated credential rotation for '{path}'...")
        self.store_secret(path, new_key_value_dict)
        print(f"[VAULT ROTATION] New credentials written with updated generation tag.")

class SecurePipelineRunner:
    def __init__(self, vault_server, token):
        self.vault = vault_server
        self.token = token
        self.runtime_env = {}

    def inject_secrets_into_runtime(self, path):
        print(f"\n[CI/CD RUNNER] Fetching secrets dynamically for job execution...")
        secrets = self.vault.fetch_secret(self.token, path)
        # Injected strictly in-memory into isolated runtime dictionary
        self.runtime_env.update(secrets)
        print(f"[CI/CD RUNNER] Injected {len(secrets)} secrets into memory.")
        # Verify secrets are masked
        for k in secrets.keys():
            print(f"  -> ENV['{k}'] = [MASKED / SENSITIVE]")

    def execute_secure_db_query(self):
        user = self.runtime_env.get("DB_USER")
        pwd = self.runtime_env.get("DB_PASSWORD")
        print(f"[DB-CLIENT] Connecting with active memory credentials (User: {user}). Connection Established.")

if __name__ == "__main__":
    vault = EnterpriseVaultServer()
    
    # 1. Admin provisions secret in Vault
    vault.store_secret("secret/data/payment-db", {
        "DB_USER": "fin_app_usr",
        "DB_PASSWORD": "super-secure-token-9988#kL",
        "DB_HOST": "prod-aurora-cluster.internal:5432"
    })
    
    # 2. Pipeline worker fetches credential using least-privilege token
    pipeline = SecurePipelineRunner(vault, token="ci-runner-token-xyz")
    pipeline.inject_secrets_into_runtime("secret/data/payment-db")
    pipeline.execute_secure_db_query()
    
    # 3. Dynamic Rotation
    vault.rotate_secret("secret/data/payment-db", {
        "DB_USER": "fin_app_usr_v2",
        "DB_PASSWORD": "rotated-crypto-key-1122#zX",
        "DB_HOST": "prod-aurora-cluster.internal:5432"
    })
    pipeline.inject_secrets_into_runtime("secret/data/payment-db")
    pipeline.execute_secure_db_query()

