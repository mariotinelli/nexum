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

## Final publication preview

Reread the issue. Require exactly one ordered delimiter pair. Replace only content inside the delimiters and preserve byte-for-byte content before and after them; absent, nested, duplicated, or reversed delimiters block publication rather than replacing the whole description.

Compare the managed section with the last successfully persisted managed fingerprint. Classify changes outside it as preserved human content. Present changes inside it as requirement divergences with the old, remote, and canonical meanings. `pending` blocks publication. `accepted` first updates and reapproves the canonical document; `rejected` records the attributed decision and restores the approved projection. Never treat a remote edit as canonical merely because it is newer.

The managed section must stand alone for a reader without the interview or local artifact access. Generate it from the approved canonical document with `scripts/render_publication.py`. Preserve the section order and functional wording, including every story, flow, exception, rule, observable datum, acceptance/correction criterion, dependency and scope boundary. Preserve existing rule and criterion identifiers and references; one criterion in the canonical document remains one criterion in Redmine. The issue subject carries the canonical title, so the description does not repeat its H1 or local Issue/version metadata.

For Features, only the `Designs e evidências` provenance section stays local. Any condition needed to implement or accept the delivery must already appear in the functional sections before canonical approval; a local evidence pointer cannot substitute for it. For Bugs, retain evidence and reproduction limitations because they define the deviation. Append the repository-relative canonical path and approval attribution. Interview history and operational state remain local.

Use a sanitized fresh issue snapshot with `id`, `subject` and `description` (either at the JSON root or inside `issue`). From the repository root:

```sh
python <project-flow-skill>/scripts/render_publication.py <feature-or-bug-state.json> --before <issue-before.json> --output <publish-preview.md> --payload <publish-payload.json>
python <project-flow-skill>/scripts/render_publication.py <feature-or-bug-state.json> --before <issue-before.json> --check <issue-after.json>
```

The generator requires a valid canonical approval matching the document bytes and the same issue identity/title. It emits only the description update and preserves content outside the delimiters. Its printed SHA-256 covers the exact UTF-8 payload file; use that fingerprint for publication approval. Keep status and other fields unchanged unless a separate explicit instruction authorizes them. The checker compares all functional sections, permits CRLF/LF differences and equivalent canonical-reference footer wording, and verifies unmanaged content separately. Review semantic completeness before approval; this check proves faithful publication, not requirement quality.

Present the generated preview unchanged. After the approved write, persist the operation outcome first, then reread and run the checker alongside status, relations and fingerprint reconciliation. A mismatched projection remains incomplete until reconciled. A state validator passing alone does not establish publication completeness.

Show the complete resulting description, summarize preserved human content and resolved divergences, and list the stable keys of approved relations. One approval authorizes retries of the exact `redmine_update_issue` payload and those exact relations. Do not publish round-by-round comments.

For a scope dependency, use the native `blocks` relation from the prerequisite issue to the dependent issue. Plan its stable key with catalog item IDs; as soon as both Redmine IDs exist, resolve the IDs, preview the exact relation, persist approval and fingerprint, call `redmine_create_relation`, then reread and reconcile before starting another item. A catalog split or merge preserves existing relations and issues until a separately approved remote mutation changes them.

## Reconciliation loop

Before any remote call, verify the item lock, validate state, and persist the approved operation with its payload fingerprint. After the call, persist its outcome before starting another operation. On resume, reread issue plus relations and compare them with local fingerprints in operation order: create, publish, then stable-sorted relations. Continue from the first incomplete operation only.

A known failure records a new attempt with a stable error code and sanitized human message; it retains no credentials, headers, request bodies, session paths, raw response bodies, or raw exceptions. An unknown outcome always triggers a read comparison. Remote match completes locally without a repeated mutation; proven absence allows the unchanged operation to retry; divergence or ambiguity stops with safe choices and no mutation.

## Aligning an already completed publication

When the user requests publication standardization for an issue created by this flow, retain its completed state, approvals, operations and scope closure as history. Prepare a separate alignment record beside the existing artifacts with the canonical approval/hash, fresh remote baseline, complete generated preview, exact payload fingerprint and preservation review. Acquire the same item lock before writing that record or publishing. Obtain approval for the concrete replacement; preserve completed operation records and record the new attempt, immediate response outcome and checked readback in the alignment record. Unknown outcomes use the reconciliation loop above. On later reconciliation, use the latest successful publication or alignment observation as the remote baseline while preserving earlier records. Release the lock after verified completion.

This branch changes only the projection of an unchanged approved requirement. A canonical content change requires its own requirement review and approval; unrelated existing demands remain outside this flow. Historical closure records remain intact, with the later alignment linked from the new record. Older completed runs remain readable; checking them may reveal alignment work but never silently rewrites or republishes them.

## Abandonment after creation

Offer four explicit outcomes: keep the issue in collection and keep local state; request a preview to set an available canceled state; request a preview to update only the managed description; or abandon only local state while leaving Redmine unchanged. Explain the retained artifacts and resumability of each. Closing, canceling, updating, or releasing state in a way that prevents resume occurs only after the user selects the exact effect and approves its payload; otherwise the remote issue remains open and unchanged.

**Complete when:** each mutation matches an approved fingerprint, every completed operation was persisted before the next began, relations are unique by stable key, divergences are resolved, and no unmanaged content was changed.
