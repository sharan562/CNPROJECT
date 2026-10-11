# Cost-Constrained Containment of Emotet-Class Banking Malware

This Computer Networks Lab prototype models lateral worm propagation through a bank-network topology and produces a budget-constrained quarantine plan. It compares the proposed composite-risk method against no containment, random quarantine, degree-based quarantine, and earliest-observed-infection quarantine.

## Requirements

- Python 3.10 or newer
- `networkx` for topology modelling
- `matplotlib` for figures

## Setup (Windows PowerShell)

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

If PowerShell prevents environment activation, run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Then repeat the activation command.

## Run the prototype

From the project root:

```powershell
python -m src.comparison
```

The defaults are defined in `config/default.json` and can be overridden at runtime.

```powershell
python -m src.comparison --config config/default.json --seed-node WS_2 --beta 0.3 --budget 3 --trials 20 --random-seed 99
```

A second preset for the multi-branch topology is also available. Each preset writes to its own
subdirectory under `results/`, so running one experiment does not overwrite the other:

```powershell
python -m src.comparison --config config/multibranch.json
```

You can also use the convenience launcher script:

```powershell
./run_experiment.ps1
./run_experiment.ps1 -Config config/multibranch.json
./run_experiment.ps1 -Config config/default.json -SeedNode WS_2 -Beta 0.3 -Budget 3 -Trials 20 -RandomSeed 99
```

The default experiment uses:

- seed node: `WS_1`
- transmission probability: `0.25`
- quarantine budget: `2` nodes
- random seed: `42` for reproducible results

## Outputs

The command prints final infection counts and ordered quarantine plans, and updates `results/` with:

- `strategy_comparison.png` — final infection count by strategy
- `infection_curves.png` — no-containment versus proposed cumulative infection curve
- `network_topology.png` — baseline infected nodes and proposed quarantines
- `comparison_summary.json` — configuration, counts, plans, and infection histories

## Run the multi-branch scenario

```powershell
python -m src.comparison --topology data/bank_topology_multibranch.json --seed-node WS_N1 --beta 0.4 --budget 2 --trials 30
```

This 19-node topology represents three branches, six ATMs, six workstations, an admin host, remote-access gateway, core-banking server, and disaster-recovery server.

## Run tests

```powershell
python -m unittest discover -v
```

## Project structure

```text
data/bank_topology.json  Sample bank branch/ATM topology
src/propagation.py       Discrete-time worm propagation
src/risk_score.py        Composite urgency-centrality-reach score
src/containment.py       Budget-constrained proposed containment method
src/baselines.py         Fair comparison strategies
src/comparison.py        Reproducible experiment entry point
src/visualize.py         Result charts and topology figure
tests/                   Unit tests
results/                 Generated review/report artifacts
```

This prototype is a simulation only. It does not scan, contact, or interact with production networks.
