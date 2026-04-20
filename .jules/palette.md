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
**Action:** Use `aria-live` for focused text outputs. For chart containers, prefer using helpful empty state placeholders before computation so users know what will appear, and rely on the button's loading state rather than a live region to indicate chart updates.## 2026-03-27 - Enable Form Submission with Enter Key
**Learning:** Standalone inputs without enclosing `<form>` tags require users to click the button. Wrapping them natively enables the "Enter" key for submission, improving accessibility and efficiency for power users.
**Action:** Always wrap related input fields and their submission button in a `<form>` tag and use `onsubmit="event.preventDefault(); function()"` to handle the event without reloading the page.

## 2026-03-31 - Native Browser Validation
**Learning:** Using blocking `alert()` dialogs for form validation is disruptive to user flow and poorly supported by screen readers. Native validation using `setCustomValidity()` provides better accessibility, context, and a smoother user experience.
**Action:** Use native browser validation API (`el.setCustomValidity()` and `el.reportValidity()`) combined with CSS `:invalid` pseudo-class for immediate visual feedback, and use `el.focus()` to directly direct users to the error.

## 2024-05-18 - Input Focus Visibility
**Learning:** Using `outline: none` on inputs completely removes browser focus rings, leaving keyboard users without visual cues on where they are when navigating via Tab.
**Action:** Always pair `outline: none` with a custom `:focus-visible` pseudo-class (e.g., using a solid outline or box-shadow) to explicitly support keyboard navigation without affecting mouse users.

## 2024-05-18 - Decorative Emojis and Empty States
**Learning:** Decorative emojis in UI elements (like empty states) are read aloud by screen readers, creating noisy and unhelpful audio experiences (e.g., "musical note"). Additionally, inconsistent empty states across similar panels leave users uncertain about functionality.
**Action:** Always add `aria-hidden="true"` to purely decorative emojis. Ensure consistent empty state placeholders across all related UI panels to provide clear expectations before data is fetched or computed.

## 2026-04-01 - Input Semantics for Mathematical Data
**Learning:** Browsers aggressively apply spellchecking, autocorrect, and auto-capitalization to text inputs. On inputs expecting code, JSON, or mathematical arrays (like `[[0, 1]]`), this creates frustrating autocorrect behavior and visual noise (red squiggles).
**Action:** Always add `spellcheck="false" autocomplete="off" autocorrect="off" autocapitalize="none"` to the parent `<form>` (or individual inputs) when handling non-prose text data to disable aggressive browser text intelligence and provide a cleaner, code-editor-like UX.

## 2024-05-19 - Scalar Math Parameters and Form Validation
**Learning:** Using `type="text"` for scalar mathematical inputs (like time horizons or steps) in an otherwise array-heavy form prevents mobile browsers from natively opening the numeric keypad, making data entry cumbersome. Furthermore, relying entirely on JS parsing for validation can allow invalid states (like empty fields or negative time) to be submitted unnecessarily.
**Action:** Always use `type="number"` for scalar numerical inputs, and apply precise `min` and `step` attributes alongside the `required` attribute. This delegates immediate validation to the browser's native capabilities, prevents simple user errors before JS execution, and significantly improves mobile UX.

## 2024-04-06 - Structural Placeholders
**Learning:** Programmatic inputs expecting strict structures (like JSON arrays or matrices) lose their structural context when the input field is emptied by the user, leading to potential formatting errors.
**Action:** Always provide persistent `placeholder` attributes with clear examples alongside default values for programmatic inputs. This ensures the expected structural context remains visible when the field is empty, preventing user formatting errors.

