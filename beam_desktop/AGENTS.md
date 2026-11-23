# Beam Desktop Agent Guide

## Scope

This folder is a standalone, single-file beam-analysis web app. Unless a task
explicitly covers the rest of the repository, all edits should stay in this
folder.

## Project layout

- `index.html` contains the HTML, CSS, SVG rendering, beam calculations,
  validation, and interaction logic. Keep this as a single-file app unless the
  user explicitly requests a build setup or module split.
- `spec.md` is the local project summary and validation checklist.
- `prompts.md`, if it is present, is the session/request log. `AGENTS.md`,
  `spec.md`, `prompts.md`, and `index.html` belong at the project root.
- GitHub Pages should continue to serve `index.html` directly.

Do not assume absent planning or spec folders exist; do not create build,
dependency, or package configuration without a clear requirement.

## Implementation expectations

- Use plain HTML, CSS, and browser JavaScript. Do not introduce frameworks,
  dependencies, or transpilation.
- Preserve the existing responsive layout and accessible form/diagram labels.
- Keep the example loaded by default: 20 ft simply supported W12x26 with a
  uniform 1 kip/ft load.
- Maintain support for simply supported beams and cantilever beams with loads
  and section selections.
- Keep engineering units and sign conventions consistent:
  - Span and load positions are in feet.
  - Point-load magnitudes are kips.
  - Uniform-load magnitudes are kips per foot.
  - Moments are kip-ft.
  - Shear is kips.
  - Deflection is inches.
- Preserve the bending check as `|M|max * 12 / S` compared with the selected
  material's allowable stress.
- Preserve the deflection check against the selected `L/360` or `L/240` limit.
- Be careful with beam state and numerical integration. Preserve load
  boundaries, reaction calculations, coordinate sampling, and section properties
  when changing the calculator.

## Editing and validation

- Make surgical changes in `index.html`; keep CSS, markup, and JavaScript in
  their existing `<style>` and `<script>` sections.
- Prefer native browser APIs and the existing DOM helpers. Do not rewrite the
  page architecture for a small fix.
- Validate input ranges and finite values before calculations, and retain the
  visible form-error pattern for invalid input.
- Use browser developer tools or a local HTTP server to test UI changes.
- Check at minimum:
  - The default example.
  - At least one point load and one uniform load.
  - Simply supported and cantilever modes.
  - Both W12x26 and 2x10 sections.
  - Both deflection limits.
  - Responsive behavior and no browser console errors.
- The required 20 ft example should calculate a maximum moment of 50.0 kip-ft
  and a deflection of 0.609 in for the W12x26 model. Do not weaken or replace
  this as a regression check.

## Request logging

After each completed request, add one concise entry to `prompts.md` when that
file is being maintained in this project. Record what was asked, what changed,
and whether it succeeded. Do not create `prompts.md` solely for a documentation
only request unless the project already uses it.
