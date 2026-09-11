# Organizing existing artifacts

Use this branch for an explicitly requested cleanup or migration of existing Project Flow directories. The storage policy lives in [the artifact contract](artifact-contract.md). Existing runs remain readable in place; organizing their files is a local filesystem operation and does not authorize a Redmine mutation.

## Review

Run the read-only inventory from the repository root:

```sh
python <project-flow-skill>/scripts/manage_artifacts.py review . docs/harness/features/<REDMINE-ID>-<slug>
```

It prints paths, hashes, candidate history moves and destination conflicts without writing a report file. Use the matching bug/scope path when applicable. The inventory is a review aid: it does not prove that a file is disposable or execute any migration.

Inspect references from states, sources, Markdown links, catalog progress, approvals, publication alignments and legacy snapshots. Check tracked files with Git. Classify each proposed change as a move, a proven disposable file, or retained history. Show exact source/destination paths, dependent reference edits, conflicts and tracked-file removals in the preview. Keep unknown files and evidence for incomplete or unknown-outcome operations.

**Complete when:** every proposed change has a known owner and dependencies, and the user can review the exact effect without reading a generated report alongside their requirements.

## Apply an authorized organization

Use the existing scope/item lock for live state changes. Stage the entire organization, including the path map and installed helpers, validate it, then apply the filesystem changes with rollback on failure. Keep only the canonical document in each item/scope root. Put operational state in `.flow/`, publication evidence in `.flow/publications/<operation-uuid>/`, retained reviews in `.flow/reviews/`, old state snapshots in `.flow/legacy/`, and interview/deferred-question/final-summary history in `history/`. Sources keep their existing location. Retained JSON, payloads and publication previews keep their exact bytes.

Historical references are not a reason to leave files in the root. Record their repository-relative old-to-new paths in `docs/harness/.flow/artifact-layout.json`, following `schemas/artifact-layout.schema.json`. The `moves` object maps each old path directly to its current destination, including earlier aliases when applicable; no chains, duplicate copies at old paths, temporary targets or links outside `docs/harness/`. Keep IDs, approval hashes, decisions and recorded state paths unchanged. Validators resolve old paths through this map. To locate a path recorded in history, use:

```sh
python <project-flow-skill>/scripts/manage_artifacts.py locate . docs/harness/features/<id>-<slug>/feature-state.json
```

For human Markdown that needs new link destinations, preserve its exact pre-migration bytes under `docs/harness/.flow/originals/<sha256>.md` and add a `documents` entry with `path`, `original_path`, `original_snapshot`, `original_sha256` and `relocated_sha256`. Produce the reading copy exclusively with `artifact_layout.rewrite_links`; it changes destinations, not labels, requirement prose or decisions. A layout record is not an approval. `approved_document(path, approved_hash)` verifies the original snapshot against the existing approval and proves that the reading copy is exactly the mechanical link rewrite. Renderers and publication checks continue using those exact approved bytes. A substantive edit fails this check and follows ordinary requirement review. Exact remote payloads/previews remain unchanged, even when their historical links describe the old layout.

On a later organization, compose previous aliases directly to the final destinations and preserve the earliest approved snapshots. Recompute reading copies from those originals rather than rewriting or relabeling approval history. A later actual requirement approval can hash the current document normally.

Check Git attributes before staging: automatic line-ending conversion can invalidate existing hashes even when working-tree bytes are preserved. Use scoped `-text` attributes for retained Markdown/JSON evidence and reading copies when necessary, preserving unrelated attributes. Compare staged blob bytes with the validated working-tree files so a fresh checkout retains the same approvals and migration checks.

Remove only individually reviewed disposable files. A Git ignore rule does not untrack an existing file: include any index removal in the reviewed change and use exact paths, preserving unrelated staging. Do not rewrite Git history. Revalidate links, source hashes, publication evidence and resume behavior after the move; keep the original usable layout if validation fails.

**Complete when:** each item/scope root contains only its canonical document; the path map locates historical references; every changed reading copy verifies against its original; legacy/current states and completed publication checks pass; and the same issue can resume without another creation or publication. Temporary files are ignored and absent from the Git index, while every file required for recovery is versioned.
