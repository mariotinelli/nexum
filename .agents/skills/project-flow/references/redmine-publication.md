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

The managed section must be understandable without the interview and stand alone for a reader without local artifact access. For a Feature, include title, objective, expected result, actors, main flow, business rules, essential acceptance criteria, dependencies, scope boundaries, and the repository-relative canonical path to `feature.md`. For a Bug, include title, objective, impact, current and expected behavior, known reproduction steps or their explicit limitation, conditions, evidence, frequency, reach, essential correction criteria, scope boundaries, and the repository-relative canonical path to `bug.md`.

Show the complete resulting description, summarize preserved human content and resolved divergences, and list the stable keys of approved relations. One approval authorizes retries of the exact `redmine_update_issue` payload, the confirmed approved-status mapping, and those exact relations. Do not publish round-by-round comments.

For a scope dependency, use the native `blocks` relation from the prerequisite issue to the dependent issue. Plan its stable key with catalog item IDs; as soon as both Redmine IDs exist, resolve the IDs, preview the exact relation, persist approval and fingerprint, call `redmine_create_relation`, then reread and reconcile before starting another item. A catalog split or merge preserves existing relations and issues until a separately approved remote mutation changes them.

## Reconciliation loop

Before any remote call, verify the item lock, validate state, and persist the approved operation with its payload fingerprint. After the call, persist its outcome before starting another operation. On resume, reread issue plus relations and compare them with local fingerprints in operation order: create, publish, then stable-sorted relations. Continue from the first incomplete operation only.

A known failure records a new attempt with a stable error code and sanitized human message; it retains no credentials, headers, request bodies, session paths, raw response bodies, or raw exceptions. An unknown outcome always triggers a read comparison. Remote match completes locally without a repeated mutation; proven absence allows the unchanged operation to retry; divergence or ambiguity stops with safe choices and no mutation.

## Abandonment after creation

Offer four explicit outcomes: keep the issue in collection and keep local state; request a preview to set an available canceled state; request a preview to update only the managed description; or abandon only local state while leaving Redmine unchanged. Explain the retained artifacts and resumability of each. Closing, canceling, updating, or releasing state in a way that prevents resume occurs only after the user selects the exact effect and approves its payload; otherwise the remote issue remains open and unchanged.

**Complete when:** each mutation matches an approved fingerprint, every completed operation was persisted before the next began, relations are unique by stable key, divergences are resolved, and no unmanaged content was changed.
