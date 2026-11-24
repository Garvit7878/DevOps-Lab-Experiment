<div align="center">

# Lab 4: Advanced Deployment Strategies & Enterprise DevOps Toolkit

**Enterprise-Grade Infrastructure Automation | CI/CD | Zero-Downtime Deployments**

</div>

---

<table>
  <tr>
    <td><b>Name</b></td>
    <td>Garvit Sharma</td>
    <td><b>Roll Number</b></td>
    <td>2301730190</td>
  </tr>
  <tr>
    <td><b>Email</b></td>
    <td>garvitsharma8909@gmail.com</td>
    <td><b>GitHub</b></td>
    <td><a href="https://github.com/Garvit7878/DevOps-Lab-Experiment">Garvit7878/DevOps-Lab-Experiment</a></td>
  </tr>
</table>

---

## Architecture Overview

This lab implements a complete enterprise DevOps toolkit spanning seven interconnected pillars. The diagram below illustrates how each component fits into the overall delivery pipeline:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        ENTERPRISE DEVOPS ARCHITECTURE                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ┌──────────────┐    ┌──────────────┐    ┌──────────────────────────────┐  │
│   │   Developer   │───>│   Git Push   │───>│   CI/CD Pipeline (Task 2)   │  │
│   │   Commits     │    │   / PR       │    │   Lint → Test → Scan →      │  │
│   └──────────────┘    └──────────────┘    │   Coverage Gate (≥80%)       │  │
│                                            └──────────┬───────────────────┘  │
│                                                       │                     │
│                              ┌─────────────────────────┼──────────────┐      │
│                              │                         │              │      │
│                              ▼                         ▼              ▼      │
│                   ┌──────────────────┐   ┌─────────────────┐  ┌──────────┐  │
│                   │  Blue-Green      │   │  Canary Rollout  │  │  GitOps  │  │
│                   │  Deployment      │   │  10%→25%→50%→100%│  │  ArgoCD  │  │
│                   │  (Task 3)        │   │  (Task 7)        │  │ (Task 4) │  │
│                   └────────┬─────────┘   └────────┬────────┘  └────┬─────┘  │
│                            │                      │                │        │
│                            └──────────┬───────────┘                │        │
│                                       ▼                            │        │
│                            ┌──────────────────┐                    │        │
│                            │   PRODUCTION      │◄───────────────────┘        │
│                            │   ENVIRONMENT     │                            │
│                            └────────┬─────────┘                             │
│                                     │                                       │
│                    ┌────────────────┼────────────────┐                      │
│                    ▼                                 ▼                      │
│         ┌──────────────────┐              ┌──────────────────┐              │
│         │  Secret Manager  │              │ Disaster Recovery │              │
│         │  Vault (Task 6)  │              │ Snapshots (Task 1)│              │
│         │  AES-256 | RBAC  │              │ RTO<5m | RPO<30s  │              │
│         └──────────────────┘              └──────────────────┘              │
│                                                                             │
│         ┌───────────────────────────────────────────────────────┐           │
│         │        Comprehensive Strategy Report (Task 5)         │           │
│         │   Comparison Matrix | Risk Analysis | Governance      │           │
│         └───────────────────────────────────────────────────────┘           │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Deliverables

| # | Task | Marks | Submission ID | Deliverable |
|:-:|------|:-----:|:-------------:|:-----------:|
| 1 | Disaster Recovery & Failover Mechanism | 5 | `EUID-E699-8CBC-8D64` | [📄 PDF](deliverables/Task1_Disaster_Recovery_Mechanism.pdf) |
| 2 | Automated Testing in CI/CD Pipeline | 5 | `EUID-ADB2-3545-B594` | [📄 PDF](deliverables/Task2_Automated_Testing_CICD_Pipeline.pdf) |
| 3 | Blue-Green Deployment Strategy | 5 | `EUID-015C-0AE3-A56D` | [📄 PDF](deliverables/Task3_Blue_Green_Deployment_Strategy.pdf) |
| 4 | GitOps-Based Declarative Delivery | 5 | `EUID-0734-D532-2638` | [📄 PDF](deliverables/Task4_GitOps_Based_Delivery.pdf) |
| 5 | Advanced Deployment Strategies Report | 10 | `EUID-3DFC-3772-EBA8` | [📄 PDF](deliverables/Task5_Advanced_Deployment_Strategies_Report.pdf) |
| 6 | Enterprise Secret Management | 5 | `EUID-4895-1FBF-881A` | [📄 PDF](deliverables/Task6_Enterprise_Secret_Management.pdf) |
| 7 | Canary Deployment Strategy | 5 | `EUID-23A5-7036-B7E6` | [📄 PDF](deliverables/Task7_Canary_Deployment_Strategy.pdf) |

