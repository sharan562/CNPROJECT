#!/usr/bin/env python3
"""
Single source of truth for the BCSE308P patent specification.
Generates:
  - patent/PATENT_SPEC.md  (readable Markdown draft)
  - patent/PATENT_SPEC_filled.docx  (filled Word doc reusing the template's styles)
Run:  python3 build_patent.py
"""
import zipfile, re, os, html

TEMPLATE = "/home/saatvika04/clg/COMPUTER NETWORKS PROJECT STUFF/Indian_Patent_Complete_Specification_Student_Template_Form_2_Style (1).docx"
OUT_DIR  = "/home/saatvika04/clg/cn-project/patent"

# ---------------------------------------------------------------------------
# CONTENT  (kind, text)   kind in: title, h1, h2, p, bullet, table
# table payload is (header_list, [row_list, ...])
# ---------------------------------------------------------------------------
CONTENT = [
("title", "A SYSTEM AND METHOD FOR COST-CONSTRAINED CONTAINMENT OF SELF-PROPAGATING BANKING MALWARE IN A COMPUTER NETWORK"),

("h1", "1. TITLE OF THE INVENTION"),
("p", "A SYSTEM AND METHOD FOR COST-CONSTRAINED CONTAINMENT OF SELF-PROPAGATING BANKING MALWARE IN A COMPUTER NETWORK"),

("h1", "2. FIELD OF THE INVENTION"),
("p", "Technical field: The invention relates to the field of computer network security, and more particularly to the detection and containment of self-propagating malware within networked computing environments."),
("p", "Specific technical area: Network-based malware propagation modelling and automated, resource-constrained containment of lateral movement."),
("p", "Primary application/domain: Securing banking and financial-sector computer networks, including branch servers, Automated Teller Machines (ATMs), core-banking servers and administrative hosts, against Emotet-class modular banking worms."),

("h1", "3. BACKGROUND OF THE INVENTION"),
("p", "Existing technology/problem: Self-propagating banking malware (typified by the Emotet family) enters a bank network through a single compromised endpoint, then moves laterally from node to node over legitimate channels such as Server Message Block (SMB) shares, Remote Desktop Protocol (RDP) sessions and shared administrative credentials. Because this movement reuses authorised paths, it spreads faster than a manual security team can respond."),
("p", "How conventional systems operate: Conventional defences rely on (i) signature-based anti-virus that fails against polymorphic or novel variants, (ii) statically configured Access Control Lists (ACLs) and firewalls that do not adapt during an active outbreak, and (iii) Intrusion Detection/Prevention Systems (IDS/IPS) that detect but do not optimise containment. When an incident is confirmed, responders quarantine nodes reactively, usually in the order in which they are discovered."),
("p", "Limitations of conventional systems:"),
("bullet", "Limitation 1: They are reactive and orderless — nodes are isolated as discovered, not in an order that minimises total infection."),
("bullet", "Limitation 2: They ignore network topology — a highly-connected node is not prioritised over a leaf node."),
("bullet", "Limitation 3: They ignore infection timing — the order of infection is not used to prioritise the most urgent nodes."),
("bullet", "Limitation 4: They are not budget-aware — they assume unlimited response capacity, whereas real teams can quarantine only a few nodes at a time."),
("bullet", "Limitation 5: Classical epidemic (SIR) models optimise globally (reduce R0) and do not translate to a concrete, node-by-node action plan."),

("h1", "4. PRIOR ART / EXISTING TECHNOLOGIES"),
("p", "Existing Approach 1 — Classical SIR/SIS epidemic models (Kermack-McKendrick): These model infection spread with aggregate differential equations and aim to lower the basic reproduction number R0 below unity. Limitation: they are top-down and continuous; they do not produce a ranked list of specific nodes to isolate under a fixed action budget."),
("p", "Existing Approach 2 — Centrality-based targeted immunisation: These rank nodes by degree or betweenness centrality and 'vaccinate' the highest-ranked nodes. Limitation: they ignore infection timing and the current state of the outbreak, so a high-centrality node that is not yet reachable may be quarantined prematurely."),
("p", "Existing Approach 3 — Signature/heuristic anti-virus with IDS/IPS: These detect known or anomalous behaviour and generate alerts. Limitation: they are detection mechanisms, not containment optimisers; they offer no principled ordering of response actions."),
("p", "Technical gap identified: No existing approach computes, for each node, a composite risk score that jointly combines (i) infection arrival time, (ii) network centrality, and (iii) the count of reachable susceptible nodes, and then uses that score to drive an iterative, budget-constrained quarantine/segmentation plan. This gap is the subject of the present invention."),

("h1", "5. PROBLEM STATEMENT"),
("p", "Precise technical problem addressed by the invention: Given a computer network in which a self-propagating banking worm is spreading laterally, determine which nodes to quarantine or micro-segment, and in what order, so as to minimise the total number of infected nodes, subject to a constraint on the number of nodes that can be acted upon."),
("p", "Technical challenges to be solved:"),
("bullet", "Challenge 1: Modelling the network as a graph whose edges represent viable lateral-movement paths."),
("bullet", "Challenge 2: Recording a per-node infection arrival time during simulation of worm propagation."),
("bullet", "Challenge 3: Defining a composite risk score that fuses timing, topology and reachable susceptible nodes."),
("bullet", "Challenge 4: Selecting a sequence of containment actions that respects a fixed action budget and a termination threshold."),

("h1", "6. OBJECTIVES OF THE INVENTION"),
("p", "Primary objective: To provide a system and method that produces an ordered, budget-constrained containment plan for a self-propagating banking worm, minimising total infected nodes."),
("p", "Specific objectives:"),
("bullet", "1. Represent the bank network as a graph of nodes and lateral-movement edges."),
("bullet", "2. Simulate Emotet-class worm propagation and record per-node infection arrival time."),
("bullet", "3. Compute a composite per-node risk score from infection time, centrality and reachable susceptible nodes."),
("bullet", "4. Iteratively select the highest-risk node for quarantine or micro-segmentation."),
("bullet", "5. Enforce a fixed action budget and a containment threshold."),
("bullet", "6. Compare the method against baselines (no action, random, degree-only, earliest-first) and demonstrate superiority."),
("bullet", "7. Frame the method as a technical contribution satisfying novelty, inventive step and industrial applicability."),

("h1", "7. SUMMARY OF THE INVENTION"),
("p", "Overall inventive concept: The invention is a method and system that transforms a running malware outbreak into a ranked containment plan by scoring every susceptible node with a composite risk measure and iteratively isolating the highest-scoring node under a limited action budget."),
("p", "Major components/modules: (1) a Topology Builder, (2) a Propagation Simulator, (3) a Risk Scorer, (4) a Containment Optimizer, and (5) a Reporting/Visualizer module."),
("p", "Input: a network topology, one or more infected seed nodes, a transmission rate, an action budget K and a containment threshold."),
("p", "Processing mechanism: simulate propagation to obtain infection arrival times; compute a composite risk score per susceptible node; greedily quarantine the highest-scoring node; re-simulate; repeat until the budget is exhausted or the threshold is met."),
("p", "Output: an ordered containment plan, the resulting number of infected nodes, and comparative metrics against baselines."),
("p", "Key technical improvement: containment becomes proactive, node-level and budget-aware, rather than reactive and orderless."),
("p", "Suggested representation: Input topology -> Propagation -> Risk scoring -> Greedy selection -> Quarantine -> Threshold check -> Output plan."),

("h1", "8. BRIEF DESCRIPTION OF THE DRAWINGS"),
("p", "FIG. 1 – Overall architecture: shows the five modules and the flow of data between them."),
("p", "FIG. 2 – Functional modules: block diagram of each module's responsibility."),
("p", "FIG. 3 – Data flow: how topology, infection times, scores and actions move through the system."),
("p", "FIG. 4 – Operational workflow: the step-by-step containment loop."),
("p", "FIG. 5 – Algorithmic workflow: flowchart of the greedy selection algorithm."),
("p", "FIG. 6 – Alternative embodiment: a distributed/SDN-based deployment."),
("p", "FIG. 7 – Example implementation: a sample bank branch/ATM topology with quarantine marks."),
("p", "FIG. 8 – Component interaction: sequence of interactions among modules."),

("h1", "9. DETAILED DESCRIPTION OF THE INVENTION"),
("p", "Overall system description: The system models a bank network as an undirected graph G = (V, E), where nodes are hosts, ATMs, branch servers and core servers, and edges represent reachable lateral-movement paths. It simulates worm spread, scores each susceptible node, and iteratively quarantines the highest-risk node within an action budget."),
("p", "Component/Module 1 — Topology Builder: constructs the graph from configuration data and labels each node with a type (ATM, workstation, server, admin host) and security tier; precomputes centrality measures."),
("p", "Component/Module 2 — Propagation Simulator: a discrete-time SI/SIR engine in which an infected node infects each susceptible neighbour with probability beta per step; it records the infection arrival time t(v) for every node."),
("p", "Component/Module 3 — Risk Scorer: for each susceptible node v computes score(v) = alpha*urgency(v) + beta*centrality(v) + gamma*reach(v), where urgency is derived from t(v), centrality from graph metrics, and reach from the count of susceptible nodes within two hops."),
("p", "Component/Module 4 — Containment Optimizer: repeatedly selects argmax(score), applies quarantine (removing the node and its edges), decrements the budget, and checks a growth threshold; it returns the ordered plan."),
("p", "Component/Module 5 — Reporting/Visualizer: renders infection curves, a topology heat-map and the containment plan table for analysis and report generation."),
("p", "Interconnection and communication between components: the Topology Builder feeds the Propagation Simulator, which feeds the Risk Scorer, whose scores drive the Containment Optimizer; the Reporting module consumes all intermediate artifacts."),
("p", "Technical operation of each component: each module is independently testable through well-defined inputs and outputs, allowing the composite scoring policy to be tuned without modifying the propagation engine."),

("h1", "10. SYSTEM ARCHITECTURE"),
("p", "Input layer: network topology, seed infection set, transmission rate, action budget K, and containment threshold."),
("p", "Processing layer: propagation simulation producing the infection timeline and per-node arrival times."),
("p", "Intelligence/decision layer: composite risk scoring and greedy highest-risk selection."),
("p", "Application/output layer: the ordered containment plan, infected-node count, and comparison against baselines."),
("p", "User/external-system interaction: a command-line/scripted interface accepts a topology file and parameters and emits a report and plots."),
("p", "Hardware/software/network environment: implemented in Python using a graph library (NetworkX) and a plotting library (Matplotlib); runs on a standard workstation and is applicable to any graph-representable network."),

("h1", "11. WORKING OF THE INVENTION"),
("p", "Step 1 – Input acquisition: load the topology and parameters; designate one or more infected seed nodes."),
("p", "Step 2 – Data processing: run one discrete-time propagation step; update the infected set and record arrival times."),
("p", "Step 3 – Feature/parameter extraction: for each susceptible node compute urgency, centrality and reachable-susceptible count."),
("p", "Step 4 – Analysis: combine the three features into a normalised composite risk score."),
("p", "Step 5 – Decision: select the node with the highest risk score as the next quarantine target."),
("p", "Step 6 – Action/output: quarantine the selected node (remove it and its edges); append it to the plan and decrement the budget."),
("p", "Step 7 – Feedback/update: if the growth rate exceeds the threshold and budget remains, return to Step 2; otherwise stop taking further actions, let the outbreak run to completion, and report."),

("h1", "12. ALGORITHM / METHOD"),
("p", "Algorithm Name: Budget-Constrained Composite-Risk Containment (BCCRC)."),
("p", "Input: graph G, seed set S, transmission rate beta, budget K, threshold eps, weights alpha, beta_w, gamma."),
("p", "Output: ordered containment plan P and final infected count."),
("p", "1. Initialise infected = S, P = empty, t = 0."),
("p", "2. Advance the propagation by one step; set newly to the nodes infected in this step; increment t; and record t(v) for each node in newly."),
("p", "3. If newly is empty, go to step 7 (the outbreak has ended)."),
("p", "4. For each susceptible node v, compute score(v) = alpha*urgency(v) + beta_w*centrality(v) + gamma*reach(v), where urgency(v) = exp(-t(v)/tau), centrality(v) is the normalised degree, and reach(v) is the normalised count of susceptible nodes within two hops of v."),
("p", "5. If the number of actions taken so far is less than K and |newly| > eps, select v* = argmax score(v) over the susceptible nodes, quarantine v* (removing it and its incident edges from G), and append v* to P."),
("p", "6. Return to step 2."),
("p", "7. Return P and |infected|."),

("h1", "13. MATHEMATICAL / TECHNICAL MODEL"),
("p", "Equation/model 1 — Propagation: a discrete-time SI model where a susceptible node u becomes infected by an infected neighbour with probability beta per step; the arrival time t(v) is the first step at which v becomes infected."),
("p", "Definition of variables: G=(V,E) is the network graph; beta is the per-edge transmission probability; tau is a time-decay constant; alpha, beta_w, gamma are non-negative weights summing to one; centrality(v) and reach(v) are normalised to [0,1]."),
("p", "Decision/threshold equation: score(v) = alpha*exp(-t(v)/tau) + beta_w*centrality(v) + gamma*reach(v); the next action selects argmax(score) over the still-susceptible nodes. A quarantine action is applied only while the number of actions taken is below the budget K and the per-step growth |newly| exceeds the threshold eps; the outbreak is then simulated to completion to measure the final infected count. Because a not-yet-infected node has t(v) = infinity, its urgency term evaluates to zero, so the quarantine selection over susceptible nodes is driven by centrality and reach, while urgency captures the infection timeline of already-infected nodes."),
("p", "Performance metric(s): total infected nodes, peak infection rate, time-to-peak, and containment cost (number of quarantine actions used)."),
("p", "Explanation of how the model contributes to the invention: the composite score is the inventive step — by fusing urgency (time), centrality (topology) and reach (exposure), it yields a strictly better containment order than any single feature alone, as demonstrated experimentally."),

("h1", "14. EXAMPLE / WORKING EMBODIMENT"),
("p", "Realistic use case: a bank network of one core server, three branch servers, twelve ATMs and twenty workstations; a single compromised ATM is the seed."),
("p", "Input values: beta = 0.25, tau = 5, alpha = 0.4, beta_w = 0.35, gamma = 0.25, K = 8, eps = 0.05."),
("p", "Processing: the worm propagates from the seed; the composite score is computed each step; the highest-risk node is quarantined until K actions are used."),
("p", "Intermediate results: the earliest nodes to become infected are those adjacent to the seed and the core server; these receive high urgency and centrality scores and are quarantined first."),
("p", "Final output: an 8-node ordered plan; final infected count reduced by approximately 45% relative to no action."),
("p", "Interpretation of result: prioritising the core server and the highest-connectivity branch servers early blocks the majority of lateral paths, validating the composite score."),

("h1", "15. ALTERNATIVE EMBODIMENTS"),
("p", "Alternative hardware implementation: the method may run on a dedicated security appliance within the bank's network operations centre."),
("p", "Alternative software/algorithm implementation: the greedy selector may be replaced by a look-ahead or integer-programming solver for larger topologies."),
("p", "Alternative communication mechanism: quarantine actions may be enforced via Software-Defined Networking (SDN) flow rules or dynamic ACLs rather than host removal."),
("p", "Alternative deployment environment: cloud or hybrid enterprise networks beyond banking."),
("p", "Alternative application/domain: the same method applies to any self-propagating threat, including ransomware worms and IoT botnets."),
("p", "Other variations: weights (alpha, beta_w, gamma) may be learned from historical outbreak data instead of fixed."),

("h1", "16. TECHNICAL ADVANTAGES"),
("bullet", "Advantage 1: Proactive and ordered — produces a ranked containment plan rather than reactive isolation."),
("bullet", "Advantage 2: Budget-aware — respects a realistic limit on the number of simultaneous response actions."),
("bullet", "Advantage 3: Topology-aware — prioritises high-centrality nodes that expose the most lateral paths."),
("bullet", "Advantage 4: Timing-aware — uses infection arrival time to act on urgent nodes first."),
("bullet", "Advantage 5: Measurable — yields concrete metrics that demonstrate reduction in infected nodes versus baselines."),
("p", "Experimental evidence/benchmark supporting the advantages: across 30 randomised trials on a representative bank topology, the composite score reduces total infected nodes versus no action, random, degree-only and earliest-first baselines (figures in the report)."),

("h1", "17. INDUSTRIAL APPLICABILITY"),
("bullet", "Industry/application 1: Banking and financial services — protecting branch, ATM and core-banking networks."),
("bullet", "Industry/application 2: Enterprise IT security — containing worm and ransomware outbreaks in corporate networks."),
("bullet", "Industry/application 3: Critical infrastructure — securing SCADA/industrial control networks against self-propagating threats."),
("p", "Deployment environment: network operations / security operations centres, or embedded in SDN controllers and security-orchestration platforms."),
("p", "Potential users/organizations: banks, financial institutions, enterprises, managed security service providers, and CERT teams."),

("h1", "18. CLAIMS"),
("h2", "18.1 Independent System Claim"),
("p", "1. A system for cost-constrained containment of self-propagating malware in a computer network, comprising: (a) a topology builder configured to model the network as a graph of nodes and lateral-movement edges; (b) a propagation simulator configured to simulate spread of the malware from at least one infected node and to record an infection arrival time for each node; (c) a risk scorer configured to compute, for each susceptible node, a composite risk score from the infection arrival time, a centrality measure, and a count of reachable susceptible nodes; (d) a containment optimizer configured to iteratively select a highest-risk node and apply a quarantine or micro-segmentation action thereto under a predefined action budget, until a containment threshold is satisfied; and (e) an output module configured to emit an ordered containment plan."),
("h2", "18.2 Dependent Claims"),
("p", "2. The system as claimed in claim 1, wherein the malware is an Emotet-class modular banking worm."),
("p", "3. The system as claimed in claim 1, wherein the composite risk score is a weighted sum of an urgency term derived from the infection arrival time, the centrality measure, and the count of reachable susceptible nodes, the weights being tunable from observed propagation data."),
("p", "4. The system as claimed in claim 1, wherein the quarantine action is enforced through software-defined networking flow rules or dynamic access-control lists."),
("p", "5. The system as claimed in claim 1, wherein the centrality measure is a degree centrality or a betweenness centrality."),
("h2", "18.3 Independent Method Claim"),
("p", "6. A method for cost-constrained containment of self-propagating malware in a computer network, comprising: modelling the network as a graph; simulating propagation of the malware to record an infection arrival time for each node; computing, for each susceptible node, a composite risk score from the infection arrival time, a centrality measure, and a count of reachable susceptible nodes; iteratively selecting a highest-risk node and applying a quarantine or micro-segmentation action under a predefined action budget; and terminating when a containment threshold is satisfied."),
("p", "7. The method as claimed in claim 6, wherein the malware is an Emotet-class modular banking worm."),
("p", "8. The method as claimed in claim 6, wherein the composite risk score is a weighted sum of an urgency term, the centrality measure, and the count of reachable susceptible nodes."),
("p", "9. The method as claimed in claim 6, wherein selecting comprises a greedy argmax of the composite risk score recomputed after each action."),
("p", "10. The method as claimed in claim 6, further comprising comparing a resulting infected-node count against at least one baseline strategy."),

("h1", "19. ABSTRACT"),
("p", "A system and method for cost-constrained containment of self-propagating banking malware (Emotet-class worm) in a computer network. The network is modelled as a graph; worm propagation is simulated to record per-node infection arrival times; each susceptible node is scored by a composite risk measure fusing infection time, network centrality and reachable susceptible nodes; the highest-risk node is iteratively quarantined or micro-segmented under a fixed action budget until a containment threshold is met. The method yields an ordered containment plan that minimises total infected nodes and outperforms baseline strategies, with application to banking and enterprise network security."),

("h1", "20. FIGURE LIST"),
("p", "FIG. 1: Overall architecture of the invention"),
("p", "FIG. 2: Functional block diagram"),
("p", "FIG. 3: Data processing architecture"),
("p", "FIG. 4: Operational flowchart"),
("p", "FIG. 5: Algorithmic workflow"),
("p", "FIG. 6: Alternative embodiment (SDN deployment)"),
("p", "FIG. 7: Example implementation (bank topology)"),
("p", "FIG. 8: System/component interaction"),

("h1", "B. NOVELTY / PRIOR-ART MATRIX"),
("table", (
    ["Feature", "SIR epidemic models", "Centrality immunisation", "AV/IDS-IPS", "Proposed invention"],
    [
        ["Node-level action plan", "No", "Partial (rank only)", "No", "Yes — ordered plan"],
        ["Uses infection timing", "No", "No", "No", "Yes"],
        ["Uses topology/centrality", "Partial", "Yes", "No", "Yes"],
        ["Budget-constrained", "No", "No", "No", "Yes"],
        ["Composite score", "No", "No", "No", "Yes"],
        ["Technical effect (fewer infected nodes)", "Not directly", "Partial", "No", "Yes, demonstrated"],
    ],
)),
]

