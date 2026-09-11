# Scope and requirement artifact contract

## Storage and retention

For new runs, keep only `feature.md`, `bug.md`, or `scope.md` at the root of its item/scope directory. Store the current state in `.flow/`, human interview and deferred-question history in `history/`, and normalized evidence in `sources/`. Create history and evidence files only when their workflow needs them. `.flow/`, `history/`, and `sources/` are versioned; `.work/` is disposable execution workspace.

After preflight and lock acquisition, prepare each new staging, item or scope directory from the repository root:

```sh
python <project-flow-skill>/scripts/manage_artifacts.py prepare . docs/harness/features/<REDMINE-ID>-<slug>
```

Substitute `bugs/<REDMINE-ID>-<slug>`, `scopes/<YYYY-MM-DD>-<scope-slug>`, or `.runs/<run-id>` as appropriate. This helper creates `.flow/` and `.work/` and atomically appends scoped temporary-file rules to `docs/harness/.gitignore`, preserving existing bytes. It does not stage files or create commits. Verify with `git check-ignore --no-index` that `.work/` is ignored and the canonical document, `.flow/`, history and sources are not; report any conflicting repository rule before relying on cross-checkout recovery. Live `.locks/` and pre-issue `.runs/` remain local; an unfinished pre-issue run must be recovered from its original workspace before transfer.

Relative source, scope-link and alignment-file references resolve from the item/scope root, even when the containing state is in `.flow/` or its candidate is in `.work/`. A new scope link is `../../scopes/<scope-slug>/.flow/scope-state.json`. Keep shared source links as `../../scopes/<scope-slug>/sources/<source>.md`. Repository-relative paths, such as lock keys and canonical publication footers, retain their existing meaning. Use forward slashes. `scripts/artifact_paths.py` centralizes these rules while retaining legacy flat-file resolution.

| Artifact | Destination and lifetime |
| --- | --- |
| Current requirement/scope state | `.flow/<type>-state.json` or `.flow/scope-state.json`; persist every accepted transition |
| Interview and deferred questions | `history/interview.md`, `history/pending-questions.md`; retain attributed history |
| State-validation candidates | `.work/<type>-state.json` or `.work/scope-state.json`; validate with `--previous` against the current state, replace atomically, and remove the candidate after success |
| Unapproved catalog/publication previews, exploratory review reports and unused snapshots | Reuse a phase-specific filename in `.work/`; retain only while needed by the active step |
| Approved remote operation evidence | `.flow/publications/<operation-uuid>/`; retain exact approved payload/preview and sanitized baseline/readback needed for retry, reconciliation or validation |
| Completed publication alignment | `.flow/publications/<alignment-uuid>/publication-alignment-<alignment-uuid>.json` and its evidence; retain immutable records |
| Legacy state needed by a review | `.flow/<type>-legacy.json` or `.flow/scope-legacy.json`; preserve exact bytes while referenced by history or validation |
| Scope final summary | Update `scope.md` and the state's required `final_summary`; do not emit a duplicate `final-summary.md` |

For ordinary creation/publication, use one stable operation UUID per approved operation and retain its directory association with the operation's approval in the human history. Before approval, materialize any required evidence at its durable path and record its exact hash; a durable record must not depend on `.work/`. A new attempt for the same approved operation reuses its payload and directory. Completed alignments retain the stricter UUID, immutable evidence and transition contract in the publication reference.

At each successful phase boundary, remove only this execution's known temporary files after confirming no retained state, approval, source, operation or legacy review refers to them and that the current state is durable. Pending/unknown operations keep their exact evidence. Unrecognized files require review; filenames such as `before`, `after` or `preview` alone never establish discardability. Avoid accumulating numbered review copies. On pause, preserve necessary work and report its path; resume from the durable state, not a candidate discovered in `.work/`.

**Complete when:** the canonical document is the only root-level file, durable references resolve without `.work/`, required evidence survives a checkout of versioned files, and no completed phase leaves an unneeded temporary candidate.

## Existing directories