## 2026-04-07 - Screen Reader Redundancy for Required Indicators
**Learning:** Adding a visual asterisk (*) to labels for required fields is helpful for sighted users, but if not hidden, screen readers will read "star" out loud. This is redundant and noisy if the underlying `<input>` already has the `required` attribute.
**Action:** Always wrap visual required indicators in `<span aria-hidden="true">*</span>` to keep the UI clean for screen reader users while maintaining visual cues.
## 2025-01-20 - Transform sections to landmarks in complex dashboards
**Learning:** Generic `<section>` tags do not automatically function as ARIA region landmarks for screen readers, meaning assistive tech users can't easily jump between major dashboard modules.
**Action:** Always provide an accessible name for `<section>` elements in complex layouts (e.g., using `aria-labelledby` referencing the section's `<h2>` heading) to elevate them to true, navigable region landmarks.

## 2024-05-19 - Actionable Outputs
**Learning:** Complex mathematical outputs (like synthesized matrices) generated by backend solvers are often needed for external tools (e.g., MATLAB, Python scripts). Forcing users to manually highlight and copy text from a stylized output block is cumbersome and error-prone.
**Action:** Always provide an explicit, accessible "Copy to Clipboard" icon button for complex data outputs. Ensure the button provides clear visual feedback (e.g., changing to a checkmark) and updates its `aria-label` temporarily so screen readers also receive success confirmation.
## 2026-04-10 - Async Form Validation Error Bubble Not Showing
**Learning:** In native browser form validation, calling `element.reportValidity()` on a disabled element (e.g., a button disabled during an async API call) will silently fail, meaning the error bubble never appears to the user even if `element.setCustomValidity()` was correctly set.
**Action:** When implementing async form submissions with loading states, always set `element.disabled = false` *before* calling `element.reportValidity()` in error catch blocks to ensure the validation bubble successfully renders.

## 2026-05-18 - Validation Bubble Override
**Learning:** When custom client-side validation is applied both to input fields and their parent action buttons (e.g., catching parsing errors on submit), the latter can inadvertently override the former. Specifically, if a catch block sets `setCustomValidity()` on the submit button after parsing fails, it steals focus and visually overrides the helpful inline validation bubble on the specific input.
**Action:** Always ensure that custom validation logic on parent action buttons checks for earlier input-level validation states (e.g., by throwing/catching a specific `ValidationError`) and bails out early to prevent overwriting the input's visual error bubble.

## 2024-05-19 - Visual Feedback on Stale Data
**Learning:** During heavy asynchronous operations (like numerical solving), leaving previously generated charts or outputs fully visible and interactive can confuse users, making them think the computation finished instantly or failed to start, particularly when the loading state is on a separate button.
**Action:** Always apply visual dimming (e.g., `opacity: 0.5`) and disable interactions (e.g., `pointer-events: none`) to output containers immediately when a background fetch starts, restoring them in the `finally` block. This clearly marks the current data as "stale" while the new data is computing.
## 2024-06-10 - Skip Links and Focus Management
**Learning:** Adding a "Skip to main content" link isn't enough if the target element (like `<main>`) is a non-interactive element. Browsers won't move programmatic focus to it unless it has `tabindex="-1"`. Furthermore, once it receives focus, it will display a massive focus ring unless `outline: none` is explicitly applied.
**Action:** Always add `tabindex="-1"` to the target of a skip link to allow programmatic focus, and use CSS `:focus { outline: none; }` to prevent visual noise while ensuring screen readers read the target content properly.

## 2024-06-25 - Visual Feedback for Stale Data on Input Modification
**Learning:** For forms that generate stateful outputs (like charts or complex mathematical matrices), modifying input fields without immediately updating the output can cause the output to silently become stale and inaccurate. This leads to user confusion and potentially copying incorrect data.
**Action:** Always add an `input` event listener to apply visual dimming (e.g., `opacity: 0.5`) to output containers when related input values change, indicating to the user that the displayed data is now stale and requires re-submitting the form to sync.
## 2024-08-16 - Visual Dimming Restoration on Error
**Learning:** Restoring visual dimming (removing `opacity` and `pointer-events: none`) in the `finally` block of an async operation is a common anti-pattern when updating stateful outputs like charts. If the async operation fails (e.g., due to validation errors), un-dimming the container makes the stale data appear fresh and accurate, confusing the user.
**Action:** Only restore visual dimming (e.g., `chartContainer.style.opacity = ''`) at the end of the `try` block, explicitly *after* the new data has successfully rendered. This ensures that if the operation fails, the old data remains visually dimmed, indicating it is stale and out of sync with the current form inputs.

## 2024-08-16 - API Validation Error Formatting for UI
**Learning:** Directly throwing `response.text()` for API validation errors (like Pydantic's JSON response) results in a raw JSON string being rendered inside the native form validation bubble, which is unreadable for users.
**Action:** Always intercept and parse backend API error responses before throwing them to the UI. Write a helper function (e.g., `handleApiError`) that extracts the specific error locations and messages (e.g., from `detail` arrays) and joins them into a clean, human-readable string for `setCustomValidity()`.

## 2024-08-20 - Stale Output Accessibility
**Learning:** Relying solely on visual dimming (`opacity: 0.5`) to indicate stale output leaves keyboard users and screen readers vulnerable. They can still navigate to and interact with elements inside the stale container (like a 'Copy' button) or read the stale text data as if it were accurate.
**Action:** Always explicitly disable interactive elements (`disabled = true`) or apply `pointer-events: none` alongside `aria-hidden="true"` when marking data/containers as visually stale.

## 2024-08-21 - Scalable Copy Buttons for Multiple Outputs
**Learning:** Displaying multiple complex outputs (like matrices and arrays) simultaneously in the UI requires dedicated copy actions for each to prevent user confusion and formatting errors. Hardcoding single IDs for the copy button and target text (e.g., `lqr-copy-k` and `lqr-k-val`) breaks down when scaling to multiple outputs, leading to duplicated listener code or missed stale-state handling.
**Action:** When displaying multiple complex outputs, provide dedicated copy buttons. To keep JS scalable and maintainable, use generic classes (e.g., `.copy-btn`) paired with `data-target` attributes, and use `querySelectorAll` for click listeners and state management (enabling/disabling) rather than hardcoding element IDs.
