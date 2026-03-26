# Palette's Journal - Critical Learnings

## 2024-05-27 - Accessible Grouped Inputs
**Learning:** When multiple inputs share a single conceptual visual label (e.g., minimum and maximum bounds for a single parameter), using a standard `<label>` tag creates ambiguous or broken associations for screen readers. They don't map cleanly to multiple inputs.
**Action:** Always wrap grouped inputs in a `<fieldset>` with a `<legend>` replacing the generic visual label, and provide specific `aria-label` attributes to the individual inner inputs to describe their specific roles within the group.

## 2024-05-28 - Heavy Computation Feedback
**Learning:** For heavy, blocking numerical solvers on the backend, lack of visual feedback and disabled states leads to user confusion and duplicate requests. Screen readers also need explicit context during these async operations.
**Action:** Always set action buttons to `disabled=true`, switch text to a loading state, and set `aria-busy="true"` immediately upon starting the fetch, resetting in the `finally` block. Combine with CSS pseudo-class `:disabled` for visual cues like reduced opacity and `not-allowed` cursor.

## 2024-06-03 - Button Focus Visibility
**Learning:** Setting `outline: none` on interactive elements like buttons removes the browser's default focus ring, making keyboard navigation completely invisible and breaking accessibility for users who don't use a mouse.
**Action:** Always pair `outline: none` with a `:focus-visible` pseudo-class that explicitly defines a clear, high-contrast outline (e.g., using `--accent-color` and `outline-offset`) so keyboard users can see which element currently has focus.

## 2024-06-04 - Screen Reader Feedback on Output vs Charts
**Learning:** Adding `aria-live="polite"` is excellent for simple text updates (like a newly calculated array) because the screen reader announces the change concisely. However, applying `aria-live` to a complex chart container (like Plotly or Chart.js) causes screen readers to be overwhelmed by hundreds of DOM node insertions (SVG paths, labels, etc.), rendering the page unusable.
**Action:** Use `aria-live` for focused text outputs. For chart containers, prefer using helpful empty state placeholders before computation so users know what will appear, and rely on the button's loading state rather than a live region to indicate chart updates.