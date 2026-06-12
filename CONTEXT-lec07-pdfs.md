# Lecture 07 Digest: Reverse Engineering & Token-Efficient Agentic AI with Graphify & Obsidian

**Course:** University of Haifa, "Orchestration of AI Agents" (203.3763)
**Lecture:** 07 (4-part series)
**Date:** June 2026
**Instructor:** Dr. Yoram Segal

---

## Executive Summary per PDF

### Part A: Active Knowledge & Context (lecture-07-active-knowledge-part-a.pdf)
Introduces the "Lost in the Middle" problem where LLM performance degrades when relevant information is placed in the middle of a long context window. Establishes the core motivation: agents reading unfamiliar code face context bottlenecks (~70-95% of retrieval overhead is wasted), especially with "dumb" RAG. Proposes the three-layer architecture (Files → Graphify → Obsidian) as the solution framework. Maps to **HW4 deliverable: understanding why token efficiency matters and how navigation reduces wasted context**.

### Part B: Graph Architecture (lecture-07-graph-architecture-part-b.pdf)
Defines graph-based code representation: nodes (files, classes, functions), edges (calls, imports, inheritance, inferred relationships), and evidence layers (EXTRACTED, INFERRED, AMBIGUOUS). Covers AST extraction, knowledge graphs, and how to read graphs visually and semantically. Introduces centrality metrics (betweenness, degree), communities, and hubs as complexity hotspots. Includes "God Node" detection and traceability patterns. Maps to **HW4 deliverable: building graph.json with proper node/edge typing and confidence scoring**.

### Part C: Graphify Pipeline (lecture-07-graphify-part-c.pdf)
Deep dive into the Graphify CLI: extraction pipeline (detect → extract → build → cluster → export), multi-layer synthesis (Code Structure, Media/Text, Semantic Layer from LLM), and output formats (graph.json, graph.html, GRAPH_REPORT.md). Shows how Graphify consumes raw code and produces a queryable graph with evidence metadata. Covers the "From Files to System Understanding" workflow and evidence scale (0.55–0.95 confidence thresholds). Maps to **HW4 deliverable: running Graphify on unfamiliar code and interpreting outputs**.

### Part D: Summary (lecture-07-summary.pdf)
Recap of all four components: Graphify (code graph extraction), LLM Wiki (Markdown-based memory-over-retrieval), Claude SKILLs (token-efficient context routing), and index.md/hot.md as navigational hubs. Emphasizes how the three layers fight "Lost in the Middle" via compaction, guided retrieval, and position-aware context design. Maps to **HW4 deliverable: assembling a complete HW4 submission integrating all three layers**.

---

## Graphify: Code as Graph

### What It Is
**Graphify** is a code analysis CLI that transforms source code (Python, LaTeX, PDFs, etc.) into a knowledge graph (graph.json). It operates as a deterministic AST parser plus LLM-powered semantic inference layer, producing:
- **Nodes:** files, classes, functions, modules, documents
- **Edges:** calls, imports, inheritance, inferred relationships, "semantically similar" annotations
- **Confidence scores:** EXTRACTED (high), INFERRED (medium), AMBIGUOUS (low)

### Graph Representation & Schema

**Node Types:**
- `File` (e.g., `checkout_service.py`) – code file
- `Code` (e.g., `AuthController.py`) – deterministic from AST
- `Module` – Python module or package
- `Class` – OOP abstraction
- `Function` – callable definition
- `PRD`, `Docs`, `Rationale` – documentation artifacts

**Edge Types (Three Categories):**

| **Type** | **Meaning** | **Extraction** |
|---|---|---|
| **EXTRACTED** | Direct code dependency—import, call, implements, inheritance | AST parsing (Python token analysis, direct source lookup) |
| **INFERRED** | LLM hypothesis—semantic inference from PRD/docs and code context | Claude-7 Subgraphs; confidence label applied (e.g., "CONFIDENCE: 88%") |
| **AMBIGUOUS** | Ambiguous or uncertain relation—dashed edge in graph, requires manual check | Symbol not found, unclear reference, multiple candidates |

**Example Edge Semantics:**
- `LoginPage.txt` —(calls)→ `AuthController.py` = extracted
- `PRD_auth.md` —(rationale_for: CONFIDENCE 88%)→ `AuthController.py` = inferred
- `Module C` —(ambiguous: "maybe depends on Service E?")→ `Service E` = ambiguous (dotted line)

### Graphify Pipeline Output

