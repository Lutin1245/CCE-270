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
from beam_report import save_calculation_sheet


class BeamReportTests(unittest.TestCase):
    def assert_pdf_created(self, case: BeamCase) -> None:
        result = analyze_beam(case)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "calculation-sheet.pdf"
            save_calculation_sheet(path, case, result)

            content = path.read_bytes()

        self.assertTrue(content.startswith(b"%PDF-"))
        self.assertTrue(content.rstrip().endswith(b"%%EOF"))
        self.assertGreater(len(content), 5000)

    def test_saves_calculation_sheet_pdf(self):
        case = BeamCase(
            span_ft=20,
            support="simple",
            loads=(UniformLoad(1, 0, 20),),
            section=SECTION_CATALOG["W12x26"],
        )
        self.assert_pdf_created(case)

    def test_saves_cantilever_sheet_with_mixed_loads(self):
        case = BeamCase(
            span_ft=10,
            support="cantilever",
            loads=(PointLoad(5, 6), UniformLoad(0.5, 1, 8)),
            section=SECTION_CATALOG["W12x26"],
        )
        self.assert_pdf_created(case)


if __name__ == "__main__":
    unittest.main()
