# Redmine projection contract

Group issue creation and final publication behind two meaningful previews and explicit confirmations. Approved relations may share the final preview; closing, canceling, or any other mutation requires its own explicit preview and approval.

## Creation preview

Show project, tracker, title, complete initial objective, confirmed category (or none), initial status, and the fact that one issue will be created. The initial description must already explain the Feature's observable goal or the Bug's observed deviation and include the managed delimiters:

```markdown
<!-- project-flow:start -->
<initial human-readable objective and collection status>
<!-- project-flow:end -->
```

One approval authorizes retries only for that exact payload fingerprint. Persist the approval before the first call. It does not authorize later publication.

### Feature Sequencing

For every new Feature, resolve the `Sequencing` issue custom field from the selected project's `issue_custom_fields` returned by `redmine_get_project`. Use the returned field ID and available format/allowed-value metadata; IDs are instance-specific. If the field is missing, ambiguous, or incompatible with the intended value, report the observed metadata and resolve the mapping before creation. A non-literal field name requires user confirmation.

For `new-scope`, use the item's approved `suggested_position` in `suggested_order` as its sequence, including when the catalog contains Bugs between Features. Preserve the catalog position instead of numbering Features separately.

For a standalone `new-issue` Feature, always calculate the next sequence from Redmine during creation preparation. Use `redmine_search_issues` for the confirmed project with `status_id: "*"`, following `offset`/`limit` through all result pages, and read Sequencing by its resolved custom-field ID. Include closed issues and every tracker using that field; retain only issues belonging to the confirmed project. Use `redmine_get_issue` when search results omit custom-field values. Set the new value to the largest existing numeric sequence plus one: a maximum of `35` yields `36`, even if earlier numbers are unused. If no issue has a sequence, start at `1`. Treat blank values as unset; an unreadable page or a nonblank invalid sequence must be resolved before calculating the maximum. Calculate automatically rather than asking the user to supply a number or accepting an arbitrary supplied value. Show the observed maximum and calculated next value in the creation preview; the existing exact-payload approval still applies.

Show the resolved field name, ID, value, and source of the sequence in the creation preview. Include it in `redmine_create_issue.attributes.custom_fields` as `{"id": <resolved-field-id>, "value": "<approved-sequence>"}`, alongside any other required custom fields. The creation approval and payload fingerprint cover this value. Bugs retain their existing creation behavior.

Persist the returned issue ID and create outcome immediately, then reread the issue with `redmine_get_issue` and verify the custom field by ID against the approved sequence before starting the interview. On an unknown create outcome, include Sequencing in the candidate comparison. A missing or different value is a divergence to resolve on that existing issue, never a reason to create another issue. Retries and resumed runs retain the original approved payload; a later catalog reorder does not automatically renumber created issues or change an approved retry. Final description publication preserves Sequencing.

**Complete when:** the creation preview and approved payload include the resolved Sequencing field and value, and readback confirms that value on the persisted Feature issue.

## Final publication preview

Reread the issue. Require exactly one ordered delimiter pair. Replace only content inside the delimiters and preserve byte-for-byte content before and after them; absent, nested, duplicated, or reversed delimiters block publication rather than replacing the whole description.

Compare the managed section with the last successfully persisted managed fingerprint. Classify changes outside it as preserved human content. Present changes inside it as requirement divergences with the old, remote, and canonical meanings. `pending` blocks publication. `accepted` first updates and reapproves the canonical document; `rejected` records the attributed decision and restores the approved projection. Never treat a remote edit as canonical merely because it is newer.

The managed section must stand alone for a reader without the interview or local artifact access. Generate it from the approved canonical document with `scripts/render_publication.py`. Preserve the section order and functional wording, including every story, flow, exception, rule, observable datum, acceptance/correction criterion, dependency and scope boundary. Preserve existing rule and criterion identifiers and references; one criterion in the canonical document remains one criterion in Redmine. The issue subject carries the canonical title, so the description does not repeat its H1 or local Issue/version metadata.

For Features, only the `Designs e evidências` provenance section stays local. Any condition needed to implement or accept the delivery must already appear in the functional sections before canonical approval; a local evidence pointer cannot substitute for it. For Bugs, retain evidence and reproduction limitations because they define the deviation. Append the repository-relative canonical path and approval attribution. Interview history and operational state remain local.

Use the storage and retention policy in [the artifact contract](artifact-contract.md): unapproved output belongs in `.work/`; exact evidence required by an approved operation belongs in its `.flow/publications/<operation-uuid>/` directory before approval. Use a sanitized fresh issue snapshot with `subject`, `description`, status and relations, either at the JSON root or inside `issue`. Identity may be `id` or `issue_id`; all identity fields present must agree. From the repository root:

```sh
python <project-flow-skill>/scripts/render_publication.py <feature-or-bug-state.json> --before <issue-before.json> --output <publish-preview.md> --payload <publish-payload.json>
python <project-flow-skill>/scripts/render_publication.py <feature-or-bug-state.json> --before <issue-before.json> --check <issue-after.json>
```

