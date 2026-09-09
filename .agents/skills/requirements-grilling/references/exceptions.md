# Exceptions and provenance

Read the section whose condition occurred; do not load these branches into an ordinary round preemptively.

## Deferred decisions

Record the question, why it matters, its current answerer, the decisions it blocks, and the condition for resuming. Keep it `deferred` until an attributable answer resolves it. Continue only independent branches of the same item.

## Questions for third parties

Keep the functional gap `blocking` unless the stakeholder deliberately chooses `deferred`. Record:

- the responsible role or named source;
- the exact product question and why it matters;
- every decision or deliverable it blocks;
- state, answer, provenance, and answer date.

The question remains visible after resolution as decision history. Relaying an unattributed answer does not resolve it.

## Contradictory sources

A contradiction about observable behavior is always `blocking`. Show each conflicting position, identify its source, explain the product impact, and recommend a resolution when evidence supports one. Only an authorized stakeholder decision resolves the contradiction; source recency alone does not.

## New evidence

Read and identify the new evidence before resuming the interview. Report which decisions it confirms, contradicts, invalidates, or reopens. Recompute both the tree and current frontier. A formerly resolved decision returns to `blocking` when the evidence makes its product meaning uncertain again.

## Minimum visible ledger

When the caller has no prescribed artifact, use a table with these fields:

| ID | State | Decision or question | Prerequisites | Answerer/source | Blocks | Resolution |
|---|---|---|---|---|---|---|

Do not copy pure technical choices into this ledger.

**Exception check:** every postponement, third-party question, contradiction, and reopened decision remains traceable until an attributable resolution is incorporated.
