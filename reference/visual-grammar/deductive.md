# Visual Grammar: Deductive

How to render a `deductive` thought as a diagram.

## Node Structure

Deductive reasoning moves from general premises to a specific conclusion. The diagram uses a **top-to-bottom pyramid layout**:

- **Premises** (top tier) → Rendered as **blue rectangles**, one per premise in the `premises` array
- **Logic Form** (middle) → Label on the connecting edge (e.g., "modus ponens", "modus tollens", "syllogism")
- **Conclusion** (bottom) → **Green pill/stadium shape** if `validityCheck` is true; **red pill** if `validityCheck` is false
- **Validity/Soundness badges** → Small labels or badges near the conclusion showing the check results

Color encoding for conclusion:
- Green (`#22c55e`) if `validityCheck == true`
- Red (`#ef4444`) if `validityCheck == false`
- Orange (`#f59e0b`) if `soundnessCheck == false` (premises may be false)

## Edge Semantics

- **Solid arrow** (`→`) — Premise feeds into the logical inference; all premises converge to a single conclusion arrow
- **Labeled edge** — The `logicForm` (e.g., "modus ponens") is displayed on the edge connecting premises to conclusion

## Mermaid Template

```mermaid
graph TD
    P1["🔵 Premise 1<br/>General principle"]
    P2["🔵 Premise 2<br/>Specific instance"]
    
    Conclusion["✓ Conclusion<br/>Derived specific fact<br/>(Valid: ✓)"]
    
    P1 -->|modus ponens| Conclusion
    P2 -->|modus ponens| Conclusion
    
    style P1 fill:#3b82f6,stroke:#1e40af,color:#fff
    style P2 fill:#3b82f6,stroke:#1e40af,color:#fff
    style Conclusion fill:#22c55e,stroke:#16a34a,color:#fff
```

## DOT Template

```dot
digraph Deductive {
    rankdir=TB;
    node [shape=box, style="filled,rounded"];
    
    P1 [label="Premise 1\nGeneral principle", 
        fillcolor="#3b82f6", fontcolor="white"];
    P2 [label="Premise 2\nSpecific instance", 
        fillcolor="#3b82f6", fontcolor="white"];
    
    Conclusion [label="Conclusion\nDerived specific fact\n(Valid: ✓)", 
                fillcolor="#22c55e", fontcolor="white"];
    
    P1 -> Conclusion [label="modus ponens", color="#3b82f6", penwidth=2];
    P2 -> Conclusion [label="modus ponens", color="#3b82f6", penwidth=2];
}
```

## Worked Example

Based on the Alice admin example from `reference/output-formats/deductive.md`:

### Mermaid

```mermaid
graph TD
    P1["🔵 All users in the admin<br/>group can edit posts"]
    P2["🔵 Alice is in the<br/>admin group"]
    
    Conclusion["✓ Alice can edit posts<br/><br/>Valid: ✓ Soundness: ✓"]
    
    P1 -->|modus ponens| Conclusion
    P2 -->|modus ponens| Conclusion
    
    style P1 fill:#3b82f6,stroke:#1e40af,color:#fff
    style P2 fill:#3b82f6,stroke:#1e40af,color:#fff
    style Conclusion fill:#22c55e,stroke:#16a34a,color:#fff,stroke-width:3px
```

### DOT

```dot
digraph DeductiveAdmin {
    rankdir=TB;
    node [shape=box, style="filled,rounded"];
    
    P1 [label="All users in the admin\ngroup can edit posts", 
        fillcolor="#3b82f6", fontcolor="white"];
    P2 [label="Alice is in the\nadmin group", 
        fillcolor="#3b82f6", fontcolor="white"];
    
    Conclusion [label="Alice can edit posts\n\nValid: ✓  Soundness: ✓", 
                fillcolor="#22c55e", fontcolor="white", penwidth=3];
    
    P1 -> Conclusion [label="modus\nponens", color="#3b82f6", penwidth=2];
    P2 -> Conclusion [label="modus\nponens", color="#3b82f6", penwidth=2];
}
```

## Special Cases

- **Invalid deduction**: If `validityCheck == false`, render the conclusion in **red** (`#ef4444`) with a thick red border and dashed edges from premises to indicate the logical chain is broken.

- **Unsound but valid**: If `validityCheck == true` but `soundnessCheck == false`, render the conclusion with a **yellow/orange border** (`#f59e0b`) to indicate the form is correct but one or more premises are not actually true in the real world.

- **Multiple logic forms**: If the reasoning applies multiple inference rules (e.g., chained modus ponens), show each intermediate step or label the edge with all applicable forms.

- **Premise contradiction**: If premises are logically inconsistent, add a red `⚠️ Contradiction` node pointing to both conflicting premises, indicating the deduction is unsalvageable.

