"""
Enterprise GitOps Declarative Controller & Reconciliation Engine
Demonstrates Git repository as Single Source of Truth (SSOT),
continuous drift detection, declarative manifest reconciliation,
and automated self-healing against unauthorized out-of-band mutations.
"""
import json
import time

class GitOpsReconciliationController:
    def __init__(self):
        # Desired State stored declaratively in Git
        self.git_desired_state = {
            "metadata": {"app": "enterprise-settlement-service", "namespace": "prod-financial"},
            "spec": {
                "replicas": 5,
                "image": "docker.enterprise.internal/fin/settlement:v3.2.1",
                "resources": {"cpu": "2000m", "memory": "4Gi"},
                "env": {"ENCRYPTION_MODE": "STRICT_FIPS_140_2"}
            }
        }
        # Live State in Kubernetes / Cloud cluster
        self.live_cluster_state = json.loads(json.dumps(self.git_desired_state))

    def detect_drift(self):
        diffs = []
        for key in ["replicas", "image", "resources", "env"]:
            desired_val = self.git_desired_state["spec"].get(key)
            live_val = self.live_cluster_state["spec"].get(key)
            if desired_val != live_val:
                diffs.append({
                    "property": key,
                    "desired (Git)": desired_val,
                    "actual (Cluster)": live_val
                })
        return diffs

    def simulate_manual_cluster_tampering(self):
        print("\n[MUTATION EVENT] Engineer runs manual 'kubectl edit' or changes replicas out-of-band:")
        self.live_cluster_state["spec"]["replicas"] = 1  # Dangerously lowered!
        self.live_cluster_state["spec"]["image"] = "docker.enterprise.internal/fin/settlement:debug-untested"
        print("  -> Live Cluster modified manually: replicas=1, image=debug-untested")

    def git_commit_new_desired_state(self, new_image, new_replicas):
        print(f"\n[GIT COMMIT] Pull Request merged into Git repo: Updating spec to {new_image}, replicas={new_replicas}")
        self.git_desired_state["spec"]["image"] = new_image
        self.git_desired_state["spec"]["replicas"] = new_replicas

    def reconcile_loop(self):
        print("\n[GITOPS RECONCILIATION LOOP TRIGGERED]")
        diffs = self.detect_drift()
        if not diffs:
            print("  [SYNC STATUS: Synced] Live state matches Git SSOT. Zero drift detected.")
            return
        
        print("  [SYNC STATUS: OutOfSync] Infrastructure drift identified!")
        for diff in diffs:
            print(f"    - Field '{diff['property']}': Cluster has '{diff['actual (Cluster)']}' vs Git SSOT '{diff['desired (Git)']}'")
        
        print("  [ACTION] Applying Declarative Reconciliation: Overwriting Live State with Git SSOT...")
        self.live_cluster_state = json.loads(json.dumps(self.git_desired_state))
        print("  [HEALED] Cluster reconciled successfully. Live State is now identical to Git repository.")

if __name__ == "__main__":
    controller = GitOpsReconciliationController()
    
    # 1. Normal sync state
    controller.reconcile_loop()
    
    # 2. Tampering & Self-Healing
    controller.simulate_manual_cluster_tampering()
    controller.reconcile_loop()
    
    # 3. Declarative Git rollout
    controller.git_commit_new_desired_state("docker.enterprise.internal/fin/settlement:v3.3.0", 8)
    controller.reconcile_loop()

