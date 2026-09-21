# Team Split — 2 Members

**Rule from the brief:** each member must be able to explain the *whole* project in viva, not just
their part. This split gives each member both substantive coding and documentation so both can be
tested on any section.

---

## Member 1 — Core Algorithm & Containment Engine (the inventive step)

**Coding (owns the core of the invention):**
| File | Responsibility |
|---|---|
| `src/propagation.py` | Discrete-time worm propagation; records per-node infection arrival time `t(v)` |
| `src/risk_score.py` | Composite score `α·urgency + β·centrality + γ·reach` |
| `src/containment.py` | Greedy budget-constrained quarantine/segmentation optimizer |

**Patent spec sections (owns the "invention" writing):**
- 5. Problem Statement
- 6. Objectives
- 7. Summary of Invention
- 12. Algorithm / Method
- 13. Mathematical / Technical Model
- 18. Claims
- 19. Abstract

**Testing:** unit tests for propagation timing, risk-score normalization, and greedy selection.

---

## Member 2 — Topology, Baselines & Evaluation (the surrounding system)

**Coding:**
| File | Responsibility |
|---|---|
| `src/topology.py` | Builds the bank network graph (nodes, edges, asset types) |
| `src/simulate.py` | CLI runner + the 4 baselines (no-action, random, degree-only, earliest-first) |
| `src/visualize.py` | Infection curves, topology heat-map, containment-plan table |
| `data/bank_topology.json` | Sample branch/ATM topology |

**Patent spec sections (owns the "context" writing):**
- 2. Field of Invention
- 3. Background
- 4. Prior Art / Existing Technologies
- 8. Brief Description of Drawings
- 9. Detailed Description
- 10. System Architecture
- 11. Working of the Invention
- 14. Example / Working Embodiment
- 15. Alternative Embodiments
- 16. Technical Advantages
- 17. Industrial Applicability
- 20. Figure List

**Research:** Indian banking malware case studies (Drinik 2021, SOVA 2022, Anatsa/TeaBot, Emotet /
CERT-In, AIIMS 2022) with citations — feeds section 3 and the final report.

---

## Shared (both)

- Final integration of both code halves (one runnable simulation).
- The 8–10 page CN Lab report (CO mapping, contribution table, results screenshots).
- The novelty/prior-art matrix (section B).
- Viva preparation — both must explain the full pipeline end-to-end.

---

## Contribution table (for the report)

| Member | Design | Coding | Testing | Documentation |
|---|---|---|---|---|
| Member 1 | risk-score model, containment algorithm | propagation, risk_score, containment | unit tests (timing, score, greedy) | Problem, Objectives, Summary, Algorithm, Math Model, Claims, Abstract |
| Member 2 | topology model, evaluation harness | topology, simulate (baselines), visualize | baseline comparison runs | Field, Background, Prior Art, Drawings, Detailed Description, Architecture, Working, Example, Alternatives, Advantages, Applicability, Figures |
