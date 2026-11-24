"""
Enterprise Canary Rollout & Metric Analysis Engine
Simulates phased weighted traffic split (10% -> 25% -> 50% -> 100%),
monitors Prometheus-style metrics (error rate, latency p99),
and automatically triggers rollback when error budget is exceeded.
"""
import random
import time

class CanaryRolloutController:
    def __init__(self, baseline_version="v2.1.0", canary_version="v2.2.0"):
        self.baseline_version = baseline_version
        self.canary_version = canary_version
        self.rollout_steps = [10, 25, 50, 100]
        self.max_allowed_error_rate = 2.0  # Percentage (%)
        self.max_allowed_p99_latency_ms = 120.0

    def evaluate_telemetry(self, canary_weight, inject_fault=False):
        print(f"\n[PHASE: CANARY WEIGHT = {canary_weight}%]")
        total_requests = 100
        canary_requests = int(total_requests * (canary_weight / 100.0))
        baseline_requests = total_requests - canary_requests
        
        # Synthetic Telemetry: only inject errors if inject_fault is True
        if inject_fault:
            canary_errors = random.randint(3, 5)
            canary_latency = random.uniform(220.0, 310.0)
        else:
            canary_errors = 0
            canary_latency = random.uniform(45.0, 85.0)
        
        error_rate = (canary_errors / canary_requests) * 100 if canary_requests > 0 else 0
        
        print(f"  Routing Profile: Baseline({self.baseline_version}): {baseline_requests} reqs | Canary({self.canary_version}): {canary_requests} reqs")
        print(f"  Canary Telemetry -> Error Rate: {error_rate:.2f}% (Threshold: {self.max_allowed_error_rate}%) | p99 Latency: {canary_latency:.1f}ms (Threshold: {self.max_allowed_p99_latency_ms}ms)")
        
        # Guardrail check
        if error_rate > self.max_allowed_error_rate or canary_latency > self.max_allowed_p99_latency_ms:
            print(f"  [ALARM TRIGGERED] Canary breached SLA! Initiating immediate traffic rollback to 0%.")
            return False
        
        print(f"  [GATE APPROVED] Telemetry within healthy parameters. Advancing to next phase...")
        return True

    def execute_progressive_rollout(self, fail_at_step=None):
        print(f"Starting Canary Deployment Workflow: {self.baseline_version} -> {self.canary_version}")
        for step in self.rollout_steps:
            inject = (step == fail_at_step)
            healthy = self.evaluate_telemetry(step, inject_fault=inject)
            if not healthy:
                print(f"[STATUS] Rollout Aborted at {step}% weight. Cluster restored to Baseline {self.baseline_version} 100%.")
                return False
            time.sleep(0.05)
        print(f"\n[SUCCESS] Canary {self.canary_version} promoted to 100% Production Baseline!")
        return True

if __name__ == "__main__":
    controller = CanaryRolloutController()
    print("--- SCENARIO 1: Canary Breaches Error Threshold at 25% ---")
    controller.execute_progressive_rollout(fail_at_step=25)
    
    print("\n--- SCENARIO 2: Successful Phased Promotion ---")
    controller.execute_progressive_rollout(fail_at_step=None)