**Command:** `graphify extract <folder>` → outputs:

1. **graph.json** (primary output)
   - JSON structure with nodes, edges, clusters, evidence metadata
   - Each edge contains: `source`, `target`, `relation`, `label`, `confidence`, `source_file`
   - Example: `{"source": "checkout_service.py", "target": "payment_api.py", "relation": "calls", "label": "process_payment", "confidence": 0.95}`

2. **GRAPH_REPORT.md** (narrative summary)
   - List of nodes and edges extracted
   - Rationale for each high-confidence cluster
   - Complexity metrics (degree, betweenness, community assignment)
   - God Nodes flagged

3. **graph.html** (visual)
   - Interactive visualization with communities colored, hubs emphasized
   - Supports zoom, pan, filtering by confidence

### Key Graphify Outputs

- **Detect phase:** scan raw folder for code, docs, PDFs
- **Extract phase:** AST parse + semantic layer inference (Claude-7)
- **Build phase:** construct graph with evidence labels
- **Cluster phase:** community detection via modularity (louvain); identify hubs
- **Export phase:** write graph.json, GRAPH_REPORT.md, graph.html

**Token efficiency benefit:** Graphify reduces ~71.5% of irrelevant file reads vs. naive chunking by using structural + semantic clustering.

---

## Obsidian Vault: Active Knowledge Space

### Role of index.md and hot.md

**index.md** = "Hub" / navigation entry point
- Lists all projects (Portfolio) and domains (Domain) in the vault
- Provides hierarchical overview (Portfolio → Domains → Projects → Components)
- Acts as "one click away" from any major concept
- Wikilinks guide the user to secondary pages

**hot.md** = "Hot Topics" / frequently accessed or critical concepts
- Usually indexed from index.md with special status
- Contains synthesis of currently-active debugging/query concepts
- Updated during agent queries (e.g., after running graph-guided search)
- Serves as a "refresh" mechanism to prevent context rot

### Vault Structure (Portfolio DNA)

The vault is organized as a **three-level nested system:**

```
Vault/
├── index.md                           (Hub - "go here first")
├── hot.md                             (Hot topics - active concepts)
├── log.md                             (Audit trail / decision log)
└── wiki/
    ├── [Domain 1]/
    │   ├── README.md                  (Domain overview)
    │   ├── [Project 1].md             (Project-specific page)
    │   └── [Component pages]          (Architecture + rationale)
    └── [Domain 2]/
        ├── README.md
        └── [Project pages]
```

**Levels of Vault Organization:**
- **Portfolio** (top): All work represented in vault; linked via index.md
- **Domain** (middle): Thematic grouping (Python, LaTeX, etc.); contains domains within wiki/
- **Project** (bottom): Specific codebase or document set; PRD, PLAN, TODO, Code references

### Pages to Create

**Mandatory:**
1. **index.md** – Portfolio hub; list all 10 domains + 20 projects; wikilinks to domain READMEs
2. **hot.md** – Actively queried concepts; refreshed during agent runs
3. **log.md** – Decision log; trace of query → finding → action

**Per Domain:**
4. **wiki/[DomainName]/README.md** – Domain intro; list projects in this domain

**Per Project (within domain):**
5. **wiki/[DomainName]/[ProjectName].md** – Project overview; link to PRD, PLAN, Code, architecture diagram

**Linking Conventions:**
- **Wikilinks:** `[[index.md]]`, `[[hot.md]]`, `[[wiki/Python/AuthFlow.md]]`
- **Transclusion:** `![[wiki/Python/AuthFlow.md]]` embeds full page
- **Backlinks:** Obsidian auto-indexes; allows reverse navigation
- **Tags:** Use `#prd`, `#code`, `#decision` for filtering in searches

### Obsidian as Navigation Vault

Obsidian's role is **not to store all code**, but to:
- Provide **semantic memory** (Markdown-based, human-readable)
- Enable **guided retrieval** (index.md as entry; wikilinks guide agent queries)
- Reduce **"Lost in the Middle"** via Parallel Depth Scan (PDS) in Obsidian fetch: read index.md first, then choose which wiki pages to load based on query relevance
- Track **decisions & rationale** (wiki pages annotate WHY code exists, not just WHAT it does)

---

## "Lost in the Middle" & Context Windows

### The Core Problem

**"Lost in the Middle"** (Liu et al., 2024): When long context windows are passed to LLMs, information placed in the **middle** suffers ~40–50% performance drop compared to beginning/end.

