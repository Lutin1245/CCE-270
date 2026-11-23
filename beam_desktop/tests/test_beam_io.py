import csv
import json
import tempfile
import unittest
from pathlib import Path

from beam_calculations import (
    BeamCase,
    PointLoad,
    SECTION_CATALOG,
    UniformLoad,
    analyze_beam,
)
from beam_io import export_results_csv, load_beam_case, save_beam_case


class BeamFileTests(unittest.TestCase):
    def test_save_and_open_preserves_case_and_loads(self):
        case = BeamCase(
            span_ft=30,
            support="cantilever",
            loads=(PointLoad(4.5, 12.25), UniformLoad(0.75, 4, 18)),
            section=SECTION_CATALOG["W18x35"],
            deflection_limit_ratio=240,
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "design.json"
            save_beam_case(path, case)

            self.assertEqual(load_beam_case(path), case)
            saved_data = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(saved_data["format_version"], 1)
            self.assertEqual(saved_data["section"], "W18x35")
            self.assertEqual(len(saved_data["loads"]), 2)

    def test_rejects_unsupported_file_version(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "newer-version.json"
            path.write_text(
                json.dumps(
                    {
                        "format_version": 2,
                        "span_ft": 20,
                        "support": "simple",
                        "section": "W12x26",
                        "deflection_limit_ratio": 360,
                        "loads": [],
                    }
                ),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValueError, "Unsupported beam file version"):
                load_beam_case(path)

    def test_rejects_invalid_load_without_returning_a_case(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "invalid-load.json"
            path.write_text(
                json.dumps(
                    {
                        "format_version": 1,
                        "span_ft": 20,
                        "support": "simple",
                        "section": "W12x26",
                        "deflection_limit_ratio": 360,
                        "loads": [
                            {
                                "kind": "point",
                                "magnitude_kips": 5,
                                "position_ft": 21,
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValueError, "within the beam span"):
                load_beam_case(path)

    def test_csv_export_contains_unit_headers_and_all_sample_rows(self):
        result = analyze_beam(
            BeamCase(
                span_ft=20,
                support="simple",
                loads=(UniformLoad(1, 0.11, 19.73),),
                section=SECTION_CATALOG["W12x26"],
            )
        )
        self.assertIn(0.11, result.x_ft)
        self.assertIn(19.73, result.x_ft)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "results.csv"
            export_results_csv(path, result)

            self.assertTrue(path.read_bytes().startswith(b"\xef\xbb\xbf"))
            with path.open("r", encoding="utf-8-sig", newline="") as file:
                rows = list(csv.reader(file))

        self.assertEqual(
            rows[0], ["x (ft)", "V (kips)", "M (kip-ft)", "Deflection (in)"]
        )
        self.assertEqual(len(rows), len(result.x_ft) + 1)
        self.assertEqual(float(rows[1][0]), 0.0)
        self.assertEqual(float(rows[-1][0]), 20.0)
        exported_positions = {float(row[0]) for row in rows[1:]}
        self.assertIn(0.11, exported_positions)
        self.assertIn(19.73, exported_positions)
        moment_peak_index = next(
            index for index, x in enumerate(result.x_ft) if x == 10.0
        )
        peak_row = [float(value) for value in rows[moment_peak_index + 1]]
        self.assertAlmostEqual(peak_row[1], result.shear_kips[moment_peak_index])
        self.assertAlmostEqual(peak_row[2], result.moment_kip_ft[moment_peak_index])
        self.assertAlmostEqual(peak_row[3], result.deflection_in[moment_peak_index])


if __name__ == "__main__":
    unittest.main()
