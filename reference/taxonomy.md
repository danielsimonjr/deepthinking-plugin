# Reasoning Mode Taxonomy

This file is the canonical reference for which mode applies to which problem shape. It will grow as more modes are added in future versions.

## v0.1.0 Modes

### Sequential (`sequential`)
- **Category:** think-standard
- **Shape:** Iterative planning with revision
- **Signals:** "plan", "break down", "steps to", "how to approach"
- **Anti-signals:** Formal logical inference (use deductive), pattern-from-cases (use inductive)

### Inductive (`inductive`)
- **Category:** think-core
- **Shape:** Observations → pattern → generalization
- **Signals:** Multiple specific examples, "pattern", "trend", "in general", "these all..."
- **Anti-signals:** Premise-driven inference (use deductive), single-case analysis (use sequential)

### Deductive (`deductive`)
- **Category:** think-core
- **Shape:** Premises → logical inference → conclusion
- **Signals:** "if X then Y", explicit rules, syllogisms, "can we conclude"
- **Anti-signals:** Uncertain premises (consider bayesian in a later version), observation-driven reasoning (use inductive)

## How to Read This File

When a category skill is loaded, the skill can read from this taxonomy to (a) confirm the problem fits its mode, and (b) recommend switching to a different mode if it does not fit.

## Future Modes

Not yet implemented in v0.1.0 (ship in future versions):
- Core: shannon, hybrid, mathematics, physics, computability
- Causal: causal, counterfactual, temporal, historical
- Probabilistic: bayesian, evidential
- Strategic: gametheory, optimization, constraint
- Analytical: analogical, firstprinciples, metareasoning, cryptanalytic
- Scientific: scientificmethod, systemsthinking, formallogic
- Engineering: engineering, algorithmic
- Academic: synthesis, argumentation, critique, analysis
- Advanced: recursive, modal, stochastic