The generator requires a valid canonical approval matching the document bytes and the same issue identity/title. It emits only `issue_id` and `changes.description`, preserving content outside the delimiters. Its printed SHA-256 covers the exact UTF-8 payload file; use that fingerprint for publication approval. Keep status and relations unchanged. The checker compares all functional sections, permits CRLF/LF differences and equivalent canonical-reference footer wording, and separately verifies unmanaged content, status and relations. Review semantic completeness before approval; this check proves faithful publication, not requirement quality.

Present the generated preview unchanged. After the approved write, persist the operation outcome first, then reread and run the checker alongside fingerprint reconciliation. A mismatched projection remains incomplete until reconciled. A state validator passing alone does not establish publication completeness.

Show the complete resulting description, summarize preserved human content and resolved divergences, and list the stable keys of approved relations. The `redmine_update_issue` publication payload contains only the issue identifier and resulting description: omit `status_id` entirely, including the current or initial status. This preserves status changes made by others since creation or the last read. Requirement approval, publication approval, and local `approved` or `completed` milestones do not authorize a Redmine status transition. One publication approval authorizes retries of that exact payload and those exact relations. Do not publish round-by-round comments.

Keep legacy `approved_status_id`, `approved_status_name`, and `approved-status` mapping confirmations as historical data only. They never supply a publication field or authorize a transition. On resume, inspect any approved publication payload before retrying; if it contains a status field or its original fields cannot be established, pause publication and report that the recorded operation needs recovery. Preserve its fingerprint and history: the current state contract does not support replacing an approved operation's payload. Reconcile unknown outcomes before resolving recovery. A completed publication is not repeated or automatically reversed. Any user-requested status change, including repair of an earlier unintended change, is a separate action with its own exact transition preview and explicit approval.

For a scope dependency, use the native `blocks` relation from the prerequisite issue to the dependent issue. Plan its stable key with catalog item IDs; as soon as both Redmine IDs exist, resolve the IDs, preview the exact relation, persist approval and fingerprint, call `redmine_create_relation`, then reread and reconcile before starting another item. A catalog split or merge preserves existing relations and issues until a separately approved remote mutation changes them.

## Reconciliation loop

Before any remote call, verify the item lock, validate state, and persist the approved operation with its payload fingerprint. After the call, persist its outcome before starting another operation. On resume, reread issue plus relations and compare them with local fingerprints in operation order: create, publish, then stable-sorted relations. Continue from the first incomplete operation only.

A known failure records a new attempt with a stable error code and sanitized human message; it retains no credentials, headers, request bodies, session paths, raw response bodies, or raw exceptions. An unknown outcome always triggers a read comparison. Remote match completes locally without a repeated mutation; proven absence allows the unchanged operation to retry; divergence or ambiguity stops with safe choices and no mutation.

## Aligning an already completed publication

When the user requests publication standardization for an issue created by this flow, retain its completed state, approvals, operations and scope closure as history. Acquire the same item lock and create `.flow/publications/<uuid>/publication-alignment-<uuid>.json` for each new alignment, retaining its baseline, preview, payload and readback in that same operation directory. All file references are relative to the item root (for example `.flow/feature-state.json`, `feature.md`, and `.flow/publications/<uuid>/baseline.json`); a legacy canonical state may remain at `feature-state.json`. Use schema v2 from `schemas/publication-alignment.schema.json`; never reuse an alignment file for a later canonical or remote baseline.

The record keeps issue identity; completed canonical state, document hash and approval; lock acquisition/release; sanitized fresh baseline with status and relations; exact preview and payload paths/hashes; payload approval; append-only attempts and observations; and verified readback. Its append-only status history is `pending → approved → unknown|completed`, with `unknown → completed` after reconciliation. Validate every candidate against its predecessor during operation. Place the candidate at `.work/publications/<uuid>/publication-alignment-<uuid>.json`, so its filename retains the alignment identity and its references resolve from the same item root. On success replace the current record atomically and remove the candidate:

```sh
python <project-flow-skill>/scripts/validate_publication_alignment.py <candidate.json> --previous <publication-alignment-uuid.json>
```

Obtain approval for the concrete generated payload before the first mutation. An unknown outcome is reconciled by readback; retry only after the remote absence of that exact payload is proven, and reuse its unchanged fingerprint. `completed` requires the approved payload to match the readback, every functional section to pass, unmanaged content/status/relations to remain unchanged, and the lock release to be recorded after verified completion. A completed record is immutable.

Legacy `publication-alignment.json` schema v1 records remain valid in read-only mode. Never append transitions to them; a later alignment gets a new UUID-named v2 record. A canonical content change is not an alignment: it requires its own requirement review and approval before a new alignment begins. Historical closure records and unrelated demands remain intact.

## Abandonment after creation

Offer four explicit outcomes: keep the issue in collection and keep local state; request a preview to set an available canceled state; request a preview to update only the managed description; or abandon only local state while leaving Redmine unchanged. Explain the retained artifacts and resumability of each. Closing, canceling, updating, or releasing state in a way that prevents resume occurs only after the user selects the exact effect and approves its payload; otherwise the remote issue remains open and unchanged.

**Complete when:** each mutation matches an approved fingerprint, every completed operation was persisted before the next began, relations are unique by stable key, divergences are resolved, no unmanaged content was changed, and the publication payload contains no status field.