> **Total Marks: 40**

---

## Task Summaries

### Task 1 — Disaster Recovery & High-Availability Failover

Automated DR engine with continuous point-in-time snapshots, SHA-256 integrity seals, and standby promotion.

```
  Primary DB (Active R/W)
        │
        ├── Continuous Snapshots (every 60s)
        │       └── SHA-256 Sealed → dr_vault_backups/
        │
        ├── Health Probes ──── 3x Timeout? ──── ALERT
        │                                         │
        │                                         ▼
        │                              ┌─────────────────────┐
        │                              │  Failover Engine     │
        │                              │  1. Verify Snapshot  │
        │                              │  2. Promote Standby  │
        │                              │  3. Re-point DNS     │
        └── Standby Replica ◄──────────│  4. Audit Ledger     │
             (Warm)                    └─────────────────────┘
```

| Metric | SLA Target | Achieved | Status |
|--------|-----------|----------|:------:|
| Recovery Time (RTO) | ≤ 300s | 0.152s | ✅ |
| Recovery Point (RPO) | ≤ 30s | 0.000s | ✅ |
| Ledger Integrity | 100% Hash Match | SHA-256 Verified | ✅ |

---

### Task 2 — Automated Testing & CI/CD Quality Gates

Multi-stage pipeline with six sequential quality gates — zero-trust approach where any failure blocks deployment.

```
 Push / PR
    │
    ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  Gate 1       │───>│  Gate 2       │───>│  Gate 3       │
│  Flake8 Lint  │    │  Unit Tests   │    │  Integration  │
│  + Bandit     │    │  (PyTest)     │    │  Tests        │
└──────────────┘    └──────────────┘    └──────┬───────┘
                                               │
    ┌──────────────┐    ┌──────────────┐       │
    │  Gate 6       │◄───│  Gate 5       │◄──────┤
    │  Promotion    │    │  Trivy CVE    │    ┌──┴───────────┐
    │  to Staging   │    │  Scanner      │    │  Gate 4       │
    └──────────────┘    └──────────────┘    │  Coverage     │
                                            │  ≥ 80%        │
                                            └──────────────┘
```

**Results:** 4/4 tests passed | 94.44% coverage | All gates green

---

### Task 3 — Blue-Green Zero-Downtime Deployment

Dual-stack architecture with atomic traffic switching and instant rollback capability.

```
           ┌─────────────────────────────────────────┐
           │            Layer-7 Ingress Router        │
           └───────────────┬─────────────────────────┘
                           │
              ┌────────────┴────────────┐
              │                         │
    ┌─────────▼─────────┐    ┌─────────▼─────────┐
    │   BLUE STACK       │    │   GREEN STACK      │
    │   (v1.4.0)         │    │   (v1.5.0)         │
    │                    │    │                    │
    │   ● Current Live   │    │   ● New Release    │
    │   ● Warm Standby   │◄──│   ● Smoke Tested   │
    │     after cutover  │    │   ● Active after   │
    │                    │    │     cutover         │
    └────────────────────┘    └────────────────────┘

    Cutover:  BLUE ══════════════════> GREEN   (atomic, zero-downtime)
    Rollback: BLUE <══════════════════ GREEN   (sub-second revert)
```

---

### Task 4 — GitOps Declarative Delivery with ArgoCD

Git as the Single Source of Truth (SSOT) with automated drift detection and self-healing reconciliation.

```
    ┌──────────┐     PR Merge      ┌──────────────────┐
    │  GitHub   │─────────────────>│  ArgoCD Agent     │
    │  (SSOT)   │                   │  (In-Cluster)     │
    └──────────┘                   └────────┬─────────┘
         ▲                                  │
         │                        Compare & Reconcile
         │                                  │
         │                                  ▼
         │                         ┌──────────────────┐
         │   Manual kubectl edit   │  Kubernetes       │
         │   detected & reverted   │  Cluster (Live)   │
         └─────────────────────────│  State            │
                                   └──────────────────┘

    Drift Detected?
      YES → Overwrite live state with Git SSOT (self-heal)
      NO  → Synced ✅
```