**Why it matters for HW4:**
- Reading unfamiliar code naively = passing entire codebase to Claude
- Performance decays when bug-relevant code is "buried" in the middle
- **Example:** 50,000 LoC codebase; the bug is in a 200-line module in the middle → Claude's inference quality degrades significantly

### How Graph-Guided Navigation Saves Tokens

**Baseline (naive RAG):**
- Chunked retrieval: break code into 1K-token chunks
- Vector similarity: find ~top-k similar chunks to query
- Problem: chunks may be incoherent; context includes unrelated code
- Token waste: ~70–95% of retrieved tokens are irrelevant

**Graph-Guided (Graphify + Obsidian):**
1. **Query** → route to index.md (cheap read)
2. **index.md** → suggests relevant domain/project via wikilinks
3. **Navigate** → load only relevant wiki pages (e.g., AuthFlow, not entire codebase)
4. **Graph context** → fetch from graph.json only nodes reachable from query source (e.g., "find all calls to checkout_service")
5. **Result:** ~60% reduction in tokens passed to Claude, higher signal-to-noise

### Mechanism: Position-Aware Context Design

**Key insights:**
- **Beginning:** Query + index.md (query context)
- **Middle:** Only relevant wiki pages / graph subgraph (active knowledge)
- **End:** SKILL summaries / compact rationale (executive summary)

**Multi-Scale Positional Encoding:**
- Encode position of each chunk relative to total window
- Attend first to beginning (query), then middle (evidence), then end (summary)
- Reduces "middle rot" by explicitly emphasizing middle content via attention calibration

---

## God Nodes / Centrality / Complexity Hotspots

### Definition

**God Node** (bottleneck in Graphify parlance) = a node with **unusually high degree and betweenness centrality**, such that:
- Many other nodes depend on it (degree ≥ 50 incoming edges is a red flag)
- Lies on many shortest paths through the graph (high betweenness)
- Changes to this node risk cascading failures

**Example:** An `AuthController` class that all services call → God Node.

### How to Detect

**Graphify detection:**
1. **Degree:** Count in-degree + out-degree of each node
2. **Betweenness:** Run Betweenness Centrality algorithm on DAG of the code graph
3. **Threshold:** Node with degree > 50 or betweenness > some percentile (e.g., 90th) → flag in GRAPH_REPORT.md
4. **Visual:** Oversized nodes in graph.html; red/orange color coding

**In GRAPH_REPORT.md:**
```
## God Nodes
- AuthController.py (degree: 67, betweenness: 0.85) [CRITICAL]
- SessionStore.py (degree: 43, betweenness: 0.72) [WARNING]
```

### Why They Matter for Debugging

- **Single Point of Failure:** Bug in God Node affects many downstream tests
- **Bug Likelihood:** God Nodes are high-mutation targets (more changes = more bugs)
- **Trace Efficiency:** Start debugging from God Node; investigate incoming/outgoing edges first
- **Refactoring Signal:** God Node candidates for refactoring / splitting into smaller modules

---

## Token Efficiency: Methodology & Metrics

### Baseline vs. Graph-Guided Comparison

**Metrics to track:**

| **Metric** | **Baseline (Naive RAG)** | **Graph-Guided** | **Improvement** |
|---|---|---|---|
| **Total tokens used** | T_baseline (e.g., 50K) | T_graph (e.g., 20K) | ~60% reduction |
| **Files read** | F_baseline (e.g., 150 files) | F_graph (e.g., 25 files) | ~80% reduction |
| **Agent iterations** | Iter_baseline (e.g., 5) | Iter_graph (e.g., 2) | 2.5x faster |
| **Time-to-root-cause** | T_baseline (e.g., 180s) | T_graph (e.g., 40s) | 4.5x faster |
| **Bug found?** | Yes/No | Yes/No | Same accuracy |

### Measurements to Report in HW4

1. **Graph extraction cost:**
   - Time to run Graphify CLI
   - Nodes, edges, communities detected
   - Confidence distribution (% EXTRACTED vs. INFERRED vs. AMBIGUOUS)

2. **Navigation efficiency:**
   - Size of index.md + hot.md (in tokens)
   - Depth of wiki pages visited (e.g., "2 hops from index.md to bug")
   - Tokens per file in graph-guided vs. naive approach

3. **Agent execution:**
   - Number of LLM calls in baseline vs. graph-guided
   - Tokens per call (should decrease after first 2 calls with graph guidance)
   - Latency per agent iteration

