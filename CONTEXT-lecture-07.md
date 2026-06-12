# Lecture 07 Digest: Spoken Session — Reverse Engineering, Debugging & Token-Efficient Agentic AI

**Course:** University of Haifa, 203.3763 — "Orchestration of AI Agents"  
**Lecture:** 07 (Delivered on campus, recorded + partial whisper.cpp transcript)  
**Instructor:** Dr. Yoram Segal  
**Date:** June 2026  

---

## REVISIONS / ADDITIONS vs the Written Spec & PDF Digest

### Critical Binding Statements (Verbatim Hebrew + English Translation)

**On HW4 deadlines and submission model:**
- Dr. Segal emphasized: **Two-week submission window, but start immediately.** "היום אני נותן לכם תרגיל ארבע" (Today I give you assignment 4). "אל תחכו עד היום האחרון" (Don't wait until the last day). Late submission: −5 points per 24h, no special request needed (already stated in spec, but he re-emphasized orally).
- Key phrase (verbatim Hebrew): "קחו את התרגיל, תסיימו, וזה בכלל יותר מפשט" = "Take the assignment, finish it, and it's actually simpler/faster."
- **Implication:** Start today/this week, not in two weeks. Exam period overlap will cause extra stress.

**On what he WILL and WON'T check:**
- Hebrew (paraphrased): "אני רוצה לראות את המקרה לפני ואחרי" = "I want to see the before and after case."
- "תראו לי את התמונה לפני, איך הייתה הארכיטקטורה... ותראו לי אחרי" = "Show me a picture before: how the architecture was... and show me after: what you improved."
- **Clear mandate:** He will examine before/after code AND before/after Obsidian/graph representation (knowledge level, not just code level).
- **He WILL NOT accept:** "I found a bug and fixed it" without architectural insights. He wants "show me what you learned about the codebase structure."

**On the token-savings proof (core requirement):**
- "אני רוצה שתשכנעו אותי שאתם חוסכים טוקנים" = "I want you to convince me you're saving tokens."
- Baseline vs. graph-guided comparison is **mandatory for grading.** He said: "תראו לי את הטוקנים לפני... כמה טוקנים זה לקח לכם... ותראו לי אחרי כמה טוקנים זה עולה לכם" = "Show me the tokens before — how many tokens did it take — and show me after — how many tokens it costs now."
- **If you don't see savings:** "אם מישהו לא הצליח לחסוך... שיסביר למה" = "If someone didn't manage to save, explain why." Honest explanation acceptable; zero measurement = problem.

**On creativity and extensions (differentiator):**
- "מה אתם מביאים לעצמכם" = "What do you bring to the table?" Extensions are **critical for standing out.** He said the spec gives the baseline; what YOU add determines your grade relative to peers.
- Example extensions he hinted at: "איזה שימושים אחרים, איזה הרחבות" (other uses, extensions) — e.g., ranking suspect nodes by centrality, dynamic `hot.md` generation, impact analysis ("what breaks if I change this?").

**On CrewAI vs. LangGraph (guidance, not hard rule):**
- Lecture PDFs hint LangGraph; speaker restated: CrewAI for sequential hierarchical tasks (Manager → Researchers), **LangGraph for graph-driven, state-persisting, conditional branching** (which HW4 reverse-engineering is). No punishment for picking either, but LangGraph "feels right" for this task.

**On the buggy repositories (flexibility with caveats):**
- Three provided repos (BugsInPy, broken-python, buggy-python) are acceptable.
- **You CAN bring your own repo IF:** ≥10,000 LoC and ≥70 code files (stated in spec, confirmed orally). "אני מוכן לקבל" = "I'm ready to accept." But he warned: if you use your own code that already has documentation, "זה לא עשינו בזה כלום" = "we didn't do anything with it." The whole point is to reverse-engineer UNFAMILIAR code. Don't pick a repo where you already know the structure.

---

## Graphify: Oral Clarifications

### Graph Schema & Edge Confidence

**From lecture (addition to PDFs):**
- Edges have three confidence levels: **EXTRACTED** (AST-derived, 100% certain), **INFERRED** (LLM-hypothesized, 50–95% confidence range), **AMBIGUOUS** (unclear, requires manual validation).
- **When reporting:** "שימו לב שמידע שנמצא באמצע הוא מידע חלש" = "note that information in the middle [of context window] is weak."
- Implied guidance: **Only trust EXTRACTED edges initially.** Use INFERRED only if needed; flag AMBIGUOUS for manual review.
- Confidence scores appear in edge labels; graph.json MUST include `confidence` field per edge (not just node).

### God Nodes & Bottlenecks (Architectural Red Flags)

**Oral emphasis (beyond PDFs):**
- Defined as: "צוואר בקבוק" (bottleneck) — a node through which ALL data flows, high degree + high betweenness centrality.
- Detection method: "אתם רואים העיגול הזה יותר גדול מהעיגול הזה? למה?" = "You see this circle is bigger than that circle? Why?" Because of **more connections (degree)**, not physical size.
- **Risk:** If the God Node fails, entire subsystem fails. Also high mutation target (more changes = more bugs).
- **Your task:** Identify God Nodes in GRAPH_REPORT.md; flag as `[CRITICAL]` or `[WARNING]` depending on degree/betweenness threshold. Suggested: degree > 50 or betweenness in 90th percentile.
- Example he gave (paraphrased): "AuthController class that all services call → God Node."

### Graphify Execution & Depth Trade-offs

**Key insight (oral):**
- Graphify can work in **shallow mode** (AST only, zero LLM calls) or **deep mode** (AST + LLM inference).
- Shallow is free (token-wise); deep costs tokens but finds semantic relationships.
- When you run `graphify extract <folder>`, it asks: "מה העומק שאתם רוצים להיכנס בחקירה" = "What depth do you want to dive into?" You decide.
- For HW4: He expects you to **show both approaches** (or at least justify your choice). "זה בחינם" vs. "זה יעלה לכם קצת טוקנים" (this is free vs. this costs you tokens).
- **Output files:** `graph.json` (primary), `GRAPH_REPORT.md` (narrative), `graph.html` (visual). All required; HTML viewable in browser.

---

## Obsidian Vault: Oral Clarifications

### index.md vs. hot.md Role (Reinforced)

**From lecture:**
- **index.md** = "Hub, one click away from any major concept" (wikilinks guide entry).
  - Lists all Projects and Domains in the vault.
  - Hierarchical: Portfolio → Domains → Projects → Components.
  - Used by agents as **first navigation step** (always read index.md first, then branch to specific wiki pages).

- **hot.md** = "Hot Topics, frequently accessed or critical concepts."
  - Dynamically updated DURING agent queries.
  - Acts as a "refresh" mechanism (prevents context rot mid-session).
  - Should synthesize currently-active debugging concepts.
  - Agents re-read hot.md after each iteration to focus next steps.

**Oral re-emphasis:**
- "קרא תחילה את ה-index.md, אחר כך עבור לעמודים ב-wiki ככל הנדרש" (transliterated) = "Read index.md first, then navigate to wiki pages as needed."
- He wants Obsidian to **behave like Wikipedia:** clickable links, back-links, transclusion. Not a file dump; a **navigable knowledge base.**

### Vault Structure Reminder

- Obsidian vault in `vault/` folder at repo root.
- Minimum pages: `index.md`, `hot.md`, `log.md` (decision log).
- Additional pages: one per domain (if applicable), one per major component under investigation.
- **Do NOT hand-build.** Use templates (Frontmatter: type, status, project) to stay consistent.

---

## "Lost in the Middle" & Context Windows (Lecture Amplification)

### The Core Problem (Reinforced Orally)

**Verbatim Hebrew emphasis:** "המידע שנמצא באמצע הוא מידע חלש. המערכת שוכחת אותו, היא לא יודעת אותו." = "Information in the middle is weak information. The system forgets it; it doesn't know it."

**Why it happens:**
- LLM attention weights decline steeply in the middle of long contexts.
- Contradictory information in middle confuses inference (LLM resolves conflicts by favoring beginning/end).
- Irrelevant context in middle = noise → lower signal-to-noise ratio.

**HW4 application:**
- Naive approach: dump entire codebase → tokens wasted on irrelevant code → bug-finding performance degrades.
- Graph-guided approach: index.md → wikilinks → hot.md → subgraph query → focused code snippets → tokens focused on relevant paths.
- **Result:** 60–70% token reduction claimed in PDFs; prove it in your submission.

### Position-Aware Context Design (Reinforced Orally)

**Strategy he emphasized (verbatim paraphrased):**
- "תמיד מה שבמרכז הוא חלש ויש איתו בעייתיות" = "Whatever is in the middle is weak and problematic."
- **Solution:** Explicit position encoding:
  - **Beginning (strong):** Query + index.md (meta-navigation).
  - **Middle (active):** Only relevant wiki pages + subgraph nodes (the actual evidence).
  - **End (strong):** Summary + recommendation (executive summary).
- This is why hot.md is important: it refreshes the middle context mid-query.

---

## Agent Design (CrewAI vs. LangGraph) — Oral Clarifications

### Preferred Architecture (Guidance, Not Mandate)

**LangGraph recommendation reinforced:**
- State-based traversal (query → graph navigation → code reading → hypothesis → validation).
- Conditional branching (if AMBIGUOUS confidence, branch to manual check; else follow EXTRACTED edges).
- Iterative (state persists; agent knows what it's already explored).
- **Easier to control token budget** via state snapshots and selective re-prompting.

**If you choose CrewAI:**
- Sequential tasks (Manager orchestrates Researchers).
- Each researcher is specialized: one for graph analysis, one for code reading, one for hypothesis testing.
- Coordinator synthesizes findings.
- More dialogue rounds = higher token cost; acceptable if you show **explicit token tracking** per agent per round.

### Graph-Guided Agent Workflow (Pseudocode, Oral Expansion)

**He emphasized the iteration loop:**
1. Load graph.json + index.md + hot.md.
2. Parse query (bug symptom).
3. Route to hot.md (find relevant section).
4. Follow EXTRACTED edges from hot.md nodes → build subgraph.
5. For each subgraph node: read code snippet, match to symptoms.
6. If no match: backtrack, try INFERRED edges.
7. If match: inspect callers/callees (contextual neighbors).
8. **Hypothesis test:** Run unit tests on suspected code.
9. **Validate:** Confirm root cause, generate explanation.
10. **Update hot.md:** Add new findings for next iteration.
11. **Exit condition:** Root cause confirmed OR no more productive paths.

**Key oral point:** "צריך להריץ את היוניטסטים כדי לבדוק שלא שברתם את הקוד" = "Run unit tests to check you didn't break the code." This is a gate — every agent action must be validated.

### Context-Reduction Mechanisms (Practical Guidance)

**From oral:**
- **Subgraph fetching:** Only K-hop neighbors from bug symptoms (suggested K=2–3 to start).
- **Confidence filtering:** EXTRACTED-only initially; escalate to INFERRED if no progress.
- **/compact + /refresh SKILLs:** If session grows large, use Claude's SKILL mechanism to summarize beginning + end, discard middle. He mentioned this briefly but said it's **optional** for HW4.
- **Index-first retrieval:** Always query index.md first; let it guide which wiki pages to load next.

---

## Reverse Engineering: Block & Class Diagrams (Oral Guidance)

### Extraction Workflow (Concrete Steps He Outlined)

**Step 1: File-level structure (AST)**
- Run Graphify on codebase → parse all Python files.
- Extract imports, module definitions, class definitions.
- Build a Directed Acyclic Graph (DAG) of dependencies.

**Step 2: Semantic labeling**
- For each class/module: "מה הקוד הזה עושה? מי כותב אותו?" = "What does this code do? Who writes it?"
- Use Claude to label by responsibility (API, Service, Repository, DAO, Data Model).
- Assign to tiers: Presentation → Business Logic → Data Access.

**Step 3: Diagram generation**
- **Block diagram** (high-level tiers): manually draw or generate from Graphify output.
- **OOP diagram** (class-level): extract classes, inheritance, key methods. Graphify.html can show this; you may need to simplify for clarity.
- **Data-flow diagram** (optional): trace how data flows from UI → Service → DB.

### Expected Artifacts (He was Specific)

**He said:** "אתם צריכים להוציא את ה-object-oriented, ה-OOP של הקלאסים" = "You need to extract the object-oriented, the OOP of the classes."

Two diagrams **must** be in your submission:
1. **Architectural block diagram:** folders/tiers/layers, high-level components, data flow.
2. **OOP/class diagram:** classes, inheritance, key methods, relationships.

These are graded as part of **reverse engineering** evidence (Requirement 5.2).

---

## "God Nodes" & Centrality Metrics (Oral Reinforcement)

### What to Report in GRAPH_REPORT.md

**He said explicitly:**
- List all nodes with degree ≥ 50 OR betweenness centrality ≥ 90th percentile.
- Mark as `[CRITICAL]` (degree > 100 or betweenness > 0.90) or `[WARNING]` (degree 50–100 or betweenness 0.70–0.90).
- For each God Node: explain **why** it's a bottleneck + **risk** (single point of failure, mutation target) + **fix option** (refactor into sub-modules).
- Example from his lecture: "AuthController.py (degree: 67, betweenness: 0.85) [CRITICAL] — All auth requests flow through this. If it fails, system is down."

---

## Q&A Highlights (Student Binding Questions & Answers)

### On HW4 Repo Choice & Significant Enough Size

**Q:** "Can I use my own repo instead of BugsInPy?"  
**A:** "Yes, if it's ≥10,000 LoC and ≥70 code files. But if it's YOUR code with YOUR documentation, זה לא עשינו בזה כלום (we didn't learn anything). Pick UNFAMILIAR code."

### On Token Savings — What Counts?

**Q:** "What if I don't see token reduction?"  
**A:** "Explain why. Honest analysis is acceptable. But measure it — zero measurement = failure."

### On Submission & Timing

**Q:** "Can I submit early / ahead of the two-week window?"  
**A:** "I grade everyone at the deadline. Don't wait; start immediately. But I won't grade early submissions individually."

### On Extension Work & Differentiators

**Q (implied):** "What makes my submission stand out?"  
**A:** "אמור להיות עכשיו איזשהו שלב שבו אתם מסתכלים על ההמלצות" = "There should be a step where you look at [graph-generated] recommendations and think about how to improve further." Add something creative: ranking by centrality, dynamic hot.md, impact analysis, organizational graph (if you extend the idea to teams).

---

## Logistics, Grading & Self-Grade Remarks

### Submission & Grading Model

- **Deadline:** Friday, 19 June 2026, 23:59 (Asia/Jerusalem).
- **Submission:** GitHub repo (public or shared with rmisegal@gmail.com; inaccessible = auto-zero). + Moodle submission PDF (auto-generated by `scripts/fill_submission_pdf.py`).
- **Late penalty:** −5 points per 24h (no special request needed).
- **Grading timing:** All submissions graded together at deadline (not early).

### Self-Grade Guidance

- Default honest self-grade: **85/100** (spec §5: invites "rigorous lens" if inflated, penalizes if too low).
- Over-claiming (90+) triggers detailed audit; under-claiming (70–80) biases grader downward.
- Focus on **quality of before/after + token measurement + original extension + clear README** to justify 85+.

### HW3 Patterns That Worked (Reusable)

- SDK layer (single public entry) ✓
- Gatekeeper for every LLM call (must be wired, not decorative) ✓
- Per-mechanism PRDs + ADRs ✓
- Class diagram ✓
- 800+ task TODO ✓
- Pre-commit hooks + GitHub Actions CI (pinned Python 3.13, MUST be GREEN) ✓
- Honest self-grade = 85 ✓

---

## Pet Peeves & Watch-Outs

- **Don't dump entire codebase into LLM naively.** Graph-guided navigation is the WHOLE POINT.
- **Don't skip Obsidian setup.** It's not optional; it's the navigation layer that enables token savings.
- **Don't trust AMBIGUOUS edges without manual validation.** Graph is probabilistic; be skeptical.
- **Don't measure tokens only at the end.** Track them throughout (baseline vs. graph-guided, per agent iteration).
- **Don't pick a familiar codebase.** The exercise is reverse-engineering unfamiliar code; if you know it, you lose the learning.
- **Don't start two weeks in.** Begin this week; you'll have breathing room before exam period collision.
- **Don't forget before/after at BOTH code and knowledge levels.** Show architectural improvement, not just bug fixes.
- **Don't over-complicate the agent.** One agent with multiple specialized skills is better than many chained agents (higher token cost, harder to debug).
- **Don't skip the research questions (spec §4).** Answer them explicitly in README + reports: What architecture emerged? Where are God Nodes? How did graph save tokens? Etc.
- **Don't submit without unit tests GREEN.** CI must pass; red suite = automatic penalty.
- **Don't hide your creative work.** The extensions and original insights are what distinguish submissions. Make them explicit.

---

## Most Important Findings for HW4 Planning

### 1. **Token Savings Proof is Non-Negotiable**
Dr. Segal will **reject or heavily penalize** submissions without before/after token metrics. He wants to see:
- Baseline: naive agent reads N files, consumes T tokens, finds bug in M iterations.
- Graph-guided: agent reads N' files (N' << N), consumes T' tokens (T' << T), finds bug in M' iterations (M' ≤ M).
- **If no savings:** Explain why (e.g., small codebase, all code relevant). Honest explanation > zero measurement.

