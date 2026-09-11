# Feature interview and document contract

Use this branch only after the shared workflow confirms `Feature` and the run lock is held. On resume, keep every valid decision, answer, approval, source reconciliation, and completed remote operation, then continue at the state's first incomplete phase.

Interview for objective and success, actors and permissions, inputs and observable results, primary and alternate flows, states, validation and recovery, functional integrations, and scope boundaries. Follow `requirements-grilling`'s frontier and completion gate; implementation choices and non-functional requirements not explicit in the evidence remain outside the interview.

Draft `feature.md` from `templates/feature.md`. Its objective explains actor, need, observable change, value, and essential limits. Numbered user stories cover every confirmed functional behavior without an artificial limit. Cover main and alternate flows, rules, observable data, verifiable acceptance criteria, dependencies, evidence, and scope boundaries. Each criterion states a condition, action, and result and traces to a described flow or rule.

When late evidence exists, the shared workflow must reconcile its confirmed, contradicted, and reopened decisions before this contract can pass.

**Complete when:** every required Feature section is substantive, each confirmed functional behavior appears in the document, every criterion is independently observable, and no gap, contradiction, deferred question, or source reconciliation remains.