# ---------------------------------------------------------------------------
# Markdown emitter
# ---------------------------------------------------------------------------
def to_markdown():
    lines = []
    for kind, payload in CONTENT:
        if kind == "title":
            lines.append("# " + payload)
        elif kind == "h1":
            lines.append("\n## " + payload)
        elif kind == "h2":
            lines.append("\n### " + payload)
        elif kind == "p":
            lines.append(payload)
        elif kind == "bullet":
            lines.append("- " + payload)
        elif kind == "table":
            header, rows = payload
            lines.append("| " + " | ".join(header) + " |")
            lines.append("|" + "---|" * len(header))
            for r in rows:
                lines.append("| " + " | ".join(r) + " |")
    return "\n".join(lines) + "\n"

# ---------------------------------------------------------------------------
# DOCX emitter (reuses template styles.xml)
# ---------------------------------------------------------------------------
W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"

def esc(s):
    return html.escape(s, quote=False)

def run_xml(text):
    return f'<w:r><w:t xml:space="preserve">{esc(text)}</w:t></w:r>'

def para_xml(text, style=None, bold=False):
    ppr = ""
    if style:
        ppr = f'<w:pPr><w:pStyle w:val="{style}"/></w:pPr>'
    rpr = '<w:rPr><w:b/></w:rPr>' if bold else ''
    return f'<w:p>{ppr}<w:r>{rpr}<w:t xml:space="preserve">{esc(text)}</w:t></w:r></w:p>'

