# PRD — Computer Networks Lab Project (BCSE308P)

**Status:** Committed direction (Option A)
**Date:** 2026-09-16
**Team:** 2 members (roles TBD)
**Course:** BCSE308P Computer Networks Lab, SCOPE, VIT Vellore

---

## 1. Project Summary

A **system and method for cost-constrained containment of self-propagating banking malware**
(embodiment: **Emotet-class modular banking worm**) in a computer network. The project models how
the worm propagates node-to-node across a bank's branch/ATM topology, computes a per-node
propagation-risk score, and iteratively selects the highest-risk node/segment for
micro-segmentation or quarantine **under a limited action budget**, to minimize the total number of
infected nodes.

The deliverable is framed as a **patentable invention** (system + method), not "a simulation app."

---

## 2. Course & Evaluation Context

- **Component:** Course Project / Product Component — 30 of 100 total marks.
- **Evaluation window:** last two weeks of lab hours.
- **Grading rubric (30 marks):**

| Criterion | Marks |
|---|---|
| Problem identification & CO relevance | 2 |
| Design & architecture | 5 |
| Implementation & working demonstration | 10 |
| Innovation & application of concepts | 10 |
| Documentation, viva & teamwork | 3 |

- **Course outcomes (CO1–CO5)** must be explicitly mapped and justified in the report.

### Review timeline

| Review | Content | Due |
|---|---|---|
| Review 1 | Problem identification & proposal | 2026-08-24 (passed) |
| Review 2 | Design, development & progress | 2026-09-14 (passed) |
| Review 3 | Final prototype, report & viva | 2026-10-09 |

- **Immediate deadline (advisor):** present strong, focused input to the advisor by **Monday 2026-09-21**.
- Lab assessment also scheduled Monday.

---

## 3. Stakeholders

- **Advisor / faculty:** drives scope, patentability, SIH anchoring, and the Monday checkpoint.
- **Team:** 2 students — each must be able to explain the whole project in viva (individual marks, not split equally).
- **Evaluators:** grade the demo, report, patent spec, and viva against the 30-mark rubric.

---

## 4. Problem Statement

**Original (rejected):** generic malware — "model how malware spreads through a network."

**Advisor's objection:** malware is too vast a domain; a generic solution covering all malware types is
not acceptable. Must narrow to **one specific malware type** that genuinely needs an optimal solution.

**Reframed (current):**

> Self-propagating banking malware (Emotet-class worm) moves laterally across a bank's network
> faster than a manual security team can respond. Existing epidemic/SIR containment models optimize
> globally (reduce R₀) but do **not** answer the operator's real question: *"Given I can only
> quarantine/segment a limited number of nodes right now, which ones do I act on to minimize total
> infection?"*

**Gap this project fills:** a node-level, budget-constrained, action-aware containment method.

---

## 5. Constraints (hard requirements)

