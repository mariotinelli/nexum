# New scope: complete an approved catalog

Use this path after preflight and explicit selection of `new-scope`. Read [catalog discipline](catalog-discipline.md) before delimiting the catalog. Orchestration stays here; each item uses the reusable discipline in `new-issue.md` and its Feature or Bug branch.

## 1. Normalize and orient once

Follow `intake.md` for every declared source and `design-inputs.md` for design evidence. Create `docs/harness/scopes/<YYYY-MM-DD>-<scope-slug>/`, using deterministic suffixes `-02`, `-03`, and so on for collisions, and acquire a scope lock before its first write. Inspect the repository once and retain the result in scope state.

Allocate each normalized source once. A source supporting two or more items is `scope-shared`, stays under the scope, and is referenced from item states by a relative path. A source supporting exactly one item is `item-exclusive`, moves to that item's `sources/` directory when its issue is created, and is referenced from the scope allocation record; never retain a second copy. If discovery yields one item, preserve the scope artifacts and continue directly without restarting preflight, intake, normalization, orientation, or conversation.

**Complete when:** every retained source is readable, normalized once, and has exactly one ownership/path allocation; repository orientation is recorded without secrets; the scope owns its lock; and every observed candidate is represented.

## 2. Build and approve the complete catalog

Account for every observable objective or deviation with a stable candidate record. Mark unresolved classification or allocation as `undecided`; it blocks catalog approval and item work. Each catalog item records its candidate IDs, stable ID, Feature/Bug type, name, complete human objective, actors, observable result or deviation, evidence, direct functional dependencies, separate-acceptance rationale, lifecycle, status, and deterministic position.

Apply a **catalog-first gate** after repository orientation. Turn the evidence into candidate vertical items before starting an exhaustive functional interview. When a catalog field cannot be determined, ask only the smallest product question whose answer can change candidate inclusion, Feature/Bug classification, item boundary, direct dependency, source allocation, or processing order. Then recompute and present the catalog. Preserve every other behavioral uncertainty as input for the future owning item; it does not trigger `requirements-grilling`, a numbered item interview, or a decision ledger in `scope.md` during `repository-analyzed`, `catalog-proposed`, or `catalog-approved`.

Apply the capability cohesion, title convention, behavioral coverage and delivery-dependency criteria in the shared discipline. Build `input_inventory`, `behaviors`, `title_convention`, item `delivery`, `dependency_reasons` and `order_reasons` in scope v3. Keep candidate and physical source allocation records separate from behavior responsibility. Scope-only contextual/excluded sources use `scope-context` with no item IDs.

Generate the complete catalog/coverage block and approval preview with `render_catalog.py`. Reconcile the preview against every normalized source before seeking approval; the validator cannot discover behavior omitted from both the evidence inventory and catalog. Use the resulting hash for the attributed approval, then rerun validation before creating any issue.

**Complete when:** every relevant reference is resolved; every behavior has a verifiable destination; every active item has a cohesive boundary and confirmed title; the graph and order are justified and valid; the full generated projection is approved; and no item-level functional interview has started.

## 3. Process the first incomplete item

Select the first active item in approved order whose status is not `completed`; all preceding items and direct dependencies must be completed. An open functional gap anywhere earlier blocks this item and every later flow. Existing runs retain their schema. For an explicit legacy review, follow the enrichment and preservation contract in `artifact-contract.md` before resuming.

Initialize requirement state v4 with `mode: new-scope`, `scope_item` (relative `state_path`, `catalog_item_id`, approved `catalog_sha256`), and relative evidence links. Copy the confirmed `title_convention` and item `delivery` exactly; inherit classification, audiences and boundaries without repeating catalog questions. Run `new-issue.md` from classification/novelty confirmation through category and creation preview. Create exactly one issue only after preview approval and immediately before the first interview round; move item-exclusive sources once, create the definitive artifacts, and update scope progress atomically.

The **item-interview gate** opens only when `catalog-approved` is in the scope's completed phase prefix and the selected item's completed create operation, issue ID, definitive artifact path, and requirement state are durable. Invoke `requirements-grilling` for that selected item only. If any precondition is absent, resume the first incomplete catalog or creation step instead of asking item-level functional questions.

Execute the complete shared Feature/Bug cycle. If the interview exposes an unresolved functional gap, record it in both histories, mark the item `blocked`, pause with an objective resolution condition, and run no later item or downstream flow. Complete the item only when its requirement state validates at `completed`, its Redmine projection and operations reconcile, and every gap is resolved.

As soon as both endpoint issue IDs exist for a planned relation, preview and obtain explicit approval for its stable key, publish the native Redmine `blocks` relation, and reconcile its outcome before another item starts. Never duplicate an equivalent relation.

**Complete when:** exactly the first incomplete item is completed and validated, its issue and artifact links are durable, all now-addressable relations are published and reconciled, and no open gap exists.

## 4. Continue or stop

After each completed item, show current issues, relations, catalog progress, remaining order, and blockers. Ask the user to choose `continue` or `stop`; after the final item offer `finish` or `stop`. Persist the attributed decision before acting.

`continue` returns to step 3. `stop` appends a `voluntary-stop` pause with the first incomplete item and objective resume condition, preserving the entire catalog, item progress, issues, relations, approvals, sources, and histories. Resume reruns preflight and reconciliation, validates the scope and item states, then selects the same first incomplete active item in approved order.

**Complete when:** one decision follows the completed item; continuation has not skipped an item, or stopping has a valid resumable pause and no remote mutation follows it.

## 5. Reconcile and close the scope

After all active items complete, reread every issue and relation. Reconcile unknown outcomes and divergences in operation order. Validate every separate requirement state and the scope state. Build the final `scope.md` summary listing all issues, native relations, canonical artifacts, approvals, validations, and one actionable next recommendation. Present its exact projection and persist one attributed scope-completion approval.

The scope may reach `completed` only when every active item is completed, every retained/retired item preserves any existing issue and artifacts, every relation is published and reconciled, every required approval is valid, every validation passes, all candidates are decided, and no functional gap is open.

**Complete when:** `validate_scope_state.py` accepts phase `completed`, the final summary contains all six required sections, and no item, relation, approval, reconciliation, candidate, gap, or validation remains incomplete.

## Catalog revision

New evidence that changes names, audiences, deliveries, coverage, conventions, or divides, combines, adds, removes, retypes, reorders, or changes dependencies pauses the scope before mutation. Show its effect on names, audiences, deliveries, coverage, candidate mapping, source ownership, graph, order, issues, relations, and artifacts. Invalidate the prior catalog approval, append an approved `catalog_changes` record, retain retired entries and every created issue/artifact, update the active catalog, and obtain approval of the complete revised projection. A split or merge never closes, deletes, reuses, or rewrites an existing issue automatically; any later remote disposition is a separate previewed decision.

**Complete when:** history is append-only, every prior issue ID remains in item progress, the revised active graph/order/source allocation validate, and exactly one approval covers the current complete catalog.
