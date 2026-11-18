# Beam Designer

## Purpose
A beam design tool for civil engineering students and engineers. The app lets the user configure a simply supported or cantilever beam, place point and uniform loads, and select a steel or lumber section. It updates shear, moment, deflected-shape diagrams, strength and stiffness checks, and the lightest passing section immediately.

## Users
A civil engineering student checking homework or an engineer sizing a floor beam or deck joist.

## Inputs
- Support type: Simply supported or Cantilever (fixed at the left end).
- Span: 4 to 40 ft, synchronized slider and number box.
- Point loads: magnitude in kips (downward positive), position in ft, editable/removable.
- Uniform loads: magnitude in kips/ft, start and end in ft, editable/removable.
- Add point load and Add uniform load buttons.
- Point loads are draggable along the beam and snap to 0.25 ft.
- Loads extending beyond the beam end are cut off.
- Material: Steel or Lumber.
- Steel W-shapes use E = 29,000 ksi and allowable bending stress Fb = 30 ksi:

  | Section | Ix (in^4) | Sx (in^3) | Weight (lb/ft) |
  |---------|-----------|-----------|----------------|
  | W8x10 | 30.8 | 7.81 | 10 |
  | W10x12 | 53.8 | 10.9 | 12 |
  | W12x26 | 204 | 33.4 | 26 |
  | W14x22 | 199 | 29.0 | 22 |
  | W16x26 | 301 | 38.4 | 26 |
  | W18x35 | 510 | 57.6 | 44 |
  | W21x44 | 843 | 81.6 | 44 |
  | W24x55 | 1350 | 114 | 55 |

- Douglas Fir-Larch No. 2 lumber uses E = 1,600 ksi and Fb = 0.900 ksi:

  | Section | Ix (in^4) | Sx (in^3) |
  |---------|-----------|-----------|
  | 2x8 | 47.63 | 13.14 |
  | 2x10 | 98.93 | 21.39 |
  | 2x12 | 177.98 | 31.64 |

- Deflection limit: L/240 or L/360, default L/360.
- Self-weight is ignored.

## Calculations
- Compute reactions from statics.
- Compute shear V(x), moment M(x), and deflection y(x) at 1 ft spacing or finer and exactly at every load start, end, and point-load position.
- Integrate M/EI twice using y = 0 at both supports for a simply supported beam, or y = 0 and slope = 0 at the fixed end for a cantilever.
- fb = |Mmax| * 12 / Sx (ksi).
- Deflection check uses |ymax| <= L/240 or L/360, with L in inches.
- Lightest passing section: lowest-weight steel section that passes both checks; if weights tie, use larger Ix. For lumber, use the first passing table entry.
- kips and ft for screen values; deflection in inches.

## Outputs
- Beam drawing with supports, load arrows, and reactions.
- Three stacked diagrams for shear, moment, and deflected shape on the same x scale.
- Filled diagrams with maximum values labeled.
- Mouse hover vertical guide showing V, M, and y at the pointer x.
- Bending and deflection cards showing actual and allowable values, utilization bar, and PASS/FAIL.
- Lightest passing section recommendation with Use section button.
- Side-by-side section comparison table for the selected material.
- Printable calculation sheet containing the inputs, diagrams, reactions, checks, and comparison.
- Everything updates immediately when inputs change.

## Look and feel
- Open with a 20 ft simply supported W12x26 beam and a 1 kip/ft uniform load over the full span.
- Clean commercial engineering interface: light background, white cards, soft shadows, one accent color, modern system font, generous spacing.
- Inputs in a left panel and results in a right panel; panels stack on phones.
- Every input has a short label with units. Check-card hover explains the formula.

## Validation
1. Simply supported, 20 ft, W12x26, full-span uniform 1 kip/ft:
   reactions 10 k each; max shear 10 k; max moment 50.0 kip-ft at 10 ft;
   fb = 17.96 ksi; max deflection 0.609 in at 10 ft; L/360 = 0.667 in; both pass.
2. Simply supported, 20 ft, W12x26, point load 10 k at 5 ft:
   reactions 7.5 k left and 2.5 k right; max moment 37.5 kip-ft at 5 ft;
   fb = 13.47 ksi; max deflection 0.340 in at 8.82 ft.
3. Cantilever, 10 ft, W12x26, point load 5 k at free end:
   reaction 5 k and fixed-end moment 50 kip-ft; max deflection 0.487 in at free end;
   L/360 = 0.333 in; deflection fails.
4. Simply supported, 12 ft, 2x10, uniform 0.05 kip/ft:
   max moment 0.90 kip-ft; fb = 0.505 ksi; max deflection 0.147 in; both pass.

## Validation additions
- Section comparison: with the default loading and W12x26 selected, changing the candidate section must update each row's bending and deflection utilization and PASS/FAIL state.
- Print sheet: print preview must include beam name, inputs, reactions, diagrams, checks, and section comparison.

## Out of scope
- Self-weight, shear stress, lateral-torsional buckling, load combinations, continuous beams, saving designs.

## Build stages
1. Mockup - single `index.html` responsive layout with placeholder inputs, beam drawing, three empty/realistic diagrams, and check cards.
   Check: layout matches the visual style and all controls/output panels are visible on desktop and mobile.
2. Beam input and load controls - support, span, material/section, deflection limit, editable load cards, add/remove controls, and synchronized span slider/number box.
   Check: all controls update the app immediately and point loads can be moved.
3. Structural calculations - reactions, shear, moment, deflection, and bending/stiffness checks in clearly named functions.
   Check: all four published validation cases match.
4. Drawing and diagrams - beam, supports, load arrows, reactions, filled diagrams, maximum labels, and shared hover guide.
   Check: arrows and diagrams align with the beam x scale and update with inputs.
5. Section recommendation and side-by-side comparison - rank candidate sections and show utilization table.
   Check: section choice and recommendation respond to all validation loading cases.
6. Printable calculation sheet - update spec and app with print-specific styling and print button.
   Check: browser print preview contains the complete calculation report.
