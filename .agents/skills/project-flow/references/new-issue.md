# New issue: shared Feature and Bug cycle

Use this path only after the preflight and context selection in `SKILL.md` pass. Read [catalog discipline](catalog-discipline.md) for capability boundaries, evidence reconciliation and project title conventions.

## 1. Normalize and orient

Follow `intake.md` to inventory, fully extract, and separately normalize every declared source. When a source is presented as a design or design evidence, also apply `design-inputs.md` before accepting it. Create the run state, read [pause and resume](pause-resume.md), and acquire its item lock before replacing any state or making a remote call. Inspect the repository for stack, existing behavior, and canonical vocabulary while excluding dependencies, generated output, caches, binaries, and secret-bearing files. Retain only exclusion patterns and non-secret technical context for the state created after classification.

If `new-issue` evidence contains more than one product capability after the cohesion assessment, recommend `new-scope`, explain the proposed split, and wait for confirmation. On confirmation, continue from the existing normalized evidence and repository orientation without restarting intake. If `new-scope` contains one item, continue directly through this shared cycle without restarting.

**Complete when:** every retained source is normalized and hashed when applicable, every declared design passes its stricter gate, repository evidence is recorded without secrets, the exact item lock is held, and the input describes exactly one demand.

## 2. Confirm classification and novelty

Suggest Feature when the demand primarily asks for a new observable outcome; suggest Bug when it primarily reports a difference between current and expected behavior. Explain the evidence for the suggestion and require the user to confirm Feature or Bug. Map and, when non-literal, confirm the tracker for that type.

Search the selected project for semantically similar issues using the demand's goal, actors, current/expected behavior, and domain terms rather than title-only equality. Present every credible candidate with its ID, title, status, and reason for similarity. A match never authorizes reuse or an update. Ask whether this is a new demand or the same demand as one candidate and record the attributed decision.

Create the versioned run state with the source inventory and hashes, repository evidence, classification suggestion and rationale, confirmed type, similarity candidates and decision, identity, and times. When the user identifies an existing demand, validate the state at `item-ready`, report its issue ID, and stop successfully before category selection, creation approval, or any Redmine mutation. Direct the user to an editing workflow without editing, commenting on, linking, or changing the existing issue.

**Complete when:** the classification is explained and confirmed, the matching tracker is resolved, and either novelty is confirmed or the run has ended without a remote mutation because an existing demand was identified.

## 3. Prepare the creation

Recommend the closest existing category with evidence from its name and project context. The user must confirm that category or explicitly choose another existing category or no category. Record the attributed decision in state. Category creation is outside this release.

In requirement state v4, confirm `title_convention` and `delivery` using the shared discipline, then compose the initial title from those fields. A scope item inherits these exact confirmed fields through `scope_item`; do not ask them again. Include the visible delivery, user result and boundaries in the complete initial objective. Prepare the confirmed tracker, category, and initial status. For a Bug, the objective identifies the observed deviation without inventing a cause or deterministic reproduction. Read the Redmine projection reference, show the complete creation preview, and ask the first meaningful remote confirmation. Do not ask for priority, assignee, version, dates, or estimate.

**Complete when:** a new demand and existing category or no category are confirmed, and the user explicitly approves the exact creation payload.

## 4. Create without duplication

Set `remote_operations.create` to `approved` with approval identity, time, and the exact payload fingerprint; validate and atomically persist that state before calling `redmine_create_issue`. After a successful response, immediately persist the returned issue ID, observation, and `completed` operation before moving files or advancing a phase. Move the durable run files without overwriting an existing directory: Feature files go to `docs/harness/features/<REDMINE-ID>-<slug>/`; Bug files go to `docs/harness/bugs/<REDMINE-ID>-<slug>/`.

After a known failure, append only a sanitized attempt result and retain the approved operation for a safe retry. After an unknown outcome, persist `unknown` and reconcile before any retry: search the confirmed project using the immutable run identity and approved payload, then compare every credible candidate. One exact match completes the operation with that issue ID; no match records `absent` and permits retrying the same fingerprint; ambiguity or divergence blocks for user resolution. If state already has an issue ID or the create operation is completed, never call create. A credential, request header, API key, raw exception, or unsanitized response never enters state, artifacts, or output.

**Complete when:** exactly one remote issue is identified, its ID and completed create operation were persisted before any later action, and source plus state live in the definitive type-specific directory.

## 5. Interview and approve

For a Feature, read [the Feature interview and document contract](new-issue-feature.md). For a Bug, read [the Bug interview and document contract](new-issue-bug.md). Create `interview.md` at the first round and invoke `requirements-grilling` with all normalized sources, repository evidence, and selected document contract. Append every numbered question, recommendation, answer, provenance, reopened decision, and explicit understanding confirmation to the interview history.

For evidence received after decisions exist, return to the intake contract. Show and record the confirmed, contradicted, and reopened decisions before asking more questions. Resolve the resulting gaps before drafting or publishing.

If a decision is deferred or belongs to a third party, follow the pause/resume contract. Continue asking independent questions whose answers do not depend on deferred decisions. A pending deferred question prevents requirement approval and every later phase, even when the draft is otherwise complete.

Use `domain-modeling` only when its invocation gate fires. Keep item-specific decisions in the requirement; only reusable, resolved terminology may update domain documentation, and Project Flow only flags architecture candidates. Present the whole document and require explicit approval. Editorial corrections may remain in this run; a behavioral scope change becomes a separate candidate and does not create another issue.

**Complete when:** the grilling audit has no open gaps or contradictions, the interview preserves the complete decision history, the type-specific document contract passes, and the user explicitly approves the document.

## 6. Publish and finish

Reread the issue immediately before publication and on every resume. Preserve human content outside the managed delimiters byte-for-byte. Compare the current managed section with its last persisted fingerprint; present every human requirement change as a divergence. Incorporate an accepted change into the canonical document only after confirmation, invalidate the old requirement/publication approval, resolve affected gaps, and approve the revised canonical document before preparing a new publication payload. A rejected change remains recorded and is not copied into the canonical document.

Build the autonomous final projection, show the complete update preview and human-content preservation result, then ask the second meaningful remote confirmation. Persist its fingerprint and approval before calling `redmine_update_issue`. On success, persist the completed publish operation and resulting managed-section fingerprint before relations or phase advancement. On known failure, record only a sanitized failure and retry the unchanged approved payload; on unknown outcome, reread and compare before retrying. A matching remote fingerprint completes the operation, an unchanged prior fingerprint permits retry, and any other state is a surfaced divergence.

For each approved native relation, create one stable key from relation type and endpoint issue IDs. Reread existing relations first; mark an existing equivalent relation completed without calling create, otherwise persist approval and call `redmine_create_relation`. Persist each completed relation before considering the next. Unknown outcomes use the same reread-and-compare rule, so repeating reconciliation cannot duplicate an edge. Summarize relations under the final publication approval; any relation not already approved requires a new preview and confirmation.

Validate all artifacts and advance to `completed` only when create, publish, and every planned relation are completed and no requirement divergence is pending. Release the item lock only after the final state has been persisted; a paused run retains its lock so a later execution must explicitly recover it. Report project, issue, artifact paths, approvals, operations, validations, and the recommended next role. Offer a commit, but create one only with explicit permission.

**Complete when:** the final issue description is understandable without the interview, points to the canonical file, preserves unmanaged human content, every remote operation and divergence is reconciled, approvals are attributable, and final state validation succeeds.
