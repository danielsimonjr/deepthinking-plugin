# Visual Grammar: Inductive

How to render an `inductive` thought as a diagram.

## Node Structure

Inductive reasoning moves from specific observations to a general principle. The diagram uses a **top-to-bottom funnel layout**:

- **Observations** (top tier) → Rendered as **blue rectangles**, one per observation in the `observations` array
- **Pattern node** (middle tier) → A single **orange ellipse** labeled with the `pattern` excerpt (or "Pattern Recognition" if pattern is not yet explicit)
- **Generalization node** (bottom tier) → A **green pill/stadium shape** containing the `generalization` text
- **Counterexamples** (side tier) → **Red boxes with dashed edges** to the generalization, showing exceptions that constrain confidence

Border thickness on the generalization node encodes confidence: `confidence ≥ 0.8` → thick border; `confidence < 0.6` → thin dotted border.

## Edge Semantics

- **Solid arrow** (`→`) — Observation supports the pattern; weight reflects the strength of the observation
- **Dashed arrow** (`⇢`) — Counterexample contradicts the generalization; labeled "contradicts" or "exception"
- **Thick edge** — Strong supporting observation; used when observation relevance is high

## Mermaid Template

```mermaid
graph TD
    O1["🔵 Observation 1"]
    O2["🔵 Observation 2"]
    O3["🔵 Observation 3"]
    
    Pattern["⭐ Pattern Recognition<br/>Common thread"]
    
    Gen["✓ Generalization<br/>General principle"]
    
    O1 --> Pattern
    O2 --> Pattern
    O3 --> Pattern
    Pattern --> Gen
    
    style O1 fill:#3b82f6,stroke:#1e40af,color:#fff
    style O2 fill:#3b82f6,stroke:#1e40af,color:#fff
    style O3 fill:#3b82f6,stroke:#1e40af,color:#fff
    style Pattern fill:#f59e0b,stroke:#d97706,color:#000
    style Gen fill:#22c55e,stroke:#16a34a,color:#fff
```

## DOT Template

```dot
digraph Inductive {
    rankdir=TB;
    node [shape=box, style="filled,rounded"];
    
    O1 [label="Observation 1", fillcolor="#3b82f6", fontcolor="white"];
    O2 [label="Observation 2", fillcolor="#3b82f6", fontcolor="white"];
    O3 [label="Observation 3", fillcolor="#3b82f6", fontcolor="white"];
    
    Pattern [label="Pattern Recognition\nCommon thread", 
             fillcolor="#f59e0b", fontcolor="black"];
    
    Gen [label="Generalization\nGeneral principle", 
         fillcolor="#22c55e", fontcolor="white", shape=box];
    
    O1 -> Pattern [color="#3b82f6", penwidth=2];
    O2 -> Pattern [color="#3b82f6", penwidth=2];
    O3 -> Pattern [color="#3b82f6", penwidth=2];
    Pattern -> Gen [color="#f59e0b", penwidth=2];
}
```

## Worked Example

Based on the database connection timeout scenario from `reference/output-formats/inductive.md`:

### Mermaid

```mermaid
graph TD
    O1["🔵 Monday 2026-04-06<br/>Deploy failed with<br/>DB timeout"]
    O2["🔵 Wednesday 2026-04-08<br/>Deploy failed with<br/>DB timeout"]
    O3["🔵 Friday 2026-04-10<br/>Deploy failed with<br/>DB timeout"]
    
    Pattern["⭐ Pattern<br/>All recent deploys fail<br/>at DB connection phase"]
    
    Gen["✓ Generalization<br/>Recent production deploys<br/>consistently fail at DB<br/>connection phase"]
    
    CEx["⚠️ Counterexample<br/>Tuesday 2026-04-07<br/>deploy succeeded"]
    
    O1 --> Pattern
    O2 --> Pattern
    O3 --> Pattern
    Pattern --> Gen
    CEx -.->|contradicts| Gen
    
    style O1 fill:#3b82f6,stroke:#1e40af,color:#fff
    style O2 fill:#3b82f6,stroke:#1e40af,color:#fff
    style O3 fill:#3b82f6,stroke:#1e40af,color:#fff
    style Pattern fill:#f59e0b,stroke:#d97706,color:#000
    style Gen fill:#22c55e,stroke:#16a34a,color:#fff,stroke-width:3px
    style CEx fill:#ef4444,stroke:#991b1b,color:#fff
```

### DOT

```dot
digraph InductiveTimeout {
    rankdir=TB;
    node [shape=box, style="filled,rounded"];
    
    O1 [label="Monday 2026-04-06\nDeploy failed with\nDB timeout", 
        fillcolor="#3b82f6", fontcolor="white"];
    O2 [label="Wednesday 2026-04-08\nDeploy failed with\nDB timeout", 
        fillcolor="#3b82f6", fontcolor="white"];
    O3 [label="Friday 2026-04-10\nDeploy failed with\nDB timeout", 
        fillcolor="#3b82f6", fontcolor="white"];
    
    Pattern [label="Pattern\nAll recent deploys fail\nat DB connection phase", 
             fillcolor="#f59e0b", fontcolor="black"];
    
    Gen [label="Generalization\nRecent production deploys\nconsistently fail at DB\nconnection phase", 
         fillcolor="#22c55e", fontcolor="white", penwidth=3];
    
    CEx [label="Counterexample\nTuesday 2026-04-07\ndeploy succeeded", 
         fillcolor="#ef4444", fontcolor="white"];
    
    O1 -> Pattern [color="#3b82f6", penwidth=2];
    O2 -> Pattern [color="#3b82f6", penwidth=2];
    O3 -> Pattern [color="#3b82f6", penwidth=2];
    Pattern -> Gen [color="#f59e0b", penwidth=2];
    CEx -> Gen [label="contradicts", style=dashed, color="#ef4444", penwidth=2];
}
```

## Special Cases

- **Confidence encoding**: 
  - `confidence ≥ 0.85`: Thick border (penwidth=3) on generalization
  - `0.6 ≤ confidence < 0.85`: Normal border (penwidth=2)
  - `confidence < 0.6`: Dotted border (style=dotted) to show weak confidence
  
- **Sample size indicator**: If `sampleSize` is small (≤3), add a badge to the pattern node (e.g., "🔍 n=3") to indicate limited sample.

- **Counterexamples**: Render each counterexample as a red rectangle with a dashed edge to the generalization, labeled "contradicts" or "exception: [brief description]". Multiple counterexamples reduce confidence (model this via border style/thickness).

- **Multiple patterns**: If the inductive reasoning identifies more than one pattern (unlikely in the simple format but possible in extended cases), show them as separate orange ellipses, each feeding into the generalization with different arrow weights.