Resume existing flat layouts in place unless organization is requested, preserving schema versions and append-only history. Locate both root states and `.flow/` states, including scopes; two states for one identity are a conflict to reconcile, not a reason to choose the newest. Read [legacy artifact organization](artifact-organization.md) when the user requests reorganizing existing files: its explicit path map and verified link-only reading copies allow complete relocation without inventing approvals or rewriting recorded state paths. A new publication alignment may use the organized layout while its canonical state remains in the legacy location.

For new scope and requirement states, omit `redmine.approved_status_id` and `redmine.approved_status_name`. Schemas accept these optional legacy fields and `approved-status` confirmations only to preserve existing history; they have no publication semantics. Local approval and completion fields describe the requirements workflow, independently of the remote issue status.

For `new-scope`, create `docs/harness/scopes/<YYYY-MM-DD>-<scope-slug>/` with:

- `scope.md`: the human-readable objective, complete catalog, canonical dependency graph, parallel-ready groups, suggested order, approval, progress, and item-gap summary; start from `templates/scope.md`. It is not an interview ledger: before an item starts, it contains no numbered functional questions or item-level decisions.
- `.flow/scope-state.json`: operational state conforming to `schemas/scope-state.schema.json` through multi-item `completed`.
- `sources/*.md`: normalized evidence shared by more than one item or received for the scope as a whole.

Use scope schema version `3` for new runs. Read [catalog discipline](catalog-discipline.md) for the additional metadata and deterministic projection. Its ordered phases are `mode-confirmed`, `inputs-normalized`, `repository-analyzed`, `catalog-proposed`, `catalog-approved`, `items-processing`, `relations-reconciled`, `scope-approved`, and `completed`; `paused` records an interruption without completing a phase. Validate each snapshot with `python <project-flow-skill>/scripts/validate_scope_state.py <scope-state.json>` and each replacement with `--previous`. The validator checks candidate disposition, single source ownership, graph/catalog agreement, deterministic order, sequential item progress, continue/stop decisions, functional gaps, preserved issue identities, native relations, reconciliation, approvals, validations, and final summary.

Scope versions `1` and `2` and requirement versions `2` and `3` remain readable and valid under their existing contracts. Retain the version when resuming; never silently upgrade. For an explicitly requested legacy catalog/delivery review, enrich a separate candidate with all new fields, keeping unknowns pending. Preserve identities, sources, item IDs, issues, paths, operations and history. Retain every prior approval as invalidated, obtain a new approval of the enriched content, and run the corresponding validator with `--previous <legacy-state.json> --review-legacy`. This flag validates enrichment; it never invents or writes decisions. A v1 scope maps its first-item progress into `item_progress` and retains its completed facts. Unresolved enrichment remains a draft; keep the legacy file intact until the new candidate and approval validate. Subsequent product revisions use ordinary transitions.

When the explicit scope review also changes capability boundaries or dependencies, pause for `catalog-change` and include `legacy_review: {previous_state, reason}` in the v3 candidate. `previous_state` is the exact legacy state being compared, preserving the previous catalog, graph and history. Only an unstarted item with no issue, artifact or publication may become `retired`; started or published items retain their lifecycle, IDs, issue IDs, paths and completed facts. Keep removed, unpublished and unapproved relation records with `status: retired`; their endpoints and stable keys stay unchanged. Published or approved relations require separate reconciliation and cannot be retired through this review. The preview includes the legacy snapshot hash and retired relations. Ordinary transitions preserve the snapshot unchanged.

Before approval, run the scope validator with `--previous <legacy-state.json> --review-legacy --draft`. This checks preservation without granting approval or permitting replacement. After the complete preview is approved, append its attributed catalog-change record and approval, then rerun without `--draft` before replacing the legacy file. Both commands are read-only; the draft flag never creates an approval.

The scope directory name uses a deterministic collision suffix (`-02`, `-03`, and so on). `scope.md` links item artifacts and shared sources by relative path. A shared normalized source remains in the scope and an item state may reference it as `../../scopes/<scope-slug>/sources/<source>.md`; do not copy it into each item. Item-exclusive or later evidence stays under that item. An unaffected requirement may retain the hash of its original catalog approval after a revision: that approval must remain in scope history, a current complete approval must validate, and the item's delivery, convention, type and project must still match exactly. Changed delivery metadata requires reconciliation and new approval.