### 2. **Before/After at Knowledge Level is Equally Important**
Don't just show code before/after. Show:
- Obsidian vault structure **before** (e.g., auto-generated index.md).
- Obsidian vault structure **after** (enriched with hot.md, linked insights, decision log).
- Graph **before** (raw Graphify output).
- Graph **after** (annotated with bug-finding path, God Nodes flagged, architecture understanding).
- This is the "leverage" of the graph-knowledge-graph approach.

### 3. **Architectural Understanding > Bug Fix**
He said: "מה הבנתם מהגרף? מה הבנתם, איך תכננו את הקוד הזה?" = "What did you understand from the graph? How was this code designed?"
- A trivial bug fix (off-by-one) with deep architectural insights = **high grade.**
- A major architectural bug fix with no insights = **low grade.**
- Show you **learned the system**, not just patched a line.

### 4. **Extensions & Creativity Are the Differentiator**
- Baseline: follow the spec, deliver the graph + agent + token proof.
- Excellent: add something original (e.g., God Node refactoring proposal, dynamic hot.md generator, impact analysis, organizational graph).
- He said: "מה אתם מביאים לעצמכם" = What you bring to the table is what sets you apart.

### 5. **Start This Week, Not in Two Weeks**
- Exam period overlap is real; two-week window is a courtesy, not permission to procrastinate.
- His recommendation: "קחו את התרגיל, תסיימו" (take the assignment, finish it) by next week.
- You'll have time to iterate, test, and document without deadline stress.

