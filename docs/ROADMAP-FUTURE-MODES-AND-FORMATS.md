# Roadmap: Reasoning Modes and Output Formats — Future Work

This document lists reasoning mode and output format candidates that are NOT yet part of the plugin, with tier assignments and rationale. Each entry is a forward-looking proposal. The canonical sets below describe what is currently shipped.

## Methodology

Candidates were identified by scanning the plugin's reference documentation and the deprecated `deepthinking-mcp` source corpus for mentions of reasoning methods and output formats not present in the canonical sets. Each candidate was evaluated for distinctness from existing canonical modes, academic or professional standing, fit with the plugin's prose-only reasoning model (no runtime computation), and effort relative to the 10-place mode invariant documented in `CLAUDE.md`.

Each entry includes a tier (Strong / Plausible / Rejected), an effort estimate (Trivial / Small / Medium / Large), and a redundancy risk assessment. Tier 1 candidates merit serious consideration for the next release; Tier 2 candidates are worth a brainstorm pass; Tier 3 candidates are documented for completeness and should not be revisited without new evidence.

## Current canonical sets

### 34 reasoning modes (v0.4.1)

**Logical & Formal:**
- abductive — inference to best explanation
- deductive — logical derivation from premises
- inductive — pattern generalization from examples
- formallogic — symbolic logic and proof construction

**Mathematical & Computational:**
- algorithmic — step-by-step problem solving
- computability — decidability and complexity analysis
- mathematics — mathematical proof and calculation
- recursive — self-referential problem decomposition

**Probabilistic & Uncertain:**
- bayesian — belief updating with evidence
- evidential — Dempster-Shafer belief functions
- stochastic — random process modeling

**Causal & Temporal:**
- causal — cause-effect relationship analysis
- counterfactual — what-if scenario reasoning
- temporal — time-based relationship reasoning
- historical — past event analysis and precedent

**Systems & Strategic:**
- systemsthinking — holistic system behavior analysis
- gametheory — strategic interaction modeling
- optimization — constraint satisfaction and improvement
- constraint — constraint satisfaction problems

**Analytical & Critical:**
- analysis — systematic decomposition
- critique — weakness identification and evaluation
- argumentation — structured argument construction
- synthesis — integration of multiple sources

**Scientific & Engineering:**
- scientificmethod — hypothesis testing methodology
- engineering — design trade-offs and failure analysis
- physics — physical law application
- firstprinciples — fundamental assumption reasoning

**Information & Communication:**
- shannon — information theory and encoding
- cryptanalytic — code breaking and security analysis

**Cognitive & Meta:**
- analogical — similarity-based reasoning
- metareasoning — reasoning about reasoning
- modal — possibility and necessity logic
- hybrid — multi-method combination
- sequential — ordered step reasoning

### 9 mode-agnostic format grammars (v0.4.1)

These live at `reference/visual-grammar/formats/<format>.md` and define surface syntax shared across all 34 modes:

- ascii — plain text diagrams and tables
- dashboard — interactive HTML with embedded visualizations
- graphml — XML graph interchange format
- html — structured web document format
- json — structured data interchange
- markdown — lightweight markup with embedded diagrams
- modelica — differential equation modeling language
- tikz — LaTeX vector graphics (TikZ package)
- uml — unified modeling language diagrams

### 2 per-mode visual grammars (v0.4.1) — also first-class

These live at `reference/visual-grammar/<mode>.md` (one file per mode) because each mode needs its own Mermaid + DOT template tailored to its semantic structure. They are equally first-class — `render-diagram.py` wraps `mmdc` and `dot` to render SVG/PNG from these:

- mermaid — diagram-as-code for flowcharts, sequence diagrams, state machines (rendered via `mmdc`)
- dot — Graphviz directed/undirected graphs (rendered via `dot`)

