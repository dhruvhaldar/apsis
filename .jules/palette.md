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

## 2024-05-24 - Accessible Overflowing Math Blocks
**Learning:** Mathematical formulas containing matrices or long integral equations often overflow horizontally on smaller screens. While `overflow-x: auto` allows mouse users to scroll, keyboard-only and screen reader users cannot access or read the full overflowing equation if the container isn't focusable.
**Action:** When creating containers with `overflow: auto` or `overflow: scroll` (like `.math-block`), always add `tabindex="0"` to make them keyboard focusable, assign an appropriate ARIA role (`role="region"`), give them an accessible name (`aria-label`), and provide a clear `:focus-visible` styling to indicate focus without relying on mouse interactions.

## 2026-04-23 - Focus Loss on Disabled Elements
**Learning:** When an interactive element (like a submit or copy button) is disabled (e.g., `disabled = true`) during an async or delayed operation, it instantly loses keyboard focus. The browser subsequently drops focus to the `<body>`, forcing keyboard-only and screen reader users to completely restart their navigation from the top of the page.
**Action:** Before disabling an element, always check if it currently has focus (`const wasFocused = document.activeElement === btn;`). If it did, explicitly call `btn.focus()` when re-enabling it in the `finally` block, `catch` block, or `setTimeout` to seamlessly restore the user's navigational context.

## 2026-04-23 - ARIA Label Updates on Disabled Elements
**Learning:** Updating the `aria-label` of a button (e.g., from 'Copy' to 'Copied') while the button is temporarily `disabled` fails to announce the change to screen readers, because disabled elements are generally ignored by accessibility APIs for dynamic updates.
**Action:** For temporary success states on disabled elements, do not rely on `aria-label` alone for screen reader feedback. Always use a visually hidden `aria-live="polite"` announcer region and inject the success message there.

## 2024-05-24 - Async Form Validation Focus Stealing
**Learning:** When using `finally` blocks in async form submissions to restore focus to a submit button (e.g., `if (wasFocused) btn.focus()`), it can inadvertently steal focus away from input fields that have just triggered native browser validation errors. This causes the helpful browser-native error bubble to immediately close, confusing the user and making the error invisible.
**Action:** When implementing custom client-side validation that hooks into native `reportValidity()`, always reset the `wasFocused` tracking variable (e.g., `wasFocused = false`) in the `catch` block if the error was a validation error on an input field. This ensures the input retains focus and the native error bubble remains visible to the user.

## 2026-04-25 - Avoid Dimming Empty States
**Learning:** Applying visual dimming (`opacity: 0.5`) to output containers when data becomes stale is a good UX pattern, but applying it when the container is in its initial "empty state" makes the UI look broken or disabled before the user has even submitted anything.
**Action:** When implementing stale data dimming logic on input changes, always check if the container is currently displaying an empty state (e.g., `!container.querySelector('.empty-state')`) and skip the dimming if it is.

## 2026-04-26 - Inline Validation Feedback
**Learning:** Relying solely on color changes (like a red border) to indicate validation errors violates WCAG 1.4.1 (Use of Color). Furthermore, when adding custom icons to the right side of `input[type="number"]`, the browser's default up/down spin arrows will visually overlap the icon, creating a cluttered and unreadable UI.
**Action:** When styling `:invalid` states, always add a secondary visual indicator (like an SVG warning icon via `background-image`). For number inputs, specifically hide the default spin arrows using `::-webkit-inner-spin-button { -webkit-appearance: none; }` and `-moz-appearance: textfield` to prevent icon overlap.

## 2026-04-27 - Intuitive Inline Validation
**Learning:** Using the `:invalid` pseudo-class for required form inputs causes them to aggressively display error styles (like red borders and warning icons) immediately when the page loads, before the user has even had a chance to interact with them. This creates a hostile and confusing first impression.
**Action:** Always prefer the `:user-invalid` pseudo-class over `:invalid` for inline form validation styling. This ensures that error states are only shown after the user has interacted with the input (e.g., focused and blurred) or attempted to submit the form, creating a much more pleasant and intuitive UX.

## 2026-04-30 - Form Label Focus Tracking
**Learning:** In forms with complex layouts or dark themes, it can be hard to quickly identify which input has focus. Furthermore, labels are often seen as purely decorative text rather than clickable interactive elements that focus their associated inputs.
**Action:** Make form labels discoverable by applying `cursor: pointer` via CSS. Additionally, apply a focus-within pattern to parent containers (e.g., `.input-group:focus-within label`) to highlight the active input's label, providing clear, intuitive visual tracking as the user tabs or clicks through the form.

