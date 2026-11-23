import json
import tempfile
import unittest
from pathlib import Path

from beam_calculations import BeamCase, PointLoad, SECTION_CATALOG, UniformLoad
from beam_io import load_beam_case, save_beam_case


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


if __name__ == "__main__":
    unittest.main()
