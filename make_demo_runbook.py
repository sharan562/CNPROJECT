# -*- coding: utf-8 -*-
"""Generate DEMO_RUNBOOK.pdf — a live-demo script for the containment prototype."""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, HRFlowable

OUT = "DEMO_RUNBOOK.pdf"
DARK = colors.HexColor("#12324a")
GREY = colors.HexColor("#5a5a5a")

ss = getSampleStyleSheet()
title_s = ParagraphStyle("t", parent=ss["Title"], fontSize=20, spaceAfter=2, textColor=DARK)
sub_s = ParagraphStyle("st", parent=ss["Normal"], fontSize=10.5, textColor=GREY, spaceAfter=6)
h2_s = ParagraphStyle("h2", parent=ss["Heading2"], fontSize=11.5, spaceBefore=11, spaceAfter=4, textColor=DARK)
body_s = ParagraphStyle("b", parent=ss["Normal"], fontSize=10, leading=14, spaceAfter=3)
bul_s = ParagraphStyle("bl", parent=body_s, leftIndent=14, spaceAfter=3)

BULLET = "•  "

story = []
story.append(Paragraph("Banking Malware Containment", title_s))
story.append(Paragraph("Live Demo Script — what to click and what to say, in order", sub_s))
story.append(HRFlowable(width="100%", color=GREY, thickness=0.8, spaceAfter=10))


def bullets(items):
    for it in items:
        story.append(Paragraph(BULLET + it, bul_s))


def section(title, do=None, say=None):
    story.append(Paragraph(title, h2_s))
    if do:
        story.append(Paragraph("<b>Do</b>", body_s))
        bullets(do)
    if say:
        story.append(Paragraph("<b>Say</b>", body_s))
        bullets(say)


section("Setup (before the professor looks over your shoulder)", do=[
    "Open PowerShell in <b>Desktop\\PROJECTS\\CNPROJECT</b>.",
    "Run <b>streamlit run app.py</b> and press Enter.",
    "A browser tab opens at http://localhost:8501. Maximize it on the projector.",
])

section("Step 1 — Set the scene", say=[
    "Banking networks connect workstations, ATMs, branch servers, and the core-banking system. If one machine is infected by a self-propagating worm, it spreads sideways across those connections. The hard problem is not detection — it is deciding which few machines to isolate first when the team can only act on a small number at once.",
    "This prototype simulates that and produces an ordered quarantine plan under a fixed budget.",
])

section("Step 2 — Introduce the controls", do=[
    "Point to the left sidebar.",
], say=[
    "On the left I choose the topology — an 8-node branch or a 19-node multi-branch bank — the infected seed machine, the transmission probability, the quarantine budget, and how many trials to average over. Every change recomputes everything live.",
])

section("Step 3 — Headline result: final infection counts", do=[
    "Point to the top table “Final infection counts (single run)”.",
], say=[
    "With no containment, 8 machines end up infected. The proposed method cuts that to 4 — matching the best baseline and beating random and earliest-first.",
])

section("Step 4 — Reproduce the report numbers (default scenario)", do=[
    "In the sidebar set: Seed node = <b>WS_1</b>, transmission probability = <b>0.25</b>, budget = <b>2</b>, Random seed = <b>42</b>. Trials can stay 30, or drop to 10 to make slider changes faster.",
], say=[
    "These are the same settings as the checked-in experiment, so the numbers match the report.",
])

section("Step 5 — The strong result: switch to multi-branch", do=[
    "Set Topology = <b>Multi-branch (19 nodes)</b>, Seed node = <b>WS_N1</b>, transmission probability = <b>0.40</b>, budget = <b>2</b>.",
], say=[
    "On the bigger network — three branches, six ATMs, a core server — the difference is much clearer.",
])

section("Step 6 — Mean infections across trials", do=[
    "Point to the bar chart “Mean final infections across trials”.",
], say=[
    "Averaged over 30 runs with 95% confidence intervals: no containment is about 9.5 infected, the proposed method about 4.3 — roughly a 55% reduction, and the lowest of all five strategies.",
])

section("Step 7 — Infection curves", do=[
    "Point to the “Infection curves” chart.",
], say=[
    "This is spread over time. The proposed strategy's curve stays consistently below no containment.",
])

section("Step 8 — The network topology", do=[
    "Point to the “Network topology” graph.",
], say=[
    "Here is the actual bank network. Blue is susceptible, red is infected, orange is quarantined. The plan quarantines the core server and a workstation, cutting the main lateral path.",
])

section("Step 9 — The quarantine plan (the deliverable)", do=[
    "Point to the “Quarantine plans” table.",
], say=[
    "This is the actionable output — a ranked, budget-limited list of machines to isolate, in order. Not “quarantine everything”, but a specific plan for the response team.",
])

section("Step 10 — Live interaction (the money shot)", do=[
    "Drag the transmission-probability slider up, then drag the budget slider up.",
], say=[
    "Watch — if I make the worm more aggressive, infections rise. If I give the team a bigger budget, infections drop. Everything recomputes live. This is the real simulation, not a recording.",
])

section("Step 11 — Wrap up", say=[
    "So: a budget-aware, topology-informed containment method. It is a simulation — it never touches a real network — but it demonstrates the decision logic a response team would use.",
])

section("If something goes wrong", do=[
    "If the dashboard will not load, run the CLI instead: <b>python -m src.comparison --config config/multibranch.json</b>.",
    "It prints the same numbers and writes charts to results/multibranch/. Open those PNGs and talk through the same points.",
])

section("Two tips", do=[
    "Change one thing at a time and narrate the change.",
    "If slider changes feel slow, set Trials to 10.",
])

doc = SimpleDocTemplate(
    OUT, pagesize=A4,
    leftMargin=2.1 * cm, rightMargin=2.1 * cm,
    topMargin=1.8 * cm, bottomMargin=1.8 * cm,
)
doc.build(story)
print("wrote", OUT)
