# Pause and resume

Use this branch only after Redmine preflight succeeds. It covers a deferred product decision, a question for a third party, a voluntary stop, an incomplete run, an item-lock conflict, an open functional gap, or a `new-scope` catalog change.

## Own the item

Build one item key that is stable for the whole run: use the definitive repository-relative folder when it already exists; otherwise use the confirmed project plus normalized intended item identity and retain that key after issue creation. Run `python <project-flow-skill>/scripts/manage_lock.py acquire <docs/harness/.locks> <item-key> <run-id>`, then copy its returned `lock_id`, item key, relative lock path, and acquisition time into state before writing other artifacts. Run `manage_lock.py verify` with that run and lock ID before every state replacement or remote call so a recovered lock fences a straggler.

An existing lock is a recoverable conflict, not permission to continue. Report its run ID, lock ID, and acquisition time. Recover only after the user confirms that exact owner is abandoned: run `manage_lock.py recover` with the existing lock ID and a non-empty reason. The compare-and-replace operation refuses a changed owner. Runs with different item keys use different lock files and remain independent. Release requires the current lock ID and happens only after completion or explicit abandonment handling.

**Complete when:** this execution holds the exact lock recorded in state, or it has stopped without changing the competing run.

## Pause

Finish the current atomic local write, but start no remote mutation or later phase. Append one pause record with status `paused`, kind `decision-deferred`, `third-party-question`, or `voluntary-stop`, the prior phase, explicit reason, objective resume condition, first incomplete `resume_phase`, and timestamp. Set top-level `phase` to `paused` and validate the candidate against the prior state.

For a deferred decision, third-party question, or functional gap, append a stable record with its owner, reason, blocked decisions or items, question or description, and time. Mirror questions in `history/pending-questions.md` (the existing root file for a legacy run). Ask every independent question whose answer does not rely on a blocked decision, recording those decisions normally; do not approve the requirement, publish, move to another item, or invoke a later flow while any deferred question or functional gap remains open.

**Complete when:** persisted state and human history agree on why work stopped, what exact observation permits resume, and which phase remains incomplete; no blocked phase or remote operation ran.

## Resume

Rerun preflight before reading intake or state content beyond what is necessary to locate the candidate. Validate the current state, explicitly recover its exact lock ID after confirming the old execution is abandoned, and verify the latest pause's objective condition. Record the returned replacement lock and recovery reason in state. Mark that pause `resumed` with time and concrete evidence, restore `phase` to its recorded `resume_phase`, and validate the candidate with `--previous`.

Resolve a deferred question by retaining the original fields and adding status `resolved`, answer, answer source, and resolution time. Preserve the corresponding human entry. Never delete or rewrite prior questions, decisions, approvals, completed phases, issue identity, or completed remote operations. A decision may become `reopened` and an approval may become `invalidated` only with attributed reason and time; otherwise it remains valid.

After resuming a `voluntary-stop`, retain the original `stop` decision and append exactly one attributed `continue` or `finish` decision for the same completed item. The new decision is valid only after the corresponding pause is durably marked `resumed`; an older pause for another decision cannot authorize it. This append-only exception does not permit duplicate decisions in any other circumstance.

Reread the issue and its relations, compare their fingerprints with local operations, and reconcile every `unknown` outcome before continuing. Preserve completed operations and append reconciliation observations; a remote match completes locally, proven absence permits retry of the unchanged approved payload, and divergence blocks for an attributed decision. Use the state and evidence locations from the [artifact contract](artifact-contract.md); `.work/` candidates are never authoritative resume states. Then continue from the first incomplete remote operation inside the first phase absent from `completed_phases`. For a scope, select the first active catalog item not completed in the approved total order; completed items, issue IDs, catalog history, and relations remain intact. Do not repeat a completed phase, operation, or equivalent relation. When state validation identifies unknown schema, invalid content, impossible transition, unresolved divergence, or a lock owned elsewhere, stop with its sanitized diagnostic and corrective action instead of repairing silently.

**Complete when:** the pause is durably marked resumed, all still-valid history is unchanged, the item lock is owned, and execution is positioned at exactly the first incomplete phase.

## Pause a catalog change

In `new-scope`, a proposed division, union, addition, removal, retyping, dependency change, or reorder is a `catalog-change` pause. Record the affected item IDs and show the impact on evidence ownership, graph edges, parallel-ready groups, total order, issues already created, and artifact paths. Invalidate the current catalog approval before modifying catalog data, then require approval of the complete revised catalog and order. Preserve all created issues and item histories. Append the approved split, merge, or other change with affected items, source ownership, graph/order impact, preserved issue IDs, and artifact paths; retired entries remain addressable instead of disappearing.

When a catalog change appears during any item interview, pause both scope and item states with the same reason and objective resume condition. Resume the item only after the revised complete catalog has a valid approval and the current item's identity remains valid.

**Complete when:** no remote mutation occurs during the pause, both states agree when an item has started, and exactly one valid approval covers the current complete catalog and order.
