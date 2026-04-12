# Mode Index — Auto-Recommendation Decision Tree (v0.1.0)

When the user invokes `/think` without specifying a mode, use this decision tree to pick the most appropriate one.

## Decision Tree

Ask yourself:

1. **Does the user want to generalize from specific cases?**
   Signals: multiple observations provided, "what pattern", "in general", "these all show", "trend"
   → **Inductive**

2. **Does the user want to apply established rules to derive a conclusion?**
   Signals: "if X then Y", "given these rules", "can we conclude", explicit premises
   → **Deductive**

3. **Does the user want to break a complex task into ordered steps or iterate with revision?**
   Signals: "break down", "plan", "steps to", "how should I approach", multi-step workflows
   → **Sequential**

If none of the above clearly fit, default to **Sequential** and explain you're treating the task as iterative planning.

## Example Mappings

| User prompt | Recommended mode | Reason |
|---|---|---|
| "Break down the steps to migrate this database" | sequential | Explicit "break down" and multi-step workflow |
| "Given these three incidents, what pattern do they share?" | inductive | Multiple observations, asking for pattern |
| "If all users in admin can edit posts and Alice is in admin, can Alice edit posts?" | deductive | Explicit premises, formal inference |
| "Why did the last three deployments fail?" | inductive | "The last three" implies pattern-finding from observations |
| "What should our caching strategy be for this API?" | sequential | Multi-step design decision |
| "Plan the refactor of the auth module" | sequential | Explicit "plan" and multi-step work |

## Explain Your Choice

When auto-recommending, always start your response with one sentence naming the chosen mode and why. Example:

> "Using inductive reasoning to identify a pattern across the three deployment failures."

This transparency lets the user override you with `/think <mode>` if they prefer a different frame.