1. **Narrow to ONE specific malware type** (advisor's core requirement). → *Emotet-class worm.*
2. **Real Indian case studies, last 5 years, especially banking sector.**
3. **Anchor to an SIH 2026 problem statement** (theme: "Blockchain & Cybersecurity").
4. **Patentable** — write up as a Complete Specification (Form-2 style, 15–20 pages).
   - India Patents Act **§3(k)** excludes software *per se* → must be framed as a
     **"system and method" producing a technical effect** (improved network security / faster
     containment), not "an app/simulation."
5. **CO mapping** to BCSE308P CO1–CO5 must be explicit and defensible.
6. **No AI tools in the final report** + **plagiarism similarity < 10%** (VTOP submission).
7. **Working, demonstrable prototype** by Review 3 (not slides-only).
8. **Security/ethical:** any scanning/sniffing confined to simulation — never production/external networks.

---

## 6. Proposed Solution (the invention)

**Working title:** *"A system and method for cost-constrained containment of self-propagating
banking malware in a network."*

### Core mechanism

1. Model the bank network as a **graph** (nodes = hosts/ATMs/servers/branches; edges = reachable
   lateral-movement paths).
2. Simulate **Emotet-class worm propagation** and record **infection arrival time** per node.
3. Compute a **composite propagation-risk score** per node combining:
   - infection arrival time (earlier = more urgent),
   - node centrality / connectivity (how many others it can reach),
   - reachable lateral-movement path density.
4. **Iteratively select** the highest-risk node/segment for micro-segmentation or quarantine,
   **subject to a limited action budget K** (you can only act on a few nodes).
5. Stop when a **containment threshold** is met (e.g., infection growth < ε, or all budget spent).
6. Output: the **ordered containment plan** (which nodes, in which order) + measured reduction in
   total infected nodes vs. baseline.

### The inventive step (what is novel)

Classical SIR/epidemic models optimize **globally** for R₀ reduction (top-down, aggregate). This
method is **node-level, budget-constrained, and action-aware** — it solves *"which K nodes do I
quarantine, given a fixed action budget, to minimize total infection?"* using a composite
timing–centrality metric that prior approaches do not combine for worm containment.

### Specific malware type (embodiment)

**Emotet-class modular banking worm** — self-propagating (lateral movement) *and* financially
motivated (credential theft). Satisfies both "one specific type" and "banking" constraints.

---

## 7. Course Outcome (CO) Mapping

| CO | Outcome | How the project demonstrates it |
|---|---|---|
| CO1 | Interpret building blocks & architecture of a network | Modeling the bank network as a topology (nodes, links, branches) and analyzing how a threat propagates across it |
| CO5 | Select transport protocols with **security** for real-time applications | The containment method is a security control; ties network-layer segmentation/quarantine to reduced lateral movement |

*(Primary claim: CO1 + CO5. Confirm with advisor whether a third CO should be claimed.)*

---

## 8. Case Studies / Evidence (to cite in report)

Recent Indian banking / financial malware (last 5 years — verify each with a citable source):

| Malware | Year | Type | India relevance |
|---|---|---|---|
| Drinik | 2021 | Android banking trojan | Targeted 27+ Indian banks |
| SOVA | 2022 | Android banking trojan | Targeted Indian banks + UPI apps |
| Anatsa / TeaBot | 2021–2023 | Android banking trojan | 400+ banks globally incl. India |
| Emotet | ongoing | Modular banking trojan / worm | CERT-In advisories; worm-like lateral spread |
| AIIMS ransomware | 2022 | Ransomware (healthcare) | Major Indian cyber incident (secondary, non-banking) |

*(Older classics — Cosmos Bank 2018, Union Bank of India 2016 — outside the 5-year window but may be
referenced as background.)*

---

## 9. Technical Approach (simulation stack — to confirm with faculty)

- **Language:** Python 3.
- **Graph/topology:** `networkx` (nodes, edges, centrality metrics).
- **Propagation model:** custom discrete-time SIR-style spread with Emotet-like lateral-movement rules.
- **Optimization:** greedy iterative selection by composite risk score (budget K).
- **Visualization:** `matplotlib` (infection curve, topology heat-map, containment plan).
- **Deliverable artifacts:** simulation code, results/screenshots, report, patent spec (Form-2).

*(Alternatives if faculty requires: Packet Tracer/GNS3 for topology, NS3 for propagation. Python is the
pragmatic default for a demonstrable prototype in ~3 weeks.)*

---

## 10. Deliverables Checklist

- [ ] One-page proposal (topic, CO mapping, team roles, tools)
- [ ] Working propagation + containment simulation (demo at Review 3)
- [ ] Final report (8–10 pages): problem statement, design diagrams, implementation, results, CO mapping, contribution table
- [ ] **Patent Complete Specification (Form-2, 15–20 pages)** — the "full marks" artifact
- [ ] Source code + config files (submitted for plagiarism check)
- [ ] Malware-type → propagation-time breakdown table (advisor's explicit request)

---

## 11. Team Roles

Each member must be able to explain the whole project. Full split in [TEAM_SPLIT.md](./TEAM_SPLIT.md).

| Member | Role |
|---|---|
| Member 1 (you) | Core algorithm & containment engine — `propagation.py`, `risk_score.py`, `containment.py`; patent sections 5–7, 12–13, 18–19 |
| Member 2 | Topology, baselines & evaluation — `topology.py`, `simulate.py`, `visualize.py`, `data/`; case-study research; patent sections 2–4, 8–11, 14–17, 20 |

---

## 12. Risks & Open Questions

| # | Item | Status |
|---|---|---|
| 1 | Exact SIH 2026 problem statement / PS number to anchor to | Need to confirm on sih.gov.in portal (login) or Kaggle dataset |
| 2 | Which COs to officially claim (CO1+CO5, or add a third) | Confirm with advisor |
| 3 | Approved tools (Python sim vs Packet Tracer/GNS3/NS3) | Confirm with advisor |
| 4 | Novelty risk: is the composite risk-score method sufficiently non-obvious for §3(k) CRI? | Mitigate by framing as "system + method with technical effect" |
| 5 | Banking-vs-worm tension (India banking malware are mostly trojans, not worms) | Resolved via Emotet (both) |
| 6 | Plagiarism <10% and "no AI tools" rule for final report | Write report in own words; cite all sources |

---

## 13. Next Steps

1. Confirm exact SIH PS anchor + approved tools + CO claim with advisor (Monday).
2. Draft reframed problem statement + malware-type breakdown table + patent claims (next).
3. Build the simulation skeleton (topology → propagation → risk score → greedy containment).
4. Write the Form-2 patent spec + final report against the rubric.
