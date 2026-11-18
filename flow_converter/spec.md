# Concrete Slab Calculator

## Purpose

Calculate the ordered concrete volume and estimated cost for a rectangular slab, and provide a scaled plan-view diagram with dimensions. The app is for a homeowner or contractor making a quick takeoff before ordering concrete.

## Inputs

- **Slab length (ft):** number box; 5 to 100 ft; default 20 ft.
- **Slab width (ft):** number box; 5 to 100 ft; default 30 ft.
- **Slab thickness (in):** slider; 4 to 12 in in increments of 0.5 in; default 6 in.
- **Waste factor (%):** slider; 0 to 20% in increments of 1%; default 10%.
- **Concrete price ($/cu yd):** number box; $50 to $300 per cubic yard; default $150.00.

All inputs update the app immediately. Invalid values outside the stated ranges should be rejected or clamped, and the app should show a concise validation message rather than calculate a result.

## Calculations

- Length: $L$ (ft)
- Width: $W$ (ft)
- Thickness: $T$ (in)
- Waste factor: $w$ (%)
- Concrete price: $P$ ($/cu yd)

1. Convert thickness to feet:
   $T_{ft}=T/12$
2. Calculate base slab volume:
   $V_{base}=L \times W \times T_{ft}$ (cu ft)
3. Convert to cubic yards:
   $V_{yd}=V_{base}/27$ (cu yd)
4. Add waste:
   $V_{needed}=V_{yd}\times(1+w/100)$ (cu yd)
5. Round the required volume up to the nearest 0.25 cubic yard:
   $V_{order}=\lceil V_{needed}/0.25\rceil\times0.25$ (cu yd)
6. Calculate total cost:
   $C=P\times V_{order}$ ($)

All length and thickness units must be converted before volume calculation.

## Outputs

- **Ordered concrete:** a large, prominent value showing cubic yards to order, rounded to two decimal places and labeled `cu yd`.
- **Total cost:** a large value showing US dollars, with two decimal places and a `$` prefix.
- **Calculation summary:** a compact table showing base volume (cu yd), waste percentage, waste volume (cu yd), and exact volume with waste (cu yd).
- **Plan-view diagram:** a rectangle drawn proportionally to the entered length and width. Its width and length dimensions are labeled with their units. The diagram updates immediately when the length or width changes.

## Look and feel

- Clean, professional engineering-tool layout.
- Sliders and number boxes appear in a card on the left.
- Results and the plan-view diagram appear in a card on the right.
- The ordered-volume value is the largest result.
- Use a restrained blue accent, white cards, light gray page background, and clear labels.
- The layout stacks vertically on narrow screens and remains usable without horizontal scrolling.

## Validation

Hand calculation example:

- Length: 20 ft
- Width: 30 ft
- Thickness: 6 in
- Waste factor: 10%
- Concrete price: $150.00/cu yd

Calculation:

1. $T_{ft}=6/12=0.5$ ft
2. $V_{base}=20\times30\times0.5=300$ cu ft
3. $V_{yd}=300/27=11.1111$ cu yd
4. $V_{needed}=11.1111\times1.10=12.2222$ cu yd
5. $V_{order}=\lceil12.2222/0.25\rceil\times0.25=12.25$ cu yd
6. $C=150\times12.25=$1837.50

Expected app results:

- Ordered concrete: **12.25 cu yd**
- Total cost: **$1,837.50**
- Base volume: **11.11 cu yd**
- Waste volume: **1.11 cu yd**

## Out of scope

- Structural design or slab strength calculations
- Rebar, forms, joints, grading, or labor estimates
- Nonrectangular slab shapes
- 3D models
- Live concrete supplier pricing
- Automatic truck or crew scheduling

## Build stages

1. **Layout mockup:** Build the controls, result cards, summary table, and plan-view drawing area with realistic placeholder values. Check that the desktop and mobile layouts are readable.
2. **Volume calculations:** Implement thickness conversion, cubic-yard conversion, waste, quarter-yard rounding, and the total-cost calculation as clearly named functions.
3. **Live inputs and validation:** Connect every input to live recalculation, range validation, and the displayed error state.
4. **Plan-view diagram:** Draw a proportionally scaled rectangle and label length and width with units.
5. **Polish and accessibility:** Improve visual states, keyboard access, responsive behavior, and output formatting, then rerun all validation cases.
