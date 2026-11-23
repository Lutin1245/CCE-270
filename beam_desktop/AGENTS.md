# Beam Desktop Agent Guide

## Scope and layout

This folder contains a browser app and a Python desktop app. Keep both
available unless a task explicitly asks to remove one.

- `index.html` is the standalone web app served directly by GitHub Pages.
- `app.py` is the resizable Tkinter desktop interface.
- `beam_calculations.py` contains GUI-independent beam calculations.
- `beam_io.py` handles versioned JSON save/open.
- `tests/` contains calculation and persistence tests.
- `spec.md` is the local project specification.

Use plain HTML, CSS, and browser JavaScript for the web app. Use Python,
Tkinter, NumPy, and Matplotlib for the desktop app. Do not introduce additional
frameworks or build tooling without a clear requirement.

## Engineering behavior

- Keep the default example: 20 ft simply supported W12x26 with a uniform
  1 kip/ft load.
- Support simply supported and fixed-left cantilever beams, point loads,
  partial uniform loads, and the three catalog sections W12x26, W18x35, and 2x10.
- Use consistent units: span and load positions in feet, point loads in kips,
  uniform loads in kips/ft, moments in kip-ft, shear in kips, and deflection in
  inches.
- Preserve the bending check `|M|max * 12 / S` against the catalog allowable
  bending stress and the selected L/360 or L/240 deflection check.
- Validate finite values and load ranges before calculations. Surface invalid
  user input instead of silently substituting values.
- Keep calculation logic independent of Tkinter and Matplotlib. Test changes to
  `beam_calculations.py` without opening the GUI.
- Keep saved cases limited to the supported catalog and input fields. Validate
  an opened case fully before changing the current UI state.
- Preserve load boundaries and support boundary conditions in statics and
  deflection calculations. Do not use plot resolution as the sole source of
  reported extrema.
- The default regression case must report maximum moment 50.0 kip-ft and
  maximum deflection 0.609 in for W12x26.
- The partial-load regression case is 30 ft simply supported with 2 kip/ft
  from 0 to 15 ft: reactions 22.5 kips and 7.5 kips, and maximum moment
  126.6 kip-ft at 11.25 ft.

## Validation

- Run calculation tests with `python -m unittest discover -s tests -v`.
- Check JSON save/open round trips and ensure malformed files leave the current
  case unchanged.
- For UI changes, launch `python app.py` and check both support modes, point and
  uniform loads, all sections and both deflection limits, resizing, and visible
  input errors.
- For web-app changes, check the browser behavior and responsive layout without
  breaking direct GitHub Pages serving.

After each completed request, add a concise entry to `prompts.md` only if that
file is already being maintained. Do not create it solely for documentation
requests.
