---
name: project-flow
description: Turn readable conversation, file, URL, image, or design evidence into an approved Feature/Bug catalog or canonical requirements with recoverable Redmine projections. Use for new-scope and new-issue work, including multi-item scope completion, safe pause, resume, catalog revision, relations, and partial-failure reconciliation; this flow does not edit an existing issue as a new demand.
---

# Project Flow

Respond in Brazilian Portuguese (pt-BR) from the first announcement, including questions, progress, preflight diagnostics, approval previews, final summaries, and authored requirements in local artifacts and Redmine. Preserve technical identifiers, schema keys, commands, and quoted source text. Apply this language choice when invoking the supporting disciplines unless the user explicitly requests another language.

Deliver approved requirements: `new-scope` discovers an ordered Feature/Bug catalog and completes every item in that order; `new-issue` handles one Feature or Bug. The local Markdown is canonical; Redmine is its human-readable operational projection. Product decisions belong to the user, and implementation decisions belong to later roles.

## Preflight before intake

Treat the user's demand text as opaque until this phase passes. Create no file and do not interpret, summarize, classify, search for, or quote the demand yet.

1. Discover the Redmine tools available in this session, using the host's tool discovery/search when tools are deferred. Match exposed names and schemas to the capabilities below; host namespace prefixes may differ. Confirm that the connected Redmine MCP exposes `redmine_get_context`, `redmine_list_projects`, `redmine_get_project`, `redmine_list_trackers`, `redmine_list_statuses`, `redmine_list_categories`, `redmine_search_issues`, `redmine_get_issue`, `redmine_create_issue`, `redmine_update_issue`, and `redmine_create_relation`. A connected status or tool count alone does not establish which capabilities exist; an initially hidden tool does not establish absence. If discovery is incomplete or a check fails, read [Redmine preflight diagnostics](references/redmine-preflight.md) before reporting a blocker.
2. Call `redmine_get_context`. A successful response must identify the server and authenticated user without exposing credentials.
3. Call the read-only project, tracker, and status list tools to prove access. Do not probe write tools by mutating Redmine.

If a required capability remains unavailable, authentication fails, identity is missing, or a read fails, stop before intake and report the observed failure and its evidence-based corrective action using the diagnostic reference. Distinguish a connected server missing a capability from an unconfigured server. The valid outcome is failure before intake: no demand content processed and no artifact written.

**Complete when:** every mandatory tool is present, the authenticated identity is known, and the three read probes succeeded without reading or displaying a credential.

## Select the context

Present the projects returned by Redmine and require an explicit project selection. Read that project and its categories. Retain the available trackers for classification, map the initial/approved statuses, and require confirmation when a needed mapping is not a literal equivalent. Ask the user to confirm the authenticated identity for approval attribution.

**Complete when:** project and identity are explicitly confirmed, categories are available, and any non-literal tracker/status mapping is confirmed.

## Recover or start

After preflight and before reading new intake, look for incomplete Project Flow state under `docs/harness/.runs/`, `docs/harness/features/`, and `docs/harness/bugs/`. If one matches the requested item, read [pause and resume](references/pause-resume.md), validate it, acquire its item lock, and offer to resume it. Never interpret demand text or create an artifact before preflight merely to decide whether a run matches.

For a fresh run, derive a stable item key from the confirmed project and intended artifact identity, then acquire the lock before the first write. Runs for different keys remain independent. A conflicting live lock stops this run with its non-secret owner and acquisition time; recovery requires the explicit abandoned-lock procedure in the pause reference.

**Complete when:** exactly one valid run is selected or initialized, its schema is recognized, and this execution owns the item lock.

## Run the selected path

Now read [the source intake contract](references/intake.md) and [the artifact contract](references/artifact-contract.md) before the first local write. For `new-scope`, read [the new-scope workflow](references/new-scope.md); for `new-issue`, read [the shared item workflow](references/new-issue.md). Both paths route the selected item through that same shared Feature or Bug cycle. Read [the design contract](references/design-inputs.md) only when an input is presented as a design or design evidence. Read [the Redmine projection contract](references/redmine-publication.md) before preparing either remote write.

Invoke `requirements-grilling` for a `new-issue` interview. For `new-scope`, follow the catalog-first interview gate in `references/new-scope.md`: build and approve the complete vertical catalog, create and persist the selected issue, and only then invoke `requirements-grilling` for that one item. Invoke `domain-modeling` only if the item interview resolves a reusable canonical term or exposes a genuine architecture candidate under that skill's triggers. Do not invoke it merely because a requirement uses domain language.

**Complete when:** `new-issue` validates at `completed`; or `new-scope` validates at `completed` with every active item completed in approved order, every relation and remote operation reconciled, every approval and validation recorded, no open functional gap or undecided candidate, and a final summary. After each scope item, the user explicitly chooses to continue or stop; either choice is durable and preserves the catalog and progress.

## Boundaries

This flow never edits an existing issue found by similarity search or creates categories. It never creates commits, technical tasks, architecture decisions, or extra issues automatically. Closing, canceling, relating, or otherwise mutating Redmine always consumes an explicit recorded approval; a retry may reuse an approval only when its payload fingerprint is unchanged.
