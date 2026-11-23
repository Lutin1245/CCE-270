# Project specification

## Platform
- Python desktop app using Tkinter, started with `python app.py`
- Calculations with numpy, kept in their own module, separate from
  the window code
- Diagrams drawn with matplotlib, embedded in the window

# Beam Designer

## Purpose
Shear, moment, and deflection diagrams for a beam, with a check of
whether the beam is strong and stiff enough.

## Inputs
- Simply supported or cantilever, and the span (ft)
- Point loads and uniform loads
- A steel W-shape or a lumber size

## Calculations
- Reactions, shear, and moment from statics
- Deflection
- Bending stress fb = M/S, compared to the allowable stress
- Deflection compared to L/360

## Outputs
- The beam with its loads, and the three diagrams
- Pass or fail for bending and deflection

## Look and feel
Clean and professional, with an example beam loaded when it opens.

## Validation
20 ft simply supported W12x26 with 1 kip/ft: M = 50.0 kip-ft,
deflection 0.609 in.

## Out of scope
Continuous beams and buckling.

Detailed requirements: [polished specification](./specs/polished_spec.md).
Revised staged roadmap: [implementation plan](./00_planning/beam_designer_implementation_plan.md).


Change the Look and feel section for a desktop window: inputs in a panel on the left, the beam and diagrams on the right, and a window that can be resized. Remove the lines about phones.

Add this case to the Validation section: Simply supported, 30 ft, W18x35, uniform 2 kips/ft from 0 to 15 ft
   only: reactions 22.5 k (left) and 7.5 k (right); max moment
   126.6 kip-ft at 11.25 ft.