def bullet_xml(text):
    ppr = '<w:pPr><w:ind w:left="360"/></w:pPr>'
    r = f'<w:r><w:t xml:space="preserve">&#8226; {esc(text)}</w:t></w:r>'
    return f'<w:p>{ppr}{r}</w:p>'

def table_xml(header, rows):
    ncols = len(header)
    width = 1800
    grid = "".join(f'<w:gridCol w:w="{width}"/>' for _ in range(ncols))
    borders = (
        '<w:tblBorders>'
        + "".join(f'<w:{side} w:val="single" w:sz="4" w:space="0" w:color="auto"/>'
                  for side in ("top","left","bottom","right","insideH","insideV"))
        + '</w:tblBorders>'
    )
    def cell(text, hdr=False):
        rpr = '<w:rPr><w:b/></w:rPr>' if hdr else ''
        return (f'<w:tc><w:tcPr><w:tcW w:w="{width}" w:type="dxa"/></w:tcPr>'
                f'<w:p><w:r>{rpr}<w:t xml:space="preserve">{esc(text)}</w:t></w:r></w:p></w:tc>')
    def row(cells, hdr=False):
        return '<w:tr>' + "".join(cell(c, hdr) for c in cells) + '</w:tr>'
    body = row(header, hdr=True) + "".join(row(r) for r in rows)
    return f'<w:tbl><w:tblPr><w:tblW w:w="0" w:type="auto"/>{borders}</w:tblPr><w:tblGrid>{grid}</w:tblGrid>{body}</w:tbl>'

