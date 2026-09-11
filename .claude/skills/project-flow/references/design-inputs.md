# Design evidence

Apply this contract when a source is presented as a design or is needed to settle a design-dependent behavior.

Accept a design only when it has a stable identifier or explicit name and the complete extraction identifies the screen or component, visible states, and observable behavior. Capture, when present, its human objective, fields, actions, visible text, navigation, observable validations, role variations, related screens, and explicitly named viewport or device.

A loose image without screen or component identification is visual evidence, not a design. It cannot establish design behavior. A named screen with no observable states or behavior is incomplete design evidence and blocks when the user declared it as a design or the Feature depends on it. Ask for identification or missing design material; otherwise require the user to remove the design claim explicitly.

Describe only what is visible or explicitly annotated. Keep ambiguous transitions, hidden states, permissions, responsive behavior, and missing screens as gaps. Do not infer layout rules, design tokens, styling systems, breakpoints, or implementation from pixels.

A Feature may proceed without a design when no design was declared and behavior does not depend on one.

**Complete when:** every retained design has identification, visible states, and observable behavior, and every absent or ambiguous behavior remains an explicit gap rather than an inferred rule.
