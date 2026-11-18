# Beam Designer implementation plan

Use [the polished specification](../specs/polished_spec.md) as the product requirements. Keep the short root-level [spec.md](../spec.md) as the starting draft; update the polished specification first whenever a product decision changes.

## Current state

- The single-page app, example beam, editable load controls, responsive layout, diagrams, basic result checks, and span-based load-position limits are in place.
- An independent calculation harness matches the four numerical cases in the polished specification; browser-level regression checks of the app's JavaScript remain to be done.
- The section selector currently includes only W12x26 and 2x10. The full material tables and the lightest-passing-section recommendation are still missing.
- Point loads can be entered in the load panel but cannot yet be dragged on the beam.
- Browser-level interaction and visual checks remain to be done.

## Revised build stages

### 1. Complete section data and selection

Add every steel and lumber section from the polished specification. Keep each section's E, Fb, Ix, Sx, and steel weight together in one data table; selecting a section must update its material properties and displayed units.

**Check:** Select every section and confirm its displayed properties match the table. Switching between steel and lumber must not leave stale properties behind.

### 2. Finish load editing and beam interaction

Keep add, edit, and remove controls for point and uniform loads. Enforce positions from zero to the current span, clamp uniform-load extents at the beam end, preserve the specified -3 ft end-position demonstration case, and add point-load dragging with 0.25 ft snapping.

**Check:** Add and remove each load type, change the span, enter positions beyond the beam end, and drag a point load. The displayed inputs and beam drawing must remain consistent.

### 3. Verify analysis diagrams and hover readout

Keep reactions, shear, and moment derived from equilibrium for both support types. Show the main beam following its calculated, visually magnified deflection shape, with loads attached to it. Ensure diagram sampling includes load locations and uniform-load boundaries, with a shared x scale and a hover cursor that reports V, M, and deflection at the same position.

**Check:** Compare reactions and maximum shear/moment against hand calculations for the simply supported and cantilever cases. Inspect values immediately before and after a point load.

### 4. Complete section checks and recommendation

Use the full section table to compute bending and deflection checks for all candidates. Recommend the lightest passing steel section, breaking equal-weight ties using Ix; for lumber, recommend the first passing table entry. Clearly report when no section passes.

**Check:** Verify pass/fail states, utilization values, and the recommended section for all four specified validation cases and for a deliberately over-capacity load.

### 5. Final validation and responsive review

Run all specified hand checks, address incorrect or inconsistent results, and review the beam drawing, diagrams, controls, and status cards at desktop and phone widths. Preserve the stated exclusions: no self-weight, buckling checks, continuous beams, load combinations, or saved designs.

**Check:** All four polished-spec cases match their expected reactions, maxima, deflections, and pass/fail outcomes. No input change causes stale values or an uncaught browser-console error.

## Validation order

1. Full-span 1 kip/ft load on the 20 ft simply supported W12x26 example.
2. 10 kip point load at 5 ft on a 20 ft simply supported W12x26.
3. 5 kip tip load on a 10 ft W12x26 cantilever.
4. 0.05 kip/ft on a 12 ft 2x10 joist.
