# Uniform-load calculation check

For a simply supported 20 ft beam carrying a 1 kip/ft uniform load across the full span:

- Reactions: `RA = RB = wL/2 = 10 kips`.
- Maximum moment: `Mmax = wL^2/8 = 50 kip-ft`, at midspan.
- For W12x26 (`E = 29,000 ksi`, `I = 204 in^4`), maximum deflection is `5wL^4/(384EI) = 0.609 in`, using `w = 1/12 kip/in` and `L = 240 in`.
- Bending stress is `50 * 12 / 33.4 = 17.96 ksi`.
- The `L/360` limit is `240/360 = 0.667 in`, so both checks pass.

Entering a uniform-load end beyond the beam span is limited to the beam end before recalculation.
