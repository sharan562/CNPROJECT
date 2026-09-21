# Design Document — Cost-Constrained Containment of Emotet-Class Banking Worm

**Project:** BCSE308P Computer Networks Lab (30 marks)
**Status:** Draft v1 (for advisor review, Monday 2026-09-21)
**Companion:** [PRD.md](./PRD.md)

---

## 1. Reframed Problem Statement

Self-propagating banking malware — embodied by an **Emotet-class modular banking worm** — moves
laterally across a bank's branch/ATM network faster than a manual security team can respond.
Classical epidemic (SIR) containment models optimize **globally** (reduce the reproduction number R₀),
but they do not answer the operator's actual decision problem:

> *"Given I can quarantine or segment only a limited number of nodes right now, which nodes do I act
> on, and in what order, to minimize the total number of infected nodes?"*

This project designs and simulates a **node-level, budget-constrained, action-aware containment
method**, and validates that it outperforms baseline strategies on realistic bank-network topologies.

---

## 2. Malware-Type Breakdown (advisor-requested section)

The advisor required the generic "malware" framing be narrowed to **one specific type**. The table
below maps common malware classes to their propagation mechanism and characteristic propagation time,
and justifies why **Emotet-class worm** is the correct embodiment for a propagation simulation.

| Malware class | Propagation mechanism | Self-propagating? | Characteristic spread time* | Fits a propagation sim? |
|---|---|---|---|---|
| **Trojan** | User action (phishing, malicious app install) | No | hours–days | Weak — spread is social, not network-topological |
| **Virus** | File infection, user copies files | Partial | minutes–hours | Moderate |
| **Worm** | Self-replicating over network (SMB, RDP, malspam) | **Yes** | **seconds–minutes** | **Strong — lateral, node-to-node** |
| **Ransomware (worm-like)** | Exploit + lateral movement + encryption | Sometimes | minutes | Strong (WannaCry/NotPetya family) |
| **Rootkit** | Stealth persistence in OS kernel | No | n/a (manual deploy) | Weak |
| **Emotet (modular trojan/worm)** | Malspam entry + lateral movement + credential theft | **Yes** | minutes | **Strong — also banking-motivated** |

**Conclusion:** a *worm* is the only class whose spread is naturally modeled as node-to-node
propagation across a network graph. Among worms, **Emotet** is the ideal embodiment because it is
simultaneously self-propagating **and** financially motivated (credential/banking theft), satisfying
both the "one specific type" and "banking sector" constraints.

> \* Characteristic times are illustrative order-of-magnitude values. The final report must replace
> these with cited figures from CERT-In advisories / security-vendor telemetry (e.g., Emotet lateral
> spread timing, Drinik/SOVA delivery metrics).

---

## 3. System Architecture

The system is a pipeline of five modules. Each has one responsibility and a well-defined interface.

```
+----------------+     +----------------+     +----------------+     +----------------+     +----------------+
| 1. Topology    | --> | 2. Propagation | --> | 3. Risk Scorer | --> | 4. Containment | --> | 5. Reporting   |
|    Builder     |     |    Simulator   |     |                |     |   Optimizer    |     | / Visualizer   |
+----------------+     +----------------+     +----------------+     +----------------+     +----------------+
  bank network graph    SIR-style spread       composite score       greedy quarantine      infection curves,
  (nodes, edges,         records infection      per node (time +      under action budget   containment plan,
  asset types)           arrival time t_i       centrality + reach)   + threshold            metrics vs baselines
```

### 3.1 Topology Builder (`topology.py`)
- Models the bank network as an undirected graph `G = (V, E)`.
- **Node types:** core-banking server, branch server, ATM, employee workstation, admin host.
- **Edges:** reachable lateral-movement paths (SMB/admin shares, RDP, shared credentials).
- **Outputs:** adjacency structure + per-node `type`, `security_tier`, and centrality precomputations.
- Config loaded from `data/bank_topology.json` so topologies are swappable (single branch → full campus).

