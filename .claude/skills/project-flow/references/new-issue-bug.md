# Bug interview and document contract

Use this branch only after the shared workflow confirms `Bug` and the run lock is held. On resume, keep every valid decision, answer, approval, source reconciliation, and completed remote operation, then continue at the state's first incomplete phase.

## Investigate the deviation

Interview across the current frontier until these facets are resolved:

- impact: who or what is affected and the observable consequence;
- current behavior: what happens now, stated without a presumed technical cause;
- expected behavior: what should happen under the same conditions and why;
- conditions: known environment, state, inputs, sequence, timing, or role boundaries;
- evidence: messages, logs already supplied, screenshots described in the text, measurements, or concrete observations;
- frequency: always, intermittent, one known occurrence, or unknown, with the basis for that statement;
- reach: affected actors, records, projects, environments, versions, or other known population boundaries.

Ask for known reproduction steps, but treat them as evidence rather than a universal approval gate. A Bug without deterministic reproduction may proceed only when the reproduction limitation is explicit and the combined symptom, expected behavior, impact, evidence, frequency, conditions, and reach make the deviation clear enough to verify a correction. A report such as "it sometimes fails" without those bounds remains a blocking gap.

Do not ask the user to diagnose a cause or choose a fix. Keep technical hypotheses out of the requirement.

**Complete when:** every facet is answered or explicitly bounded as unknown, the reproduction limitation is recorded when applicable, and the observed deviation remains specific and testable.

## Draft the Bug

Draft `bug.md` from `templates/bug.md`. User stories are not required. State the current and expected behavior under comparable conditions, preserve known evidence and uncertainty, and distinguish reach from frequency. Criteria of correction must be implementation-independent and observable; each states the condition or population, the action or event, and the externally visible corrected result. Add a criterion for a non-deterministic Bug that makes the agreed evidence window or sampling boundary explicit.

When late evidence exists, the shared workflow must reconcile its confirmed, contradicted, and reopened decisions before this contract can pass.

**Complete when:** every required Bug section is substantive or explicitly records a justified unknown, no user-story section was added merely for conformity, each correction criterion can be checked against the documented deviation, and no deferred question or source reconciliation remains.