---

## Summary (6-line Brief for HW4 Worker)

1. **Graphify is mandatory; run it first.** Outputs graph.json + GRAPH_REPORT.md (annotate with God Nodes, confidence scores, evidence types).
2. **Obsidian vault (index.md, hot.md, linked pages) is a navigation layer**, not a file dump. Agents must consult it before reading code; this is where token savings come from.
3. **Token-savings proof is non-negotiable.** Measure baseline (naive agent) vs. graph-guided (with Graphify + Obsidian): files read, tokens consumed, iterations, accuracy. If no savings, explain why.
4. **Two diagrams required:** architectural block diagram (tiers/modules) + OOP/class diagram. Show reverse-engineering skill.
5. **Before/after at BOTH code and knowledge levels.** Don't just fix a bug; show how Obsidian + graph deepened your understanding of the system.
6. **Start this week.** Two-week window is real; exam period will squeeze you later. Extensions + creativity are what differentiate submissions.

---

## Cross-Reference with PDFs

- **Part A (Active Knowledge):** Lecture confirms "Lost in the Middle" as core motivation; adds emphasis on middle-context decay in LLM attention.
- **Part B (Graph Architecture):** Lecture reinforces EXTRACTED/INFERRED/AMBIGUOUS confidence scale; adds God Node detection urgency.
- **Part C (Graphify):** Lecture confirms pipeline; adds note that shallow (AST-only) is free, deep (LLM) costs tokens; you choose depth.
- **Part D (Summary):** Lecture emphasizes integration; adds concrete examples of how index.md + hot.md + graph guide agent queries.

**No contradictions found.** Lecture amplifies and clarifies the written spec; all deliverables align.