### 3.2 Propagation Simulator (`propagation.py`)
- Discrete-time SI/SIR model parameterized for worm lateral movement.
- States: `Susceptible → Infected → (Quarantined)`.
- At each timestep, an infected node attempts to infect each susceptible neighbor with probability
  `β` (transmission rate). Optional recovery/quarantine at rate `γ`.
- **Records infection arrival time `t_i` per node** — the key signal consumed downstream.
- Returns: infection timeline, per-node `t_i`, final infection set.

### 3.3 Risk Scorer (`risk_score.py`)
Computes a composite score per susceptible node:

```
score(v) = α · urgency(v) + β · centrality(v) + γ · reach(v),   α + β + γ = 1
```

- `urgency(v)` = exp(−t_v / τ) — earlier-infected nodes are more urgent (normalized). For a
  not-yet-infected node `t_v = ∞`, so `urgency = 0`; the term is non-zero only for infected nodes.
- `centrality(v)` = normalized degree or betweenness — how many nodes `v` can reach.
- `reach(v)` = normalized count of **susceptible** nodes within 2 hops of `v`.
- Weights `(α, β, γ)` are tunable; a default (e.g., 0.4 / 0.35 / 0.25) is used and sensitivity is
  reported in results.

### 3.4 Containment Optimizer (`containment.py`)
Greedy, budget-constrained selection:

```
function contain(G, seeds, β, K, ε):
    infected = seeds; plan = []; t = 0
    while True:
        newly = simulate_step(G, infected)       # one spread step; update t_i
        if not newly: break                       # outbreak ended
        t += 1; infected |= newly
        if len(plan) < K and len(newly) > ε:      # act while budget remains and
            scores = { risk_score(v) for v in susceptible(G) }  # growth is above ε
            v* = argmax(scores)
            quarantine(G, v*)                     # remove v* + its edges
            plan.append((v*, scores[v*], t))
    return plan, len(infected)
```

- **Budget `K`:** max nodes/segments the operator can quarantine (cost constraint).
- **Threshold `ε`:** stop spending quarantine budget once per-step growth (`len(newly)`) drops to `ε`;
  the outbreak still simulates to completion so the final infected count stays comparable to baseline.
- **Output:** an *ordered containment plan* (which nodes, in what order) + measured infected-count
  reduction vs. baseline.

### 3.5 Reporting / Visualizer (`visualize.py`, `report.py`)
- Infection curve (infected vs. time) for each strategy.
- Topology heat-map (node color = infection time / risk score).
- Containment-plan table and cost (number of quarantines used).
- Exports figures/tables for the report and patent spec.

---

## 4. Data Flow

1. Load/seed topology → `G`.
2. Inject 1–3 infected seed nodes (e.g., a compromised ATM or branch server).
3. Simulate propagation; record `t_i` per node.
4. Score susceptible nodes; select and quarantine the top node; decrement budget.
5. Repeat until budget `K` exhausted or growth ≤ `ε`.
6. Emit final metrics + visualizations + the ordered containment plan.

---

## 5. Evaluation Metrics

| Metric | Definition | Purpose |
|---|---|---|
| Total infected | nodes infected at end of run | primary outcome — minimize |
| Peak infection rate | max new infections per step | severity of the outbreak |
| Time-to-peak | steps to peak infection | how fast the outbreak grows |
| Containment cost | number of quarantines used (≤ K) | cost of the response |

**Baselines for comparison (must beat these):**
1. No containment (control).
2. Random quarantine (K random nodes).
3. Degree-only quarantine (top-K by connectivity).
4. Earliest-infection-first quarantine (top-K by smallest `t_i`).

The composite score is expected to outperform all four because it jointly considers timing,
connectivity, and reachable susceptible nodes.

---

## 6. Algorithm Pseudocode