**Scope complete when:** the scope state validates at `completed`; all active items and addressable native relations are completed and reconciled; all requirement/scope validations and approvals are recorded; no candidate or functional gap is open; and the final summary lists issues, relations, artifacts, approvals, validations, and the next recommendation.

## Feature and Bug artifacts

The definitive directory is `docs/harness/features/<REDMINE-ID>-<slug>/` for a Feature and `docs/harness/bugs/<REDMINE-ID>-<slug>/` for a Bug. Until the issue ID exists, use `docs/harness/.runs/<run-id>/`. `.runs/` contains only staging for the current fresh run and should be Git-ignored by the target repository.

Required final files:

- `<type>.md`: canonical, human-readable requirement; use `feature.md` from `templates/feature.md` or `bug.md` from `templates/bug.md`.
- `.flow/<type>-state.json`: operational metadata conforming to `schemas/requirement-state.schema.json`; use `feature-state.json` or `bug-state.json` consistently with `item_type`.
- `history/interview.md`: append-only human-readable question and decision history based on `templates/interview.md`.
- `sources/*.md`: one normalized file per retained source. Conversation input, when present, is `sources/conversation-input-001.md` and contains only the verbatim relevant user input.
- `history/pending-questions.md`: append-only deferred-question history based on `templates/pending-questions.md`; create it only after the first deferral and retain it after every question is resolved.

Use schema version `4` for new runs. Include `title_convention`, `delivery` and `scope_item` (null for standalone demands). Convention and delivery may be null during initial intake and must be complete by `item-ready`; scope items inherit them through a relative scope state link and approved catalog hash. Generate an immutable UUID for both `run_id` and `internal_identity`. State holds the first incomplete phase and operation, completed phase prefix, Redmine identity, attributed classification and novelty decisions, confirmed project/mappings/category, source inventory and hashes, repository orientation, attributed decisions and approvals, deferred-question and pause history, lock ownership, issue identity, payload fingerprints, append-only attempts and observations, requirement divergences, and create/publish/relation operation statuses. Requirement prose belongs in Markdown, not duplicated in JSON. Classification and similarity become mandatory when the run reaches `item-ready`; earlier snapshots remain valid while those decisions are pending. The validator continues to accept existing version 2 runs so their pause/resume history remains readable; retain their version and add reconciliation records supported by the validator rather than rewriting old history.

Allowed forward phases are `mode-confirmed`, `inputs-normalized`, `repository-analyzed`, `item-ready`, `item-created`, `interviewing`, `requirement-proposed`, `requirement-approved`, `redmine-synchronized`, and `completed`; `paused` is a temporary state, not a completed phase. `completed_phases` is always a contiguous prefix, while `phase` names its first incomplete phase. Persist state atomically after every decision, answer, pause, phase, remote attempt, observation, divergence decision, or completed operation. A later operation or phase cannot start until the previous completion is durable.

Resolve the installed `project-flow` package directory. Validate a new state with `python <project-flow-skill>/scripts/validate_state.py <feature-or-bug-state.json>`. Before replacing an existing state, write the candidate in `.work/` and run `python <project-flow-skill>/scripts/validate_state.py <candidate.json> --previous <feature-or-bug-state.json>`; replace atomically only after success. The comparison refuses deleted or rewritten history, invalid pause/resume, backward or skipped phases, mismatched identities, unsafe unknown-outcome transitions, duplicate relation keys, rewritten attempts or observations, unresolved requirement divergences, and unsanitized error material. Unknown schema versions, malformed JSON, mismatched issue IDs, and completion without create, publish, and planned relations also block progress. Both `new-issue` items and items started by `new-scope` use this validator and contract. The state validators are local and deterministic; they neither call Redmine nor read credentials. They validate workflow metadata, not semantic requirement completeness or correspondence between canonical prose and a published description. Run the separate publication check defined in [the projection contract](redmine-publication.md) before completing an item or scope.

Read [pause and resume](pause-resume.md) when an incomplete state, stop request, deferred decision, third-party question, or lock conflict appears.

**Complete when:** every required file exists in its phase-appropriate directory, every normalized source hash matches, no source or evidence reconciliation is pending, and the validator accepts the state without warning.