4. **Quality metrics:**
   - Did agent find the bug? (Y/N)
   - Did agent explain the root cause? (accuracy: %)
   - False positives in graph edges (optional: manual validation)

### Token Efficiency Formula

```
Efficiency = (Tokens_baseline - Tokens_graph) / Tokens_baseline × 100%
Target: ≥ 50% reduction
```

---

## Agent Architecture

### CrewAI vs. LangGraph

**Lecture guidance:**
- **CrewAI** preferred for **sequential, hierarchical tasks** (Manager → Researcher → Developer workflow)
- **LangGraph** preferred for **graph-based, iterative tasks** (where state flows through conditional nodes)

**For HW4 bug-finding:** Use **LangGraph** because:
1. Query formulates as nodes (Query → Graph Navigation → Code Reading → Hypothesis → Validation)
2. Conditional edges (if graph edge has AMBIGUOUS confidence, branch to manual validation)
3. State persists across iterations (found bug? → exit; no evidence? → refine query)

### Graph-Guided Agent Design

**Pseudocode:**

```
Agent workflow:
  1. INITIALIZE
     - Load graph.json
     - Load index.md, hot.md
     - Store query ("find the bug causing X")

  2. QUERY ROUTER
     - Parse query
     - Identify "bug symptoms" (e.g., "table overflow")
     - Route to relevant hot.md section

  3. GRAPH NAVIGATION
     - Start from hot.md nodes
     - Follow EXTRACTED edges only (confidence > 0.8)
     - Build subgraph of reachable nodes within K hops

  4. CODE READING
     - For each node in subgraph:
       - Read code snippet (vs. entire file)
       - Check for match with bug symptoms
       - Update hypothesis

  5. HYPOTHESIS REFINEMENT
     - If no match: backtrack to graph, try INFERRED edges
     - If match found: inspect related nodes (callers, called-by)

  6. VALIDATION
     - Run unit tests on suspected code
     - Confirm root cause
     - Generate explanation

  7. OUTPUT
     - Bug location + line number
     - Root cause explanation
     - Fix proposal (optional)
```

### Context-Reduction Mechanisms

1. **Subgraph fetching:** Only include K-hop neighbors from bug symptoms
2. **Confidence filtering:** Only trust EXTRACTED edges initially; escalate to INFERRED if needed
3. **Compaction:** Summarize large files to their key functions + comments
4. **/compact + /refresh:** SKILL mechanism to reset LLM context mid-query (clears irrelevant middle context)
5. **Index-first retrieval:** Always start with index.md; branch to specific wiki pages based on query relevance

---

## Reverse Engineering: Block & Class Diagrams

### How to Extract from Unfamiliar Code

**Step 1: File-level structure**
- Read all .py, .java, .ts files
- Build a DAG: import relationships
- Generate block diagram: folders → modules → high-level functions

**Step 2: AST extraction (Graphify step)**
- Parse each file with AST
- Extract class definitions, method signatures
- Record inheritance, interfaces
- Build OOP diagram: classes → methods → fields

**Step 3: Semantic inference**
- Use LLM (Claude) to label nodes by responsibility
- "This class manages authentication" vs. "data model"
- Assign to layer: API, Service, Repository, DAO, etc.

**Step 4: Visualization**
- graph.html from Graphify shows all of this
- Manually draw block diagram (optional): tier 1 (API) → tier 2 (Services) → tier 3 (Data)
- Draw class diagram: only EXTRACTED edges + key inheritance

**Example (from Graphify output):**

```
Block Diagram (high-level):
┌─ API Layer ─────────────────┐
│  LoginAPI.py                │
│  CheckoutAPI.py             │
└────────┬────────────────────┘
         │
         v
┌─ Service Layer ──────────────┐
│  AuthService.py              │
│  PaymentService.py           │
│  ✖ God Node: SessionStore    │
└────────┬────────────────────┘
         │
         v
┌─ Data Layer ──────────────────┐
│  UserDB.py                    │
│  TransactionDB.py             │
└───────────────────────────────┘
```

---

## Verbatim Instructions & Key Gotchas

### Do's

- **DO:** Use Graphify to extract the code graph before any manual analysis
- **DO:** Always start HW4 investigation with index.md and hot.md in Obsidian
- **DO:** Run graph-guided queries (follow EXTRACTED edges first)
- **DO:** Report token counts and file-read metrics in your HW4 submission (this is the proof of efficiency)
- **DO:** Mark edges with confidence scores; trust EXTRACTED > INFERRED > AMBIGUOUS
- **DO:** Test hypothesis by running unit tests on suspected files
- **DO:** Explain WHY the bug occurred, not just WHAT/WHERE

