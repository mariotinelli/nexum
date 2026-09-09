# Functional boundary and decision tree

Use this reference before building the first frontier and whenever classification is uncertain.

## Classify the uncertainty

A **functional gap** needs a product decision to explain externally observable behavior, a business rule, a boundary, a result, or acceptance. It belongs in the tree.

A **technical choice** selects a mechanism without changing visible behavior or scope. Repository structure, persistence, caching, retry algorithms, files, infrastructure, and similar mechanisms belong to later implementation roles. Inspect the environment for facts that constrain the product discussion, but keep the mechanism out of the requirement and interview.

If an uncertainty mixes the two, remove the proposed mechanism and expose the product effect. For example, replace “Should this use a queue?” with “May the user wait for completion, or must the result arrive later?”

Preserve a non-functional requirement only when the evidence states it extremely explicitly. Do not proactively elicit performance, security, accessibility, or availability targets, and do not turn a vague mention into a gap.

## States

- `blocking`: a functional decision is unanswered. Descendants cannot advance, while unrelated frontier branches may continue.
- `deferred`: the decision was deliberately postponed. Other independent questions for the same item may continue, but approval, publication, the next item, and downstream workflows remain closed.
- `resolved`: the decision and its material ambiguity have an attributable answer incorporated into the shared understanding.

Only these states describe functional gaps. A technical choice is excluded rather than marked deferred or resolved.

## Grow the tree

Start from the observable goal, then expand only branches relevant to the item. Test for gaps in:

- actors, permissions, and success;
- user-perceived inputs and results;
- main, empty, initial, and final states;
- alternatives, cancellation, repetition, and recovery from functional errors;
- validations, messages, business rules, calculations, dates, and time zones;
- user-visible concurrency, integrations, notifications, and audit history;
- user-visible compatibility or migration;
- acceptance conditions and boundaries inside or outside the item.

This is a coverage lens, not a questionnaire. A branch exists only when evidence, an answer, or the nature of the item makes it relevant.

## Compute a round

For every unresolved decision, list its unsettled prerequisites. The round contains the decisions with none. Remove any candidate whose need or wording could change based on another candidate's answer; it is a descendant for the next round. Ask all remaining candidates together.

After the answers, update dependencies before discovering more detail. A changed parent can resolve, replace, or reopen an entire descendant branch.

**Frontier check:** every question in the round can be answered independently now, and every other currently answerable functional decision is also present.