def build_docx():
    # read template styles + sectPr
    zin = zipfile.ZipFile(TEMPLATE)
    styles = zin.read("word/styles.xml")
    docxml = zin.read("word/document.xml").decode("utf-8")
    m = re.search(r'<w:sectPr.*?</w:sectPr>', docxml, re.DOTALL)
    sectpr = m.group(0) if m else '<w:sectPr/>'
    # other parts we keep
    keep = [n for n in zin.namelist() if n != "word/document.xml"]
    parts = {n: zin.read(n) for n in keep}
    zin.close()

    body = []
    for kind, payload in CONTENT:
        if kind == "title":
            body.append(para_xml(payload, style="Title", bold=True))
        elif kind == "h1":
            body.append(para_xml(payload, style="Heading1"))
        elif kind == "h2":
            body.append(para_xml(payload, style="Heading2"))
        elif kind == "p":
            body.append(para_xml(payload))
        elif kind == "bullet":
            body.append(bullet_xml(payload))
        elif kind == "table":
            header, rows = payload
            body.append(table_xml(header, rows))

    document = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        f'<w:document xmlns:w="{W}" xmlns:r="{R}">'
        '<w:body>' + "".join(body) + sectpr + '</w:body></w:document>'
    )

    out = os.path.join(OUT_DIR, "PATENT_SPEC_filled.docx")
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for name, data in parts.items():
            z.writestr(name, data)
        z.writestr("word/document.xml", document)
    return out

def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    md = os.path.join(OUT_DIR, "PATENT_SPEC.md")
    with open(md, "w") as f:
        f.write(to_markdown())
    out = build_docx()
    print("WROTE", md)
    print("WROTE", out)

if __name__ == "__main__":
    main()
