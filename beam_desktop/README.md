# Beam Designer

The folder includes a standalone browser version (`index.html`) and a Python
Tkinter desktop version (`app.py`).

## Desktop app setup

Use Python 3.10 or newer with Tkinter available. From this folder, install the
Python dependencies and launch the app:

```powershell
python -m pip install -r requirements.txt
python app.py
```

The default case is a 20 ft simply supported W12x26 beam with a 1 kip/ft
uniform load. The desktop app supports point loads, partial uniform loads,
simply supported and cantilever beams, three section choices, and L/360 or
L/240 deflection limits. Use **File > Save** or **File > Open** to persist and
restore complete beam cases in versioned JSON files. Use **Export results to
CSV** to export the sampled x, V, M, and deflection values with units.

## Section-property assumptions

The W-shape geometry properties use the [AISC Shapes Database v16.0](https://www.aisc.org/aisc/publications/steel-construction-manual/shapes-database-v160/):
W12x26 has Ix = 204 in⁴ and Sx = 33.4 in³; W18x35 has Ix = 510 in⁴ and
Sx = 57.6 in³. Steel E = 29,000 ksi and Fb = 30 ksi follow the existing
educational web prototype; the spec does not identify a steel grade. The
Douglas Fir-Larch No. 2 2x10 properties likewise retain the prototype values
(E = 1,600 ksi, I = 98.93 in⁴, S = 21.39 in³, Fb = 0.9 ksi). Verify material
design values for the applicable grade and code before using results for
engineering design.

## Tests

Run the GUI-independent calculation tests from this folder:

```powershell
python -m unittest discover -s tests -v
```