---

### Task 5 — Advanced Deployment Strategies Report

Comprehensive comparison and risk analysis across all five deployment pillars.

| Strategy | Cost | Blast Radius | Rollback Speed | Best For |
|----------|:----:|:------------:|:--------------:|----------|
| Blue-Green | High (2x) | Cluster-wide | < 1 sec | Stateless APIs |
| Canary | Low (+10-25%) | Small subset | Automated | High-traffic services |
| GitOps | Minimal | PR-gated | Git revert | K8s multi-cloud |
| Vault Secrets | Low | Zero leaks | Instant revoke | Zero-trust credentials |
| Disaster Recovery | Moderate | Region-level | < 1 min | DB clusters & ledgers |

---

### Task 6 — Enterprise Secret Management (HashiCorp Vault)

Zero-trust credential lifecycle: encrypted storage, RBAC-authenticated access, in-memory injection, and automated rotation.

```
    ┌─────────────────┐          ┌─────────────────────┐
    │  CI/CD Runner    │──Auth──>│  HashiCorp Vault     │
    │                  │         │                      │
    │  Requests secret │         │  ┌────────────────┐  │
    │  via AppRole     │◄─Token──│  │ AES-256        │  │
    │                  │         │  │ Encrypted Store │  │
    └────────┬────────┘         │  └────────────────┘  │
             │                   │                      │
             ▼                   │  Audit Log ✓         │
    ┌─────────────────┐         │  RBAC Policies ✓     │
    │  In-Memory Only  │         │  Dynamic Rotation ✓  │
    │  Never on disk   │         └─────────────────────┘
    │  [MASKED] in logs│
    └─────────────────┘
```

---

### Task 7 — Canary Progressive Rollout

Phased traffic shifting with real-time telemetry gates — automatic rollback on SLA breach.

```
    100% ─────────────────────────────────────────── ●  Full Promotion
     90%                                            ╱
         ─── Baseline traffic decreases ──────────╱
     50% ─────────────────────────────── ●       ╱
                                        ╱       ╱
     25% ──────────────── ●            ╱       ╱
                         ╱            ╱       ╱
     10% ──── ●         ╱            ╱       ╱
             ╱         ╱            ╱       ╱
      0% ───┴─────────┴────────────┴───────┴──────── Timeline
           Phase 1    Phase 2     Phase 3   Phase 4
           (10min)    (15min)     (20min)   (Permanent)

    Gate at each phase: Error Rate ≤ 2.0% AND p99 Latency ≤ 120ms
    Breach → Instant rollback to 0% canary
```

---

## Project Structure

```
Lab4_Submission/
│
├── deliverables/                          # Generated PDF reports
│   ├── Task1_Disaster_Recovery_Mechanism.pdf
│   ├── Task2_Automated_Testing_CICD_Pipeline.pdf
│   ├── Task3_Blue_Green_Deployment_Strategy.pdf
│   ├── Task4_GitOps_Based_Delivery.pdf
│   ├── Task5_Advanced_Deployment_Strategies_Report.pdf
│   ├── Task6_Enterprise_Secret_Management.pdf
│   └── Task7_Canary_Deployment_Strategy.pdf
│
├── code/
│   ├── disaster_recovery/
│   │   └── dr_failover_engine.py          # Automated DR snapshot & failover
│   ├── ci_cd_pipeline/
│   │   ├── app.py                         # Payment Gateway microservice
│   │   ├── test_app.py                    # Unit & integration test suite
│   │   └── .github-workflows-ci-cd.yml    # GitHub Actions multi-gate workflow
│   ├── blue_green/
│   │   └── blue_green_orchestrator.py     # Zero-downtime routing engine
│   ├── gitops/
│   │   └── gitops_reconciler.py           # SSOT reconciliation & self-healing
│   ├── secret_management/
│   │   └── vault_manager.py               # Vault RBAC & dynamic rotation
│   └── canary/
│       └── canary_controller.py           # Weighted rollout & metric analysis
│
└── generate_all_reports.py                # PDF report compiler
```

---

## How to Regenerate PDFs

```bash
pip install reportlab
cd Lab4_Submission
python generate_all_reports.py
```

All 7 PDF deliverables will be generated in the `deliverables/` directory.

---

<div align="center">
<i>Garvit Sharma — 2301730190 — Enterprise DevOps Lab 4</i>
</div>