**Total effective format coverage: 11** (the README's "All 11 export formats" table reflects this). Plus `svg` and `png` as derived rendering targets from mermaid+dot. Future format candidates below should be evaluated against this 11-format baseline, not the 9-file `formats/` directory.

## Roadmap: Reasoning Modes

### Tier 1 — Strong candidates (merit serious consideration)

**(intentionally empty)**

The plugin's 34 canonical modes are essentially feature-complete for prose-based structured reasoning. For a new mode to earn Tier 1, it must meet all four of the following bars:

1. A concrete JSON Schema sketch with field types and required/optional designations (not just a bag of nouns)
2. A worked example that does NOT reduce to existing modes when you remove the new mode's name
3. At least one external user request, or a documented gap in `test/smoke/captured/` outputs where a real Claude response failed to fit any existing schema
4. An explicit acknowledgment of the 10-place mode invariant cost (every new mode is at least Medium effort because of the synchronized-artifacts requirement in `CLAUDE.md`)

If a candidate cannot meet all four bars, it belongs in Tier 2 (watching) or Tier 3 (rejected with rationale).

### Tier 2 — Watch list (re-evaluate when concrete demand or design surfaces)

**decisionanalysis** — Decision Analysis
- **What it is** — A formal methodology for individual decision-making under uncertainty using decision trees, utility functions, expected-value calculations, sensitivity analysis, and value-of-information analysis. Foundational frameworks include Howard's decision analysis cycle and Raiffa's decision trees.
- **Why it might earn inclusion** — Plausibly fills a gap not covered by `gametheory` (multi-agent strategic interaction), `bayesian` (belief updating only), or `optimization` (constraint satisfaction with fixed objective). Decision analysis combines probabilistic belief, multi-attribute utility, and explicit alternative enumeration into a single structured artifact — none of the three canonical modes does this end-to-end.
- **Risk to address before promotion** — The schema sketch (`alternatives, criteria, probabilities, utilities, expected_values, sensitivity_analysis, value_of_information`) can be read as a union of fields from those three other modes. The promotion gate is a design spike: take a real decision (e.g., "should we migrate to PostgreSQL?") and produce both (a) three separate `bayesian`/`gametheory`/`optimization` thoughts and (b) one decisionanalysis thought, then judge whether the integrated artifact is materially better.
- **Closest existing modes** — `bayesian` (probabilities), `optimization` (alternatives + criteria), `gametheory` (utilities, but only multi-agent)
- **Schema sketch** — `decisionContext` (objective, decisionMaker, timeHorizon), `alternatives[]` (id, description), `uncertainNodes[]` (variable, distribution, parents), `utilityFunction` (attributes, weights, normalization), `decisionTree` (nodes, branches, terminal payoffs), `expectedValues[]` (per alternative), `sensitivityAnalysis` (which inputs swing the decision), `valueOfInformation` (per uncertain node)
- **Effort** — Medium-Large (10-place invariant + non-trivial math instruction in the SKILL.md prose; would require teaching Claude to compute expected values reliably)
- **Risk of redundancy** — Medium
- **Priority** — Hold for v0.6.0 or later; do not commit until a design spike demonstrates non-redundant utility

### Tier 3 — Considered and rejected

**dialectical** — Dialectical Reasoning
- **Why rejected** — Thesis-antithesis-synthesis structure is already covered by combining canonical `synthesis` (multi-source integration with convergence/divergence tracking) + `argumentation` (Toulmin claim/warrant/rebuttal) + `critique` (peer-review evaluation). "Dialectical reasoning" is also not a single well-defined method — it's a family of approaches (Hegelian, Platonic, Marxist) without a unifying schema, and the tentative schema sketch (`thesis, antithesis, synthesis, tension_points, resolution_mechanism, synthesis_quality`) has a subjective `synthesis_quality` field that makes the validation rule unverifiable.

**structuralcausalmodel** — Structural Causal Models / Pearl do-calculus
- **Why rejected** — Adding it would create a three-mode causal cluster (`causal` + `counterfactual` + `structuralcausalmodel`) with significant overlap. Pearl's "ladder of causation" has three levels (association, intervention, counterfactual) — the canonical `causal` + `counterfactual` modes already cover all three between them, and the `causal` SKILL.md already teaches `do-operator` reasoning. If Pearl's lineage needs to be explicit, the right fix is a one-paragraph attribution in the causal SKILL.md, not a new mode. If do-calculus formalism is genuinely needed at some point, extend the existing `causal` schema with optional `structuralEquations` and `interventions` fields rather than fork a new mode.

**dynamicalsystems**, **controltheory**, **networkanalysis**, **probabilistic** — Computational methods
- **Why rejected (unified rationale)** — All four require computation that the plugin cannot perform. Dynamical systems analysis needs eigenvalues and numerical integration. Control theory needs PID tuning and Bode-plot stability margins. Network analysis needs centrality calculations and community-detection algorithms. General probabilistic reasoning needs frequentist hypothesis tests, p-values, and maximum-likelihood fits. **The plugin teaches reasoning patterns expressed in JSON; it does not run computation.** This is the dividing line between the plugin and the deprecated `deepthinking-mcp` — the MCP had TypeScript handlers that auto-computed Bayes posteriors, Nash equilibria, and Allen interval relations; the plugin teaches Claude to produce these in prose. Methods whose value lies in *computation* rather than *structured reasoning about what to compute* are out of scope per the "no Node runtime" principle in `CLAUDE.md`.
- **Note** — `networkanalysis` may be revisited in the future if `graphml` consumers (Gephi, NetworkX users) start requesting structured-graph reasoning artifacts. The other three are unlikely to be reconsidered.

**reliabilityengineering** — Reliability Engineering
- **Why rejected** — Already covered by the canonical `engineering` mode, which explicitly includes failure analysis. This is the same rejection rationale applied to `fmea` below. FMEA, FTA (fault-tree analysis), and probabilistic risk assessment are standard *techniques within* engineering reasoning, not standalone reasoning paradigms.

**toulmin** — Toulmin Argumentation Model
- **Why rejected** — IS the canonical `argumentation` mode. `skills/think-academic/SKILL.md` explicitly defines argumentation as "Argumentation (Toulmin model with claim/warrant/backing/qualifier/rebuttal)" and the worked example uses Toulmin structure verbatim. Any future mention of "Toulmin" in documentation is confirming the existing implementation, not requesting a new one.

**socratic** — Socratic Questioning
- **Why rejected** — IS already part of the canonical `critique` mode. The think-academic skill description defines critique as "Critique (peer-review style evaluation, strengths/weaknesses, **Socratic questions**)". If Socratic questioning needs more prominence, the right move is to expand the critique skill's worked example, not to create a new mode.

**dempstershafer** — Dempster-Shafer Theory
- **Why rejected** — Already implemented as the theoretical foundation of the canonical `evidential` mode. Dempster-Shafer belief/plausibility functions are the core mathematical framework underlying evidential reasoning, not a separate mode.

**allentemporal** — Allen Interval Relations
- **Why rejected** — Already covered by the canonical `temporal` mode. Allen's interval algebra (before, after, during, overlaps, meets, etc.) is a specific formalism within temporal analysis, not a distinct reasoning approach.

**fmea** — Failure Mode and Effects Analysis
- **Why rejected** — Already covered by the canonical `engineering` mode, which explicitly includes FMEA as a signal and technique for systematic failure identification and analysis.

**bayesiannetworks** — Bayesian Networks (weakest rejection; re-evaluate if demand surfaces)
- **Why rejected** — Represents a specific implementation technique for the canonical `bayesian` mode rather than a distinct reasoning approach.
- **Caveat** — This rejection is the weakest in the list. Bayesian networks are arguably a *structural* reasoning approach (graphical model construction, d-separation, conditional independence) distinct from the canonical `bayesian` mode's single-hypothesis-with-evidence belief updating. They share the underlying probability calculus but the structured-reasoning artifact differs. Before promoting, someone should produce a concrete schema sketch and a worked example where the Bayesian-network artifact adds value beyond what the current `bayesian` schema can express. If promoted, the architecturally correct path is likely extending the existing `bayesian` schema with optional `network` fields (nodes, edges, conditionalProbabilityTables, dSeparation queries) rather than creating a new mode — same pattern as the `causal` extension proposed for SCMs above.
- **Status** — Re-evaluate in v0.6.0 if a real Bayesian-network use case appears in `test/smoke/captured/` outputs.

**epistemiclogic** — Epistemic Logic
- **Why rejected** — Too narrow and academic for the plugin's software engineering focus. While epistemic logic (reasoning about knowledge states) is a valid modal logic system, it lacks clear practical applications beyond the general `modal` mode's coverage of possibility and necessity.
- **Source citations** — mcp/docs/superpowers/knowledge-packs/modal.md

**deonticlogic** — Deontic Logic
- **Why rejected** — Too narrow and academic. Deontic logic (reasoning about obligations and permissions) is a specialized modal logic with limited practical applications outside legal and ethical domains, already covered by the general `modal` mode.
- **Source citations** — mcp/docs/superpowers/knowledge-packs/modal.md

**modusponens** — Modus Ponens
- **Why rejected** — Too narrow; represents a specific inference rule within the canonical `formallogic` mode rather than a complete reasoning method. Classical logical forms like modus ponens and modus tollens are components of formal logical reasoning, not standalone modes.
- **Source citations** — mcp/docs/superpowers/plans/2026-04-12-deepthinking-plugin-phase-1-2-scaffold-and-prototype.md

**syllogism** — Syllogistic Reasoning
- **Why rejected** — Too narrow; represents a specific argument form within the canonical `formallogic` mode. Syllogisms are classical three-part deductive arguments but don't constitute a complete reasoning methodology beyond formal logic.
- **Source citations** — mcp/docs/superpowers/plans/2026-04-12-deepthinking-plugin-phase-1-2-scaffold-and-prototype.md

## Roadmap: Output Formats

### Tier 1 — Strong candidates (merit serious consideration)

**latex-math** — LaTeX Math Notation (distinct from canonical TikZ)
- **What it is** — General LaTeX mathematical typesetting (equations, proofs, derivations, matrices) using the AMS-math packages — distinct from the canonical `tikz` format which is for vector diagrams using the TikZ package. The two are complementary: one renders math, the other renders graphs.
- **Consumers** — Academic papers, Overleaf, MathJax/KaTeX in web pages, local pdflatex installations. Also useful as embedded blocks inside markdown or HTML output.
- **Why it earns inclusion** — Mathematics, physics, formallogic, firstprinciples, and bayesian modes all naturally produce equations as part of their structured output. A dedicated `latex-math` format grammar would standardize how math expressions are extracted from a thought and rendered as a clean math-only artifact (e.g., a `.tex` file that could be `\input`'d into a paper). The motivation is **rendering convenience**, not JSON-escape repair — the `repair_lone_backslashes` workaround in `test/smoke/run-all-modes.py` is a separate SKILL.md prose issue (math skills should explicitly instruct "escape all backslashes in JSON strings as `\\\\`") that this format does not address.
- **Surface syntax sketch** — `\begin{align*} P(H|E) &= \frac{P(E|H) \cdot P(H)}{P(E)} \\ &= \frac{0.9 \cdot 0.3}{0.41} \approx 0.659 \end{align*}`. The `align*` environment requires `amsmath`, which the grammar file must document as a preamble dependency.
- **Renderer dependency** — None for source output. For visual rendering the user needs either `pdflatex` (with `amsmath` and `amssymb` packages) or a KaTeX/MathJax renderer in a browser. No new hard plugin dependency.
- **Effort** — Small-Medium. The grammar file itself is small (~1 file). The work is in defining per-mode math-extraction rules: which JSON fields in each of the 7 math-heavy mode schemas (mathematics, physics, computability, formallogic, firstprinciples, bayesian, evidential) should be extracted as math expressions vs prose. Estimated 2-4 hours of design work plus 1-2 hours of grammar authoring.
- **Priority** — Medium-High (rendering convenience for math-heavy modes is a real user benefit)

**csv** — Comma-Separated Values
- **What it is** — Universal tabular data format (RFC 4180) for structured numerical and categorical output. Useful when a thought contains tabular subsections (decision matrices, payoff tables, evidence weights, alternative comparisons) that need to be exported for downstream analysis tools.
- **Consumers** — Excel, R, Python pandas, database import tools, statistical software, jq pipelines, awk scripts
- **Why it earns inclusion** — Many canonical modes produce tabular data: `gametheory.payoffMatrix.entries`, `bayesian.evidence` rows, `optimization.alternatives`, `engineering.tradeStudy.alternatives`, `evidential.belief` distributions. A CSV format grammar would let users pipe these directly into spreadsheet/dataframe tools without writing extraction code. An empirical heuristic check found **27 of 34 modes** have at least one array-of-objects field with ≥3 properties — most modes are tabular-friendly.
- **Surface syntax sketch** — For a `bayesian` thought with 3 evidence items: `evidence_id,description,prior,likelihood_h,likelihood_not_h,posterior` header followed by one row per evidence item. For a `gametheory` thought, the payoff matrix flattened as `player1_strategy,player2_strategy,player1_payoff,player2_payoff`.
- **Renderer dependency** — None (text output, no external binary)
- **Effort** — Small. The surface syntax itself is trivial; the real work is a spec-design pass defining per-mode flattening rules (which JSON fields become CSV rows, which become columns, how nested structures are flattened). The design pass should prioritize modes whose tabular content is the *primary* artifact (e.g., `gametheory` payoff matrices, `bayesian` evidence rows) over modes where array fields are incidental.
- **Priority** — Medium

### Tier 2 — Plausible candidates (worth a brainstorm pass)

**pdf** — Portable Document Format
- **What it is** — Fixed-layout document format for archival and distribution of formatted content.
- **Consumers** — Document archival, academic submissions, professional reports, print distribution
- **Why it earns inclusion** — Enables archival-quality output for formal documentation and distribution beyond web formats.
- **Source citations** — plugin/reference/visual-grammar/formats/html.md, plugin/reference/visual-grammar/formats/tikz.md, plugin/reference/visual-grammar/formats/markdown.md
- **Surface syntax sketch** — Binary format (would require HTML/LaTeX intermediate conversion)
- **Renderer dependency** — Pandoc or LaTeX toolchain for conversion
- **Effort** — Medium (requires conversion pipeline)
- **Priority** — Low

**gexf** — Graph Exchange XML Format
- **What it is** — XML-based graph serialization format with rich metadata support for dynamic and hierarchical networks.
- **Consumers** — Gephi, NetworkX, graph analysis tools, social network analysis software
- **Why it earns inclusion** — More feature-rich than GraphML for complex network analysis with temporal and hierarchical data.
- **Source citations** — plugin/reference/visual-grammar/formats/graphml.md
- **Surface syntax sketch** — `<node id="1" label="Node"><attvalue for="weight" value="0.8"/></node>`
- **Renderer dependency** — None (XML output, consumed by analysis tools)
- **Effort** — Small
- **Priority** — Low

**plantuml** — PlantUML Syntax
- **What it is** — Text-based UML diagram language with simpler syntax than full UML for common diagram types.
- **Consumers** — PlantUML processors, documentation systems, IDE plugins, Confluence/JIRA
- **Why it earns inclusion** — Simpler UML syntax than canonical UML format, widely supported in enterprise documentation.
- **Source citations** — plugin/reference/visual-grammar/formats/uml.md
- **Surface syntax sketch** — `@startuml\nAlice -> Bob: Hello\nBob -> Alice: Hi\n@enduml`
- **Renderer dependency** — plantuml.jar (Java-based renderer)
- **Effort** — Medium (requires Java dependency)
- **Priority** — Low

### Tier 3 — Considered and rejected

**mermaid** — Mermaid Diagram Syntax
- **Why rejected** — ALREADY canonical. Mermaid grammars live at `reference/visual-grammar/<mode>.md` (one per mode) because each mode needs its own template tailored to its semantic structure. They are not in the `formats/` directory because they are mode-specific, not mode-agnostic. The README's "All 11 export formats" table correctly lists mermaid as one of the 11. Future work should preserve the existing per-mode structure rather than collapse it.

**dot** — Graphviz DOT Language
- **Why rejected** — ALREADY canonical, same reason as mermaid. DOT templates live at `reference/visual-grammar/<mode>.md` alongside the Mermaid template for each mode. Renderable via `scripts/render-diagram.py` → `dot` binary. Not a roadmap item.

**svg**, **png** — raster/vector rendering targets
- **Why rejected** — Already supported as derived output from mermaid and DOT via `scripts/render-diagram.py --render-as svg|png`. These are rendering targets, not source formats for reasoning visualization.

**confluence** — Confluence Markup
- **Why rejected** — Too narrow and platform-specific. Confluence can consume markdown, making dedicated Confluence markup support unnecessary given existing markdown format support.

**docx** — Microsoft Word Format
- **Why rejected** — Binary format requiring complex conversion pipeline with limited benefit over PDF or HTML for reasoning visualization. Pandoc conversion from canonical `markdown` already provides this capability.

**beamer** — LaTeX Beamer Slides
- **Why rejected** — A specific LaTeX document class, not a distinct output format. Users needing presentation format can embed canonical `tikz` output in Beamer manually.

## Sequencing recommendation

**No new reasoning modes are recommended for v0.5.0.** The plugin's 34 modes are essentially feature-complete; new modes should require external user demand rather than internal speculation. Only the two Tier 1 output formats are scheduled for the next release.

### v0.5.0 — Format expansion only (no new modes)

- **`latex-math`** format grammar (Small-Medium effort). Provides clean math rendering for the 7 math-heavy modes (mathematics, physics, computability, formallogic, firstprinciples, bayesian, evidential).
- **`csv`** format grammar (Small effort). Provides tabular export for the 27 of 34 modes with wide array-of-objects fields, prioritizing modes whose tabular content is the primary artifact.

Total estimated effort for both format grammars: 1-2 days of focused engineering work including tests, sample fixtures, and `test/test_format_grammars.py` updates.

### v0.5.x patches — quality and tooling (not new functionality)

These are independent of the format work and have higher leverage than any new mode:

- **`test_version_consistency.py`** — cross-file version coherence check; prevents the latent-bug class where `plugin.json.version` can drift from README, CHANGELOG, and SKILL.md references (see CHANGELOG `[0.4.1]` entry for the underlying story).
- **`MODE_DISPLAY_NAMES` automated sync check** — extend `test/test_artifact_consistency.py` to verify the dict in `scripts/render-html-dashboard.py` matches the canonical mode set (the 10th sync location documented in `CLAUDE.md`).
- **Smoke test parallelization** — currently sequential at 30-60 min; with 4 parallel `claude -p` workers this drops to ~10-15 min. High priority for scaling beyond 34 modes.
- **`examples/personal-command-alias/think-render.md`** — ship the missing alias parallel to the existing `think.md`.

### v0.6.0 — Speculative; do not commit until evidence exists

All v0.6.0+ candidates are conditional on evidence that does not currently exist. The plugin has no telemetry or user-feedback channel to validate "user demand" claims. Before committing to any of the items below, add a feedback-collection mechanism (GitHub Discussions, an issue-template for "missing mode", or a usage-survey link in the README).

Conditional candidates:

- **`decisionanalysis`** mode — only if a design spike produces a worked example that adds value beyond what `bayesian` + `gametheory` + `optimization` can each separately produce
- **`bayesiannetworks`** mode (or `bayesian` schema extension) — only if real Claude output in `test/smoke/captured/` shows multi-variable conditional-independence reasoning failing to fit the existing `bayesian` schema
- **`gexf`**, **`plantuml`**, **`pdf`** format grammars — only if specific consumers (Gephi users, enterprise documentation users, archival workflows) request them

### Dependencies and parallelism

- `latex-math` and `csv` are independent and can be authored in parallel (different files, different fixture sets)
- The v0.5.x quality items are independent of the format work
- Both v0.5.0 format grammars must be added to `EXPECTED_FORMATS` in `test/test_format_grammars.py` and have `test/visual/test-dashboard.py` integration verified before release

### What this roadmap deliberately does NOT recommend

| Category | What | Why |
|---|---|---|
| Format promotion | Promoting Mermaid/DOT to `formats/` | They are already canonical, just in `<mode>.md` files (architectural choice, not a gap) |
| New modes (round 1) | `toulmin`, `socratic`, `fmea`, `allentemporal`, `dempstershafer` | All already inside canonical parent modes (`argumentation`, `critique`, `engineering`, `temporal`, `evidential`) |
| New modes (round 2) | `dialectical`, `structuralcausalmodel`, `decisionanalysis` (until proven distinct) | Schema sketches reduce to unions of existing modes; failed the same "is this distinct?" test that caught Toulmin/Socratic |
| Computational modes | `dynamicalsystems`, `controltheory`, `networkanalysis`, `probabilistic`, `reliabilityengineering` | Require auto-computation the plugin cannot perform; out of scope per "no Node runtime" principle in CLAUDE.md |
| Renderer-target formats | `svg`, `png`, `pdf` | Already supported as derived outputs from mermaid+dot via `render-diagram.py`; not source formats |
| Conversion-pipeline formats | `confluence`, `docx`, `beamer` | Either already covered by canonical `markdown`/`tikz`, or require complex conversion pipelines for marginal benefit |

### Strategic gaps on the maintainer's radar

These are scaling concerns that are NOT roadmap items themselves. They require the maintainer to think about the project's trajectory rather than ship specific code.

1. **Mode count is at or near the sustainable ceiling.** The maintenance cost of 34 modes (10-place invariant × 34 = 340 synchronized artifacts) is already high. Adding mode 35 should be much harder to justify than adding mode 5 was. The bar for "yes, build this" should rise as mode count grows.
2. **No mode deprecation path.** If telemetry eventually shows that some modes are rarely used, there is no documented process for sunsetting them. Worth designing before the question becomes urgent.
3. **Smoke test scalability.** Already 30-60 min for 34 modes; will not scale past ~50 modes without parallelization (in the v0.5.x quality items above) or selective re-runs (only modes whose schemas changed since the last release).
4. **Hybrid mode evolution.** As mode count grows, `hybrid.primaryMode` enum must expand. At some point hybrid may need to become the default entry point (auto-route to specialists from a hybrid root) rather than a sibling mode. Worth a design pass before mode 40.
5. **No telemetry / user feedback channel.** All "consider for v0.6.0+ if user demand" recommendations in this roadmap are speculative because the plugin has no way to measure which modes are actually used or what's missing. A GitHub Discussions board or a periodic README-linked usage survey would let future roadmap decisions be evidence-based instead of speculative.

## Out of scope (deliberate non-goals)

**Mode count beyond ~40:** The current 34-mode taxonomy already covers the major reasoning paradigms. Additional modes should fill clear gaps rather than subdivide existing categories. Reject modes that are primarily academic exercises without clear software engineering applications.

**Formats requiring runtime servers:** Avoid output formats that require persistent server processes or complex runtime environments. The plugin should remain self-contained with minimal external dependencies beyond common command-line tools.

**Domain-specific reasoning modes:** Reject highly specialized modes like medical diagnosis, legal reasoning, or financial modeling that serve narrow domains rather than general analytical thinking. The plugin targets software engineers and technical professionals, not domain specialists.

**Interactive visualization formats:** Avoid formats requiring complex client-side interaction beyond basic HTML dashboards. The plugin focuses on static analysis artifacts rather than interactive exploration tools.

**Proprietary format dependencies:** Reject formats tied to specific commercial tools or requiring proprietary software for rendering. Maintain compatibility with open-source toolchains and standard formats.