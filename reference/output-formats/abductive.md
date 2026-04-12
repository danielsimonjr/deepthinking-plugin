# Abductive Thought — Output Format

Reasoning from surprising observations to the best available explanation — generating and ranking candidate hypotheses.

## JSON Schema

```json
{
  "mode": "abductive",
  "observations": [
    { "id": "<string>", "description": "<what was observed>", "confidence": <0-1> }
  ],
  "hypotheses": [
    {
      "id": "<string>",
      "explanation": "<what would explain the observations>",
      "assumptions": ["<assumption 1>", "..."],
      "predictions": ["<testable prediction 1>", "..."],
      "score": <0-1>
    }
  ],
  "currentHypothesis": { "...same shape as a hypothesis object, optional..." },
  "evaluationCriteria": {
    "parsimony": <0-1>,
    "explanatoryPower": <0-1>,
    "plausibility": <0-1>,
    "testability": <boolean>
  },
  "evidence": [
    {
      "hypothesisId": "<id from hypotheses>",
      "type": "supporting | contradicting | neutral",
      "description": "<what the evidence shows>",
      "strength": <0-1>
    }
  ],
  "bestExplanation": { "...same shape as a hypothesis object, optional..." }
}
```

## Required Fields

- `mode` — always `"abductive"`
- `observations` — at least one observation object with `id`, `description`, and `confidence`
- `hypotheses` — at least one hypothesis object with `id`, `explanation`, `assumptions`, `predictions`, and `score`
- `evaluationCriteria` — all four sub-fields: `parsimony`, `explanatoryPower`, `plausibility`, `testability`
- `evidence` — array of evidence objects (may be empty at the start of reasoning; should be populated as evidence accumulates)

## Worked Example

Input: "Users on the analytics dashboard are seeing 503 errors, but ONLY on Tuesday mornings between 9–10 AM. What's the best explanation?"

Output:

```json
{
  "mode": "abductive",
  "observations": [
    {
      "id": "o1",
      "description": "Analytics dashboard returns 503 errors exclusively on Tuesday mornings between 9:00 AM and 10:00 AM",
      "confidence": 0.97
    },
    {
      "id": "o2",
      "description": "Error rate returns to zero by 10:05 AM with no manual intervention",
      "confidence": 0.95
    },
    {
      "id": "o3",
      "description": "Affected endpoint is /api/reports/dashboard — other API endpoints remain healthy during the same window",
      "confidence": 0.92
    },
    {
      "id": "o4",
      "description": "Database CPU spikes to 95% during the 9–10 AM Tuesday window; normal the rest of the week",
      "confidence": 0.88
    }
  ],
  "hypotheses": [
    {
      "id": "h1",
      "explanation": "A weekly scheduled job (e.g., ETL aggregation or data warehouse sync) runs at 9 AM every Tuesday and saturates the database, crowding out dashboard queries",
      "assumptions": [
        "A cron job or scheduler fires at 09:00 on Tuesdays specifically",
        "The job issues heavy read/write queries that compete with dashboard query traffic",
        "The connection pool is shared between the scheduled job and the dashboard API"
      ],
      "predictions": [
        "Cron job logs show a Tuesday 09:00 entry corresponding to a long-running query",
        "Disabling or rescheduling the job would eliminate the 503 window",
        "Database slow-query logs show the same tables used by both the job and the dashboard"
      ],
      "score": 0.82
    },
    {
      "id": "h2",
      "explanation": "The weekly BI report generation pipeline materializes results at Tuesday 9 AM, causing write-heavy lock contention on the reports table",
      "assumptions": [
        "BI report materialization writes to the same reports table the dashboard reads from",
        "Table-level or row-level locks are held during materialization",
        "The dashboard's SELECT queries time out waiting for the lock to release"
      ],
      "predictions": [
        "Database lock-wait logs show contention on the reports table between 09:00 and 10:00 on Tuesdays",
        "Shifting the BI pipeline to run at 6 AM would move or eliminate the 503 window",
        "Adding a read replica and routing dashboard reads there would bypass the lock"
      ],
      "score": 0.71
    },
    {
      "id": "h3",
      "explanation": "Application cache is flushed every Monday night, causing a cache cold-start stampede on Tuesday morning when users hit the dashboard simultaneously",
      "assumptions": [
        "The dashboard relies on a cache layer that is cleared on Monday nights",
        "User traffic surges at 9 AM Tuesday",
        "Cache misses fall through to expensive database queries, overwhelming the DB"
      ],
      "predictions": [
        "Cache hit-rate metrics show near-zero Tuesday 9–9:30 AM, recovering by 9:45 AM",
        "Pre-warming the cache before 9 AM Tuesday would reduce or eliminate the errors"
      ],
      "score": 0.54
    }
  ],
  "evaluationCriteria": {
    "parsimony": 0.75,
    "explanatoryPower": 0.88,
    "plausibility": 0.82,
    "testability": true
  },
  "evidence": [
    {
      "hypothesisId": "h1",
      "type": "supporting",
      "description": "Application logs show a `weekly_etl_job` entry starting at 09:00:02 every Tuesday for the past six weeks",
      "strength": 0.85
    },
    {
      "hypothesisId": "h2",
      "type": "supporting",
      "description": "Database slow-query log shows a 47-minute INSERT … SELECT on the `report_snapshots` table starting at 09:00 every Tuesday",
      "strength": 0.78
    },
    {
      "hypothesisId": "h3",
      "type": "contradicting",
      "description": "Cache monitoring shows hit rates are normal (>90%) at 9 AM Tuesday — no evidence of a cold-start stampede",
      "strength": 0.72
    }
  ],
  "bestExplanation": {
    "id": "h1",
    "explanation": "A weekly scheduled ETL job runs at 9 AM every Tuesday and saturates the database, crowding out dashboard queries",
    "assumptions": [
      "A cron job or scheduler fires at 09:00 on Tuesdays specifically",
      "The job issues heavy read/write queries that compete with dashboard query traffic",
      "The connection pool is shared between the scheduled job and the dashboard API"
    ],
    "predictions": [
      "Cron job logs show a Tuesday 09:00 entry corresponding to a long-running query",
      "Disabling or rescheduling the job would eliminate the 503 window",
      "Database slow-query logs show the same tables used by both the job and the dashboard"
    ],
    "score": 0.82
  }
}
```

## Verification Checklist

Before emitting, verify:

- `mode` is exactly `"abductive"`
- `observations` has at least 1 entry; each has `id`, `description`, and `confidence` in [0, 1]
- `hypotheses` has at least 2 entries — a single hypothesis is not abductive reasoning, it is assumption
- All hypothesis `score` values are distinct — identical scores indicate the evaluation is incomplete
- The highest-scoring hypothesis is meaningfully better than the second-best (score gap ≥ 0.05); if scores are nearly equal, note this uncertainty explicitly
- `evaluationCriteria` is fully populated: all four sub-fields present, numeric values in [0, 1], `testability` is boolean
- At least one `evidence` item exists once any concrete data is available; each item references a valid `hypothesisId`
- `bestExplanation` is consistent with the highest `score` in `hypotheses` — do not point to a lower-scoring hypothesis without an explicit override reason
- Assumptions in `bestExplanation` are the specific claims that could be falsified to overturn the conclusion
- `parsimony` should be lower (closer to 0) when the winning hypothesis requires many assumptions; `explanatoryPower` should reflect how much of the observation set the hypothesis actually covers
