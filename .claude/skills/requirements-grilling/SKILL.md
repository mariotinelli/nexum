---
name: requirements-grilling
description: Interview stakeholders to expose and resolve functional requirement gaps for a product scope, Feature, or Bug. Use while defining or reviewing observable behavior and acceptance; leave technical design and implementation planning to later roles.
---

# Requirements grilling

Turn the available evidence and stakeholder answers into shared functional understanding. Product decisions belong to the stakeholder; technical facts come from the available repository, tools, and sources.

Use the caller's artifact contract when one exists. Otherwise keep a compact decision ledger in the conversation. Do not invent a project workflow, publish remotely, or create implementation artifacts.

## 1. Establish the decision tree

Read every declared source that is available and inspect relevant technical facts rather than asking the stakeholder to retrieve them. Treat sources as evidence, not authority. Identify the item being decided, its observable goal, and the functional decisions that branch from it.

Before the first round, read [the functional boundary and decision-tree rules](references/decision-tree.md).

**Complete when:** every known functional uncertainty is represented as a decision or a descendant of one, every environmental fact needed by the current frontier has been checked or marked as an unsettled prerequisite, and pure implementation choices have been excluded.

## 2. Ask the complete frontier

The frontier is every unresolved functional decision whose prerequisites are settled. In one round, ask every frontier question that remains necessary regardless of how the other questions in that round are answered. Hold dependent questions for a later round.

Number questions monotonically for the session. For each question:

```markdown
Q<N> — <decision title>

<question and, when useful, clearly separated options>

Recommendation: <recommended answer and why the evidence, consistency, or product trade-off supports it>
```

When there is no sound basis for a recommendation, say so and explain what product trade-off the stakeholder must choose. A recommendation is never an answer on the stakeholder's behalf.

Wait for answers after presenting the whole frontier.

**Complete when:** all and only the independent questions on the current frontier have been presented together, each has a unique number, and every supported recommendation includes its rationale.

## 3. Reconcile the round

Record each answer with its source and update the tree. Mark the affected gap `resolved` only when the answer settles the decision and its material ambiguity. Reopen descendants whose assumptions the answer invalidates, then recompute the frontier.

If an answer is postponed, belongs to a third party, conflicts with evidence, or new evidence arrives, read [the exception and provenance rules](references/exceptions.md) before continuing.

Do not preserve pure technical questions in requirement documents or a backlog for later. When a question mixes behavior with a proposed implementation, ask only for the externally perceived effect; leave the mechanism to the implementation role.

**Complete when:** every answer has been incorporated or remains visibly open with the correct state, invalidated decisions have been reopened, and the next frontier reflects the updated prerequisites.

## 4. Repeat and close

Repeat complete-frontier rounds until an exhaustive audit finds:

- every relevant branch in the decision tree visited;
- no `blocking` or `deferred` functional gap;
- no unresolved source contradiction;
- no unanswered third-party question;
- no silently assumed observable behavior, boundary, or acceptance condition;
- a coherent explanation of the goal, flows, rules, limits, and observable acceptance.

An empty frontier is insufficient when an unsettled prerequisite or unexpanded branch still exists. Present the reconciled understanding and ask the stakeholder to confirm it explicitly. Silence, a partial answer, or merely answering the last numbered question is not confirmation.

**Complete when:** the audit passes and the stakeholder explicitly confirms the reconciled understanding. Until both are true, report the interview as blocked or deferred and do not hand it off as complete.

When evaluating this discipline itself, use the machine-readable [evaluation scenarios](references/evaluation-scenarios.json).

## Attribution

The decision-tree, complete-frontier round, numbered-question, recommendation, and explicit-confirmation structure is substantially adapted from Matt Pocock's `grilling` skill. See [NOTICE.md](NOTICE.md) and [LICENSE-MATT-POCOCK](LICENSE-MATT-POCOCK).
