# Product capabilities, coverage and naming

Read this discipline when delimiting a `new-scope` catalog or identifying the delivery of a `new-issue`. The workflows own sequencing and remote approvals; this reference owns product boundaries and evidence reconciliation.

## Reconcile evidence and behavior

Record whether the request supplies a complete folder/package or selected files. Inventory all relevant material in a complete package, including its guide and cross-screen references. For selected files, list references outside the selection and ask whether to include or exclude each relevant target. Neighboring files alone do not expand the request. Retain contextual and explicitly excluded sources without inventing features for them.

Preserve actions, states, rules, navigation and audience differences during normalization. Label behavior as demonstrated, annotation or ambiguity; a static mockup does not prove working functionality. Give each behavior a stable ID and precise evidence locators. Assign one disposition: `covered` by exactly one responsible feature/bug, `existing-confirmed`, `excluded` by an attributed decision, or `pending`. Other items can consume a covered behavior. File ownership and behavior responsibility are separate: one source may support many items without assigning the same behavior to multiple owners.

Compare each behavior with repository evidence. Record absent, partial, existing or unknown implementation and the proposed change. Partial existence does not mean completion; a discrepancy does not establish a Bug without confirmed expected behavior. Existing coverage requires user confirmation and repository evidence; exclusions require a decision. Every behavioral source must have behaviors, but allocating all files alone never proves complete coverage. Re-read the normalized material against the inventory to find missed actions and states.

Ask catalog questions before approval when the answer changes coverage, boundaries, audience, dependencies or order. For example, if a dashboard displays hours but the origin of those hours is unspecified, resolve whether time entry/timing already exists or belongs in this catalog. Keep internal details of an already bounded capability for its later interview.

**Complete when:** all relevant evidence and references are reconciled; every behavior has a verifiable destination; no catalog-shaping question is pending.

## Delimit capabilities and compose titles

Evaluate cohesion across objective, operations, audience, surface and the unit the user will receive and accept. Consider creation, consultation, editing and lifecycle operations together. Cohesive operations may form `Gestão de Usuário` or `Gestão de Projeto`; `Minhas Tarefas` and `Painel Gerencial` are equally valid capabilities. Prefer recognizable nominal names without imposing “Gestão de”. Record what is included and why each boundary is useful. Split when there is a concrete product reason; sharing an entity or screen alone decides neither merging nor splitting. Resolve materially ambiguous boundaries with the user.

Confirm the project's title convention: available surfaces (`WEB`, `APP`), audience prefixes, shared/public screens and whether a single, aggregate or multiple audience prefix is used. An aggregate prefix represents the audience set the user defines; record that meaning in `shared_public_rule`. A common interface serving several roles is not automatically several features. WEB requires an audience, including a project-defined public/shared audience when appropriate. APP uses an audience when applicable and never `BACKOFFICE`. WEB and APP deliveries are separate items even if they share evidence.

Compose `delivery.title` mechanically from its surface, confirmed audience prefixes and name, for example `[WEB] [BACKOFFICE] Gestão de Usuário`. Apply the convention to Bugs too, retaining a defect description as the name. The flow creates only Features/Bugs, without child tasks or `[API]` titles. Store `visible_delivery`, `user_result`, `included` operations and `boundary_reason` in `delivery`; detailed requirements remain Markdown.

**Complete when:** the convention is confirmed and every item identifies a comprehensible capability or deviation with explicit included behavior and boundaries.

## Explain delivery, blockers and order

Describe what the user will see and accomplish for each item in concrete language. A blocking prerequisite is a capability still unavailable whose absence prevents completing the real delivery or its integrated acceptance. Required data, navigation and shared infrastructure are prompts to investigate, not automatic edges. Fixtures can enable concurrent development but do not establish independent delivery.

For every direct edge record the capability supplied by the prerequisite, why its absence blocks this delivery, and evidence or an attributed decision. Project only these edges to native `blocks` relations; remove cycles and transitive redundancies. Propose a total order based first on actual blockers, then confirmed priorities and the usage/lifecycle sequence. Stable ID is only a final tie-breaker; file order is not product priority. Record a reason and its basis for every position. Present graph groups as “sem bloqueios entre si no grafo”; this says nothing about technical parallelism.

**Complete when:** the user can explain each delivery, each blocking edge and each position, and the graph and total order validate.

## One complete approval projection

For scope v3, after `catalog-proposed` is completed, run:

```sh
python <project-flow-skill>/scripts/render_catalog.py <scope-state.json> --output <catalog-preview.md> --hash
python <project-flow-skill>/scripts/render_catalog.py <scope-state.json> --check <catalog-preview.md>
python <project-flow-skill>/scripts/render_catalog.py <scope-state.json> --scope-document <scope.md>
python <project-flow-skill>/scripts/render_catalog.py <scope-state.json> --check-scope <scope.md>
```

Use `.work/catalog-preview.md` for the unapproved preview and `.flow/scope-state.json` for a new scope state. Retain the approved catalog in `scope.md` with its approval hash in state; keep a separate preview only when a retained record requires its exact bytes. Reuse the temporary preview path after completing a review.

Start `scope.md` from its template; `--scope-document` atomically replaces its single marked block and preserves surrounding prose and progress. Present the entire preview, including coverage dispositions, convention, deliveries, dependency reasons and order. All active items appear exactly once in approved order with stable IDs and continuous numbering. For a long catalog, show consecutive identified parts (`parte 1/N`, etc.) preserving the original bytes and numbering when reassembled. A summary cannot replace the complete preview. Record the hash printed by the generator in the attributed `complete-catalog-and-order` approval, then validate again; validation recalculates the hash.

Changes to approved content invalidate its approval and require a complete revised preview. Normal interview progress is outside the projection. Record naming, audience, delivery and coverage impacts as well as graph, allocation and order impacts in catalog revision history. Recompute boundaries, dependencies and order after material decisions.

**Complete when:** the displayed complete preview and the generated `scope.md` block match, exactly one approval matches the recomputed hash, and all coverage and dependency gates pass.
