# Mode Index — Auto-Recommendation Decision Tree (v0.1.0)

When the user invokes `/think` without specifying a mode, use this decision tree to pick the most appropriate one.

## Decision Tree

Ask yourself, **in order**:

1. **Are concrete observations actually provided in the prompt?**
   Inductive reasoning requires *data in hand*. If the user describes events, lists incidents, or gives specific cases you can count and examine — that's induction material. If the user merely *refers to* observations without including them ("why did X fail", "what's wrong with Y"), induction is premature. You cannot induct from data you don't have.
   - Observations present AND user wants a pattern → **Inductive**
   - Observations referenced but NOT in the prompt → **Sequential** (thought 1 gathers the data, a later thought may hand off to Inductive or Abductive once the data is known)

2. **Does the user want to apply established rules to derive a conclusion?**
   Signals: "if X then Y", "given these rules", "can we conclude", explicit premises present in the prompt
   → **Deductive**

3. **Does the user want to break a complex task into ordered steps, iterate, or investigate something where the first step is gathering information?**
   Signals: "break down", "plan", "steps to", "how should I approach", "why did X happen" (without supplied observations), multi-step workflows, investigations
   → **Sequential**

If none of the above clearly fit, default to **Sequential** and explain you're treating the task as iterative planning or investigation.

## Example Mappings

| User prompt | Recommended mode | Reason |
|---|---|---|
| "Break down the steps to migrate this database" | sequential | Explicit "break down" and multi-step workflow |
| "Given these three incidents (A, B, C), what pattern do they share?" | inductive | Multiple concrete observations IN the prompt, asking for a pattern |
| "If all users in admin can edit posts and Alice is in admin, can Alice edit posts?" | deductive | Explicit premises, formal inference |
| "Why did the last three deployments fail?" | sequential | References observations but doesn't provide them — start with a data-gathering thought; thought N can hand off to inductive/abductive once the data is known |
| "What should our caching strategy be for this API?" | sequential | Multi-step design decision |
| "Plan the refactor of the auth module" | sequential | Explicit "plan" and multi-step work |

## Explain Your Choice

When auto-recommending, always start your response with one sentence naming the chosen mode and why. Example:

> "Using inductive reasoning to identify a pattern across the three deployment failures."

This transparency lets the user override you with `/think <mode>` if they prefer a different frame.