### Don'ts

- **DON'T:** Read entire code files naively; use Graphify to identify relevant subgraphs first
- **DON'T:** Trust AMBIGUOUS edges without manual validation
- **DON'T:** Skip index.md setup; it's required for token efficiency gains
- **DON'T:** Pass >100K tokens of code to Claude without graph guidance
- **DON'T:** Assume all inferred edges are correct; verify with code inspection
- **DON'T:** Build the Obsidian vault by hand; use structured templates (Frontmatter: type, status, project)

### From the Lecture

**Key phrase (verbatim):** "הטיפול בתחזוקה הדרושה היא להקטין את השטח של הרשימה המוזכרת ב-Context Window" (The maintenance required is to reduce the surface area of the mentioned list in the Context Window)

**Implication:** Don't try to fit more code; instead, fit SMARTER code via graph-guided chunking.

**Hebrew instruction (transliterated):** "קרא תחילה את ה-index.md, אחר כך עבור לעמודים ב-wiki ככל הנדרש" = "Read index.md first, then navigate to wiki pages as needed"

---

## Differences from Written HW4 Spec

### Cross-Reference with hw4-spec-ex04-graphify-obsidian-reverse-engineering.pdf

The lectures **ADD/CLARIFY** these points to the spec:

1. **graph.json schema** (lectureDefined): Must include `confidence`, `source_file`, `relation` fields for each edge
2. **Evidence scale** (lecture-specific): 0.55–0.95 confidence range; only report edges with confidence > 0.70 in primary findings
3. **God Node detection** (lecture-emphasized): GRAPH_REPORT.md should explicitly flag nodes with degree > 50 or betweenness in 90th percentile
4. **Token efficiency metrics** (lecture-required): Report # files read, # tokens used, # iterations for both baseline and graph-guided approaches
5. **Obsidian hot.md** (lecture-specific): Must exist; used by agent for dynamic query routing
6. **LangGraph recommendation** (lecture-guidance): Use LangGraph over CrewAI for state-based graph traversal
7. **Compaction / Refresh** (lecture-specific): Optional SKILL mechanism; if used, document context reset points in agent log

### No Contradictions Found

The lecture materials expand on and validate the spec; they do not contradict it. All deliverables (graph.json, GRAPH_REPORT.md, Obsidian vault, agent run log) align with spec requirements.

---

## Summary Table: Lecture Themes → HW4 Deliverables

| **Lecture Theme** | **Key Concept** | **HW4 Deliverable** | **Success Criteria** |
|---|---|---|---|
| Lost in the Middle | Context decay in long windows | Token metrics (baseline vs. graph-guided) | ≥50% token reduction |
| Graphify extraction | Code → knowledge graph | graph.json + GRAPH_REPORT.md | All nodes/edges typed; confidence scored |
| Obsidian vault | Navigation + memory | index.md, hot.md, wiki/ structure | Wikilinks functional; query-routable |
| God Nodes | Bottleneck detection | GRAPH_REPORT.md flagged nodes | High-degree / high-betweenness identified |
| Agent architecture | Graph-guided traversal | LangGraph agent code + execution log | Bug found + root cause explained |
| Token efficiency | Proof of savings | Metrics table + chart | Baseline > graph-guided (measured) |

---

## Recommended Reading Order for HW4 Worker

1. **Start:** This digest (executive overview)
2. **Then:** Lecture 07 Part C (Graphify pipeline details)
3. **Then:** Lecture 07 Part B (Graph architecture + evidence scale)
4. **Then:** Lecture 07 Part A (Context window problem)
5. **Finally:** Lecture 07 Part D (Summary + integration)
6. **Alongside:** Written HW4 spec (reference for deliverables)

---

## File References & Further Study

- **graph.json example schema:** lecture-07-graphify-part-c.pdf, p. ~18
- **Evidence scale diagram:** lecture-07-graph-architecture-part-b.pdf, p. ~20
- **God Node detection:** lecture-07-graph-architecture-part-b.pdf, p. ~15
- **Obsidian anatomy:** lecture-07-graph-architecture-part-b.pdf, p. ~12
- **Token efficiency comparison:** lecture-07-summary.pdf, p. ~8
- **Agent workflow pseudocode:** lecture-07-summary.pdf, p. ~10
