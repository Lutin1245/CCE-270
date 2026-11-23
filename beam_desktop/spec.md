# Beam Designer specification

## Platform

- Python desktop app launched with `python app.py`
- Tkinter window with inputs in a left panel and the beam plus diagrams on the
  right; the window and plots resize with the window
- NumPy-based beam calculations in a separate module, independent of the UI
- Matplotlib diagrams embedded in the window
- The existing `index.html` web app remains available and is not replaced

## Purpose

Show beam shear, moment, and deflection, with bending-strength and
serviceability checks for common beam/load cases.

## Inputs

- Simply supported or fixed-left cantilever support
- Span from 4 to 40 ft
- Any number of downward point loads and partial uniform loads
- Section selection: W12x26, W18x35, or Douglas Fir-Larch No. 2 2x10
- Deflection limit L/360 or L/240

## File operations

Provide Save and Open commands in a File menu. Store beam cases as versioned
JSON files containing the support type, span, section, deflection limit, and
all point and uniform loads. Validate an opened file before replacing the
current beam case, and report invalid or unsupported files without changing the
current case.

## Calculations

- Reactions, shear, and moment from statics
- Elastic deflection using the selected section's elastic modulus and moment of
  inertia
- Bending stress `fb = |M|max * 12 / S`, compared with the section's allowable
  bending stress
- Maximum absolute deflection compared with the selected span-to-deflection
  limit

All inputs and results use consistent units: span and load positions in feet,
point loads in kips, uniform loads in kips/ft, moments in kip-ft, shear in kips,
and deflection in inches.

Steel section properties use AISC Shapes Database v16.0. The steel allowable
bending stress and lumber design values retain the educational assumptions in
the existing web prototype; the steel grade is not specified.

## Outputs

- Beam and applied loads, shear diagram, bending-moment diagram, and deflection
  diagram
- Support reactions, maximum moment and its location, maximum deflection, and
  bending/deflection pass or fail

## Export results

Provide an Export results to CSV button. Export every sampled position along
the beam, including load boundaries, with columns for x (ft), shear V (kips),
moment M (kip-ft), and deflection (in). The UTF-8 CSV should open correctly in
Excel.

## Calculation sheet

Provide a button to save the current case as a PDF calculation sheet. List the
beam inputs and loads at the top, followed by the beam and response diagrams
and the bending and deflection checks.

## Look and feel

Clean, professional, resizable desktop window. Place beam inputs in a panel on
the left and the beam visualization, diagrams, and results on the right.

## Validation

- 20 ft simply supported W12x26 with 1 kip/ft over the full span: maximum
  moment 50.0 kip-ft and maximum deflection 0.609 in.
- 30 ft simply supported W18x35 with 2 kip/ft from 0 to 15 ft only: left
  reaction 22.5 kips, right reaction 7.5 kips, and maximum moment
  126.6 kip-ft at 11.25 ft.

## Out of scope

Continuous beams, buckling, self-weight, and code load combinations. Only the
listed three section selections are included in the initial desktop catalog.