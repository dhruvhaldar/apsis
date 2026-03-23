# Palette's Journal - Critical Learnings

## 2024-05-27 - Accessible Grouped Inputs
**Learning:** When multiple inputs share a single conceptual visual label (e.g., minimum and maximum bounds for a single parameter), using a standard `<label>` tag creates ambiguous or broken associations for screen readers. They don't map cleanly to multiple inputs.
**Action:** Always wrap grouped inputs in a `<fieldset>` with a `<legend>` replacing the generic visual label, and provide specific `aria-label` attributes to the individual inner inputs to describe their specific roles within the group.