## 2026-05-01 - Real-time Inline Validation for Strict Formats
**Learning:** For strict text inputs (like JSON arrays), validating on `input` can be frustrating because partial valid typing triggers errors. Validating on `focusout` perfectly complements CSS `:user-invalid` styling, providing immediate visual feedback and clear error states without interrupting the user's flow or waiting until form submission.
**Action:** Apply `focusout` validation logic for complex data formats (JSON, matrices) combined with native CSS `:user-invalid` to ensure a smooth, error-preventing user experience.

## 2026-05-02 - Keyboard Shortcuts and Accessibility
**Learning:** Adding visual hints for keyboard shortcuts inside buttons can create redundant and confusing announcements for screen reader users (e.g., reading "Solve PMP left parenthesis Ctrl plus Enter right parenthesis"). Power users utilizing screen readers will often discover shortcuts through documentation or application help, making the inline visual hint unnecessary noise.
**Action:** When adding inline keyboard shortcut hints to interactive elements, wrap the hint in a `<span>` and apply `aria-hidden="true"` to ensure the visual hint is hidden from accessibility APIs, keeping the button's accessible name clean and focused.

## 2024-10-24 - InnerText Destroys Structural HTML and A11y Attributes
**Learning:** When temporarily updating button contents (e.g., to a "Loading..." state) during async operations, caching and restoring the button's original state using `btn.innerText` destroys any structural HTML inside the button. This removes critical accessibility attributes like `aria-hidden="true"` and styling tags like `<kbd>`, resulting in degraded accessibility and visual regressions when the button is restored.
**Action:** Always use `btn.innerHTML` instead of `btn.innerText` when caching and restoring the content of interactive elements that contain child nodes, icons, or complex HTML structures.

## 2024-05-04 - Native Validation Tooltips
**Learning:** Native CSS `:user-invalid` styling correctly shows visual cues for invalid inputs, but it does not tell the user *why* the input is invalid if the browser's native error bubble is dismissed or hasn't appeared yet. This is particularly problematic for custom validation (e.g., using `setCustomValidity`).
**Action:** When an input is invalid, set its `title` attribute to the `validationMessage` (and clear it when valid). This exposes the error text as a native browser tooltip, allowing users to hover over the invalid field and read exactly what needs to be fixed.

## 2024-11-20 - Responsive CSS Grid on Mobile Viewports
**Learning:** Using `grid-template-columns: repeat(auto-fit, minmax(400px, 1fr))` creates a strict 400px minimum column width. On mobile devices with screen widths narrower than 400px (like iPhone SE at 375px), this forces horizontal scrolling and breaks the layout, violating WCAG 1.4.10 (Reflow).
**Action:** Always wrap the minimum value in CSS grid with `min(100%, [value]px)` (e.g., `minmax(min(100%, 400px), 1fr)`). This ensures the column shrinks to fit smaller viewports when necessary, preventing horizontal overflow while maintaining the desired layout on larger screens.