```
# Risk score
def risk_score(v, t, G):
    urgency    = normalize(exp(-t[v] / tau))
    centrality = normalize(degree_centrality(G, v))      # or betweenness
    reach      = normalize(count_susceptible_within(G, v, hops=2))
    return alpha*urgency + beta*centrality + gamma*reach

# Containment
def contain(G, seeds, beta, K, eps, alpha, beta_w, gamma):
    infected = set(seeds); plan = []; t = {s: 0 for s in seeds}
    while True:
        newly = simulate_step(G, infected)                # one spread step
        if not newly: break                               # outbreak ended
        t.update(newly)                                   # record arrival times
        if len(plan) < K and len(newly) > eps:            # act while budget & growth
            v = argmax(risk_score(x, t, G) for x in susceptible(G))
            quarantine(G, v)
            plan.append(v)
    return plan, len(infected)
```

---

## 7. Course Outcome (CO) Mapping

| CO | Outcome | Demonstration |
|---|---|---|
| CO1 | Interpret building blocks & architecture of a network | The bank network is modeled as a graph (nodes, links, topology); propagation is analyzed over that architecture |
| CO5 | Select transport protocols with **security** | The containment method is a security control that reduces lateral movement via segmentation/quarantine |

*(Confirm with advisor whether to also claim CO2 — switching/segmentation — since micro-segmentation
is a network-segmentation concept.)*

---

## 8. Patent Framing (India Patents Act §3(k) aware)

- Software *per se* is excluded; the invention must be a **system + method producing a technical
  effect** (measurably reduced lateral-movement infection).
- Frame every artifact as a method/system, never "an app/simulation."

### First-cut claims (to be refined into Form-2 language)

1. **A method for containing self-propagating malware in a computer network, comprising:**
   modeling the network as a graph of nodes and lateral-movement edges; simulating propagation of the
   malware from at least one infected node to record, for each node, an infection arrival time;
   computing, for each susceptible node, a composite risk score from said infection arrival time, a
   centrality measure, and a count of reachable susceptible nodes; iteratively selecting a highest-risk
   node and applying a quarantine or micro-segmentation action thereto under a predefined action
   budget; and terminating when a containment threshold is satisfied.
2. The method of claim 1, wherein the malware is an **Emotet-class modular banking worm**.
3. The method of claim 1, wherein the composite risk score is a weighted sum of the infection-arrival
   urgency, the centrality, and the reachable-susceptible count, the weights being tunable from
   observed propagation data.
4. **A system** comprising a processor and a memory configured to perform the method of claim 1.

---

## 9. Testing & Validation Plan

- **Unit tests:** topology build, single-step propagation (correct `t_i`), risk-score normalization,
  greedy selection (picks highest score, respects budget).
- **Correctness checks:** with `β` low → no spread; with full mesh + `β=1` → all infected; quarantine
  of a cut-vertex stops spread.
- **Reproducibility:** fixed random seed; run N=30 trials per strategy; report mean ± 95% CI.
- **Sensitivity:** vary `(α, β, γ)` weights and `K`; show the composite score is robust (not tuned to
  one topology).

---

## 10. Project File Structure

```
cn-project/
  PRD.md
  DESIGN.md
  src/
    topology.py          # build bank network graph from JSON
    propagation.py       # SI/SIR worm spread, records t_i
    risk_score.py        # composite score
    containment.py       # greedy budget-constrained optimizer
    simulate.py          # CLI entry: run strategy vs baselines
    visualize.py         # plots + heat-map
  data/
    bank_topology.json   # sample branch/ATM topology
  results/               # generated metrics + figures
  report/                # 8–10 page final report
  patent/                # Form-2 complete specification
```

---

## 11. Open Items (carry over from PRD)

1. Confirm exact SIH 2026 PS number + theme ("Blockchain & Cybersecurity").
2. Confirm approved tools (Python sim vs Packet Tracer/GNS3/NS3).
3. Confirm CO claim (CO1+CO5, or add CO2).
4. Replace illustrative propagation times with cited sources.