## 2026-05-07 - Fieldset Legend Focus Tracking
**Learning:** Form `<legend>` elements acting as group labels (e.g., for "Input Bounds" grouping multiple inputs) miss out on the visual focus tracking commonly applied to standard `<label>` elements when an input inside the group is focused. This inconsistency reduces the cohesiveness of the UI and makes tracking focus position across complex form groupings slightly harder for sighted keyboard/mouse users.
**Action:** When creating a `.focus-within` tracking style for form labels (e.g., `.input-group:focus-within label { color: highlight }`), extend the same selector logic to include `.input-group:focus-within legend`. Ensure `<legend>` specific styling is applied (like resetting the `cursor` to `default` instead of `pointer` if clicking it doesn't intuitively do anything, and padding adjustments).

## 2026-05-08 - Icon Button Disabled States & Delightful Animations
**Learning:** Icon buttons (like a clipboard copy button) that lack a clear visual `:disabled` state can cause user confusion, as they appear clickable even when the background process prevents interaction. Furthermore, adding subtle CSS animations (like gentle floating emojis in empty states) adds UI delight, but must always be wrapped in `@media (prefers-reduced-motion: no-preference)` to respect users with vestibular disorders or a preference for minimal motion.
**Action:** Always verify that every interactive element class (especially generic utility classes like `.icon-btn`) explicitly defines a `:disabled` CSS state (typically `opacity` and `cursor: not-allowed`). When adding decorative CSS animations, enforce the `prefers-reduced-motion` constraint to maintain a highly accessible baseline.

## 2026-05-09 - Spatial Orientation with Panel Focus-Within
**Learning:** In complex layouts with distinctly grouped visual panels, mouse users naturally orient themselves using the `:hover` states on those macro panels. However, keyboard users tabbing through deeply nested forms inside these panels don't receive the same macro-level visual feedback about which section they are currently working in, reducing spatial orientation.
**Action:** When a layout uses `:hover` effects to highlight macro containers (like panels or cards), always pair it with a `:focus-within` selector (`.panel:hover, .panel:focus-within`) to provide visual parity for keyboard users and maintain clear spatial orientation as they navigate through the application.

## 2024-05-18 - Respecting `prefers-reduced-motion` in JS Canvas
**Learning:** Checking CSS media queries for `prefers-reduced-motion` only stops CSS-based animations. It's equally important to extend these checks into JavaScript-driven animations (like Three.js or Canvas `requestAnimationFrame` loops) to fully respect the user's accessibility preferences.
**Action:** When implementing heavy background canvases or JS particle systems, expose a `window.matchMedia('(prefers-reduced-motion: reduce)')` boolean and conditionally pause rendering/transform loops.

## 2024-05-25 - Positive Validation Reinforcement
**Learning:** For complex inputs like JSON matrices, only showing error states (`:user-invalid`) can be stressful. Showing a subtle positive confirmation (`:user-valid`) when the format is correct gives the user confidence before submitting.
**Action:** When validating strict text formats, use CSS `:user-valid` coupled with a success icon (e.g., inline SVG data URI) to provide positive reinforcement once the user completes the input correctly.

## 2024-05-25 - Synchronizing Custom Validation and ARIA
**Learning:** `setCustomValidity` triggers CSS `:user-invalid` but does not reliably update the accessibility tree to announce the field as invalid to screen readers in all browsers.
**Action:** When implementing custom validation logic via JavaScript, always explicitly manage the `aria-invalid="true"` (or `"false"`) attribute alongside `setCustomValidity` to ensure screen readers provide accurate and immediate feedback about the input's state.

## 2024-05-25 - Semantic Cursors for Async Operations
**Learning:** Disabling a submit button during async operations using `.ui-btn:disabled` often defaults to a `cursor: not-allowed` style. While technically accurate (the button cannot be clicked), it conveys an error state rather than a loading state.
**Action:** Apply a specific `cursor: wait !important;` style to buttons when they are actively processing (e.g., matching the `aria-busy="true"` attribute). This provides a more intuitive, semantic visual cue that the application is working, overriding the generic disabled cursor.

## 2026-05-12 - Disabled State for Text Inputs
**Learning:** Text inputs that are disabled via the `disabled` attribute can appear almost identical to enabled inputs if they lack a clear visual `:disabled` state, causing user confusion.
**Action:** Always verify that every input element class (especially generic utility classes like `.ui-input`) explicitly defines a `:disabled` CSS state (typically `opacity` and `cursor: not-allowed`, or a slight background change) to clearly convey that it cannot be interacted with.

## 2024-05-25 - Contrast Ratios for Low-Opacity Text
**Learning:** Text elements that use `opacity` for styling (like `.shortcut-hint`, `.empty-state`, and placeholders) can easily violate WCAG AA 4.5:1 contrast requirements against complex, semi-transparent layered backgrounds (e.g., dark panels over darker global backgrounds). `opacity: 0.5` or `0.7` might look aesthetically pleasing but often renders the text unreadable for users with low vision.
**Action:** When designing subtle text elements on dark backgrounds, explicitly calculate the blended background color before checking contrast. Increase opacity (e.g., to `0.8` or `0.9` or `1`) or use a naturally brighter base color to ensure the final calculated contrast ratio remains above 4.5:1.

## 2026-05-15 - Accessible Names for Dynamic Canvases
**Learning:** Dynamically generated `<canvas>` elements (like those created by Chart.js) lack accessible names by default and are completely opaque to screen readers, which might just read "canvas" or ignore them entirely.
**Action:** When dynamically appending a `<canvas>` element to the DOM for data visualization, always explicitly add `role="img"` and a descriptive `aria-label` detailing what the chart represents to ensure screen readers can announce it properly.

## 2024-05-24 - Interactive Button Accessibility
**Learning:** Keyboard users often miss out on visual interactive cues like scaling and gradients if `:hover` states aren't paired with `:focus-visible`. Additionally, motion effects on focus/hover can cause vestibular discomfort during fast keyboard navigation.
**Action:** Always combine `:hover` and `:focus-visible` selectors for interactive buttons. Explicitly disable `transform` and `transition` properties for these buttons within `@media (prefers-reduced-motion: reduce)`.

## 2026-05-19 - Synchronizing Inline Validation with Submission Requirements
**Learning:** When using CSS `:user-valid` to provide positive reinforcement for complex inputs (like JSON formats), the inline validation logic must strictly match the backend or submission parsing requirements. If the inline validation is too permissive (e.g., accepting `1` or `"text"` as valid JSON), the user receives a positive reinforcement cue (`:user-valid`), only to have the form immediately fail on submission. This misalignment destroys user trust in the UI's positive feedback mechanisms.
**Action:** Always ensure that client-side inline validation logic (e.g., on `focusout`) strictly mirrors the final parsing logic used during form submission (e.g., ensuring a parsed JSON object is actually an `Array` if an array is expected).

## 2024-05-20 - Prevent Accidental Scrolling Changes on Number Inputs
**Learning:** Number inputs naturally increment or decrement when focused and the user scrolls the mouse wheel. In complex forms or long pages, users often click to focus a field, then use the scroll wheel to view the rest of the form, inadvertently changing the number value without realizing it. This causes silent data corruption and user frustration.
**Action:** Add a global `wheel` event listener to passively blur number inputs (`document.activeElement.blur()`) when the user attempts to scroll the page while a number input is focused, preventing the unintended value change.

## 2024-05-27 - Lock Form Inputs During Processing
**Learning:** Disabling only the submit button during async submissions leaves inputs active, allowing mid-flight modifications that cause user confusion and state mismatch.
**Action:** Explicitly disable all <input> elements within the form during processing.

## 2025-03-05 - Add programatic keyboard shortcuts
**Learning:** When adding visual keyboard shortcut hints inside interactive elements (like buttons), wrap the hint in a `<span>` with `aria-hidden="true"` to prevent redundant screen reader announcements, and provide the programmatic equivalent using the `aria-keyshortcuts` attribute on the parent interactive element.
**Action:** Always pair visual keyboard shortcut hints with the corresponding `aria-keyshortcuts` attribute on the interactive element.

## 2026-05-28 - Skip Link Contrast on Focus
**Learning:** Skip-to-content links that rely entirely on the page's global `--accent-dark` for their background color can violate WCAG contrast requirements (e.g., yielding 3.03:1 when using white text) because they are often designed without consideration for how bright the theme's accents actually are.
**Action:** Always ensure that hidden accessibility elements like skip links calculate contrast explicitly. Use the deepest background color (e.g., `--bg-color`) combined with an accent border and text to maintain high visibility (15:1+) when focused, instead of relying on solid bright background colors that fail contrast checks against white text.

## 2024-06-11 - Retaining Focus After Async Submissions
**Learning:** When users submit forms using keyboard shortcuts (like Ctrl+Enter) while focused on an input field, discarding the active element focus during the async fetching and indiscriminately returning focus only to the submit button (or dropping focus to the document body) disrupts keyboard navigation flow and reduces spatial orientation for keyboard users.
**Action:** When handling async form submissions, always store the currently active element universally (e.g. `document.activeElement`) rather than strictly checking if it is the submit button. Ensure that focus is restored gracefully in the `finally` block using a safety check (`typeof wasFocused.focus === 'function'`).

## 2026-05-30 - Disable smooth scrolling globally for reduced motion
**Learning:** `scroll-behavior: smooth` is often applied globally (`html { scroll-behavior: smooth; }`). Using a generic `@media (prefers-reduced-motion: reduce)` block that simply disables component animations or transitions will miss this global property. Smooth scrolling must be explicitly reverted to `auto` for users with vestibular disorders.
**Action:** When working on CSS bases or resetting styles, ensure `html { scroll-behavior: auto !important; }` exists within the `@media (prefers-reduced-motion: reduce)` block to prevent sudden vestibular discomfort.
## 2026-05-31 - Enable buttons before reportValidity
**Learning:** HTML5 constraint validation completely ignores disabled elements. Calling `.reportValidity()` on a disabled button silently fails to display the native error tooltip bubble.
**Action:** Always ensure the interactive element (e.g., submit button) is re-enabled (`disabled = false`) *before* calling `.reportValidity()` during async form error handling.

## 2024-06-12 - Auto-formatting as Positive Reinforcement
**Learning:** For strict text inputs (like JSON arrays), relying entirely on color changes (e.g. `:user-valid`) for positive reinforcement leaves the user uncertain about whether their specific formatting (spaces, quotes) was actually parsed correctly by the system.
**Action:** When validating complex string formats that will be parsed programmatically (like JSON), auto-format the user's input `onfocusout` (e.g., by replacing the input value with `JSON.stringify(parsed)`). This subtle, invisible helper acts as a powerful trust-building UX pattern, proving to the user that the system perfectly understood what they typed.

## 2026-06-03 - Enable inputs before reportValidity
**Learning:** HTML5 validation bubble (triggered by `reportValidity()`) silently fails if the input element is disabled. Since forms typically disable inputs on submission, validation logic running after this state change will not show the bubble unless the input is explicitly re-enabled first.
**Action:** Always verify that input elements are set to `disabled = false` prior to calling `reportValidity()`.

## 2024-06-14 - Prevent Focus-Stealing During Async State Restorations
**Learning:** During async flows (like form submissions or temporary UI feedback loops), elements are often temporarily disabled. Setting `disabled = true` instantly drops keyboard focus to `document.body`. A naive attempt to "fix" this by caching `document.activeElement` before the async operation and blindly calling `.focus()` on it in a `finally` block creates a highly disorienting experience, because if the user proactively tabbed away to another interactive element during the network request, their focus is forcibly stolen back.
**Action:**
1. For short feedback loops (like a 2-second "Copied" checkmark on a button), avoid `disabled = true` entirely. Instead, use a custom data attribute (like `dataset.copying = 'true'`) combined with CSS styling and JS logic to ignore rapid clicks while maintaining the native keyboard focus state safely.
2. For longer async flows (like form submissions where inputs *must* be disabled), only restore focus to the previously active element if the user is truly "lost" by including a safety check: `if (document.activeElement === document.body)`. This correctly restores focus if they were waiting, but respects their new location if they chose to navigate away.

## 2026-06-05 - Enable inputs before reportValidity on the submit button
**Learning:** Even if the submit button is enabled, having disabled required inputs within the same form can cause the browser to silently suppress the HTML5 validation bubble when calling `reportValidity()` on the button.
**Action:** When displaying a custom HTML5 validation bubble on a form's submit button via `btn.reportValidity()`, always ensure that all inputs within the form are re-enabled (`disabled = false`) first.

## 2026-06-10 - Focus Visible on Icon Buttons
**Learning:** Icon buttons that suppress default browser outlines (`outline: none`) and rely purely on `:hover` styles (like a subtle background or scale transform) often lack sufficient visual feedback for keyboard users when focused. Using `:focus-visible` without an explicit `outline` fails to communicate the active element clearly.
**Action:** When removing default outlines on interactive elements (like `.icon-btn`), always explicitly define a strong focus ring in the `:focus-visible` state (e.g., `outline: 2px solid var(--accent-color); outline-offset: 2px;`) to ensure robust keyboard accessibility.

## 2026-06-12 - Error State Icons for Color-Blind Accessibility
**Learning:** Indicating an inline form validation error strictly through a red border and red drop-shadow (`border-color: #ff6b6b`) violates WCAG 1.4.1 (Use of Color). Color-blind users (e.g., protanopia/deuteranopia) may struggle to perceive the error state, especially since the input background remains the same.
**Action:** Always pair color-based error indicators with a clear visual cue, such as an inline SVG warning icon (`background-image`), ensuring the error state is instantly perceptible regardless of color vision.

## 2024-11-21 - Touch Interface Redundancy and Mobile Padding
**Learning:** Keyboard shortcut hints (like "Ctrl+Enter") displayed directly in the UI are incredibly helpful for desktop power users, but they act as confusing, dead visual noise on touch devices (mobile/tablets) where hardware keyboards are absent. Additionally, macro structural paddings (like `padding: 20px` on a `.container` plus `padding: 30px` on an inner `.panel`) cascade beautifully on desktop but quickly starve critical horizontal space on narrow mobile screens, shrinking complex interactive elements (like data-dense charts) down to an unreadable size.
**Action:** Always wrap desktop-specific UI elements (like shortcut hints) in `@media (hover: none) and (pointer: coarse) { display: none; }` to hide them on touch devices. Furthermore, explicitly reduce macro container and panel paddings inside `@media (max-width: 600px)` blocks to maximize available interactive space for mobile users.

## 2026-06-17 - Clear Submit Button Validity on Input
**Learning:** When the server returns an error, it is sometimes displayed as a validation bubble on the submit button via `btn.setCustomValidity()`. However, when the user begins to interact with the form inputs to correct the issue, the submit button remains programmatically invalid. This can block native form submission attempts (like pressing Enter) even if the user has technically resolved the issue in the inputs.
**Action:** Always ensure that when a user interacts with form inputs, any `customValidity` previously set on the form's submit button is actively cleared, so that the button's programmatic validity state accurately reflects the new, unsubmitted state of the form.

## 2026-06-18 - Dynamic Aria-Live Announcements for Sequential Actions
**Learning:** Updating an `aria-live` region with the exact same static text (e.g., "Copied successfully!") fails to trigger a screen reader announcement on subsequent rapid clicks. Screen readers only announce changes to the DOM text node. If the text doesn't mutate, they stay silent, leaving users unaware if their second action succeeded.
**Action:** Always include dynamic, context-specific text in `aria-live` announcements (e.g., interpolating the specific item name being copied) to ensure the text content mutates and reliably triggers the screen reader on consecutive actions. Additionally, verify that timeout-based clears (`textContent = ''`) do not prematurely erase a subsequent action's message.

## 2026-06-19 - Manual control of visual success indicators over :user-valid
**Learning:** When providing visual positive reinforcement for complex inputs (like JSON arrays) that require JavaScript validation, relying on the native HTML5 `:user-valid` pseudo-class can cause false positives. The browser natively considers partial or mid-typing inputs (like `1[`) as "valid" text, triggering the green checkmark prematurely before the user finishes and `focusout` parsing can catch the error. This confuses users who think their partial input is correct.
**Action:** Avoid `:user-valid` for complex formats. Instead, explicitly control success styling via custom data attributes (e.g., `data-valid-json="true"`) that are set *only* when the JavaScript validation successfully parses the value (e.g., on `focusout`), and actively clear that attribute on `input` to hide the success mark while typing.

## 2026-06-20 - Contextual Focus Outlines for Validation States
**Learning:** Setting a global `:focus-visible` outline color (like the app's default cyan accent) causes visual clashes when the element is in a validation state (like a red border for errors, or a green border for success). Keyboard users see a confusing mix of colors that dilutes the validation feedback.
**Action:** When defining specific styling for form validation states (like `:user-invalid` or `[data-valid-json="true"]`), always include a corresponding `:focus-visible` rule that specifically overrides the `outline-color` to match the validation state's color (e.g., matching the red or green border), ensuring a cohesive, unambiguous experience during keyboard navigation.

## 2026-06-21 - Accessible Stale State Notifications
**Learning:** When inputs change and calculated outputs (like charts or text results) are visually dimmed and hidden from the accessibility tree (e.g., using `aria-hidden="true"`) to indicate they are "stale", screen reader users are not informed of this crucial state transition. They may continue expecting the data to be valid or not understand why the content disappeared or requires a form resubmission.
**Action:** Whenever an interactive output state is marked as "stale" visually, always accompany the visual change with a proactive `aria-live` announcement (e.g., "Input changed. Previous output is now stale. Resubmit to update.") to ensure screen reader users understand the current application state.

## 2026-06-25 - Native Dark Mode and Touch Keyboards
**Learning:** Even when an app implements a strict dark theme via custom CSS variables (`--bg-color`, `--text-color`), the browser natively falls back to light-mode defaults for intrinsic components like scrollbars, autofill dropdowns, context menus, and mobile browser address bars. This causes glaring, blinding flashes of white UI that break immersion. Furthermore, `<input type="number">` without a specific `inputmode` often forces mobile users to use the standard alphanumeric keyboard to enter digits, causing unnecessary friction.
**Action:** When building a dark-themed application, always explicitly declare `color-scheme: dark;` on the `:root` to force native browser components into dark mode, and pair it with `<meta name="theme-color" content="[hex]">` to style the mobile browser chrome. Additionally, always enhance numerical inputs with `inputmode="numeric"` (for integers) or `inputmode="decimal"` (for floats) to trigger the optimal, enlarged touch number pad on mobile devices.
