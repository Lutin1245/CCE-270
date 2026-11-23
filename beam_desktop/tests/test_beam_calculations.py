from math import isclose
import unittest

from beam_calculations import (
    BeamCase,
    PointLoad,
    SECTION_CATALOG,
    UniformLoad,
    analyze_beam,
)


class BeamCalculationTests(unittest.TestCase):
    def test_default_example_matches_specification(self):
        case = BeamCase(
            span_ft=20,
            support="simple",
            loads=(UniformLoad(1, 0, 20),),
            section=SECTION_CATALOG["W12x26"],
        )
        result = analyze_beam(
            case
        )

        self.assertAlmostEqual(result.max_moment_kip_ft, 50.0, places=2)
        self.assertAlmostEqual(result.max_deflection_in, 0.609, places=3)
        self.assertAlmostEqual(result.reaction_left_kips, 10.0, places=8)
        self.assertAlmostEqual(result.reaction_right_kips, 10.0, places=8)
        coarse = analyze_beam(case, step_ft=0.1)
        self.assertAlmostEqual(
            coarse.max_deflection_in, result.max_deflection_in, places=3
        )

    def test_partial_uniform_load_validation_case(self):
        result = analyze_beam(
            BeamCase(
                span_ft=30,
                support="simple",
                loads=(UniformLoad(2, 0, 15),),
                section=SECTION_CATALOG["W18x35"],
            )
        )

        self.assertAlmostEqual(result.reaction_left_kips, 22.5, places=8)
        self.assertAlmostEqual(result.reaction_right_kips, 7.5, places=8)
        self.assertAlmostEqual(result.max_moment_kip_ft, 126.5625, places=6)
        self.assertAlmostEqual(result.max_moment_position_ft, 11.25, places=6)

    def test_lumber_section_and_l240_limit(self):
        result = analyze_beam(
            BeamCase(
                span_ft=20,
                support="simple",
                loads=(UniformLoad(1, 0, 20),),
                section=SECTION_CATALOG["2x10"],
                deflection_limit_ratio=240,
            )
        )

        self.assertAlmostEqual(result.max_moment_kip_ft, 50.0, places=8)
        self.assertAlmostEqual(result.allowable_deflection_in, 1.0, places=8)
        self.assertAlmostEqual(
            result.bending_stress_ksi,
            50.0 * 12 / SECTION_CATALOG["2x10"].section_modulus_in3,
            places=8,
        )

    def test_cantilever_tip_load(self):
        load_kips = 2.0
        span_ft = 10.0
        section = SECTION_CATALOG["W12x26"]
        result = analyze_beam(
            BeamCase(
                span_ft=span_ft,
                support="cantilever",
                loads=(PointLoad(load_kips, span_ft),),
                section=section,
            )
        )

        expected_deflection = (
            load_kips * (span_ft * 12) ** 3
            / (3 * section.elastic_modulus_ksi * section.moment_of_inertia_in4)
        )
        self.assertAlmostEqual(result.reaction_left_kips, load_kips, places=8)
        self.assertAlmostEqual(result.fixed_end_moment_kip_ft, -20.0, places=8)
        self.assertAlmostEqual(result.max_moment_kip_ft, -20.0, places=8)
        self.assertAlmostEqual(result.max_moment_position_ft, 0.0, places=8)
        self.assertTrue(isclose(result.max_deflection_in, expected_deflection, abs_tol=1e-4))

    def test_center_point_load_simple_support(self):
        result = analyze_beam(
            BeamCase(
                span_ft=20,
                support="simple",
                loads=(PointLoad(5, 10),),
                section=SECTION_CATALOG["W12x26"],
            )
        )

        self.assertAlmostEqual(result.reaction_left_kips, 2.5, places=8)
        self.assertAlmostEqual(result.reaction_right_kips, 2.5, places=8)
        self.assertAlmostEqual(result.max_moment_kip_ft, 25.0, places=8)
        self.assertAlmostEqual(result.max_moment_position_ft, 10.0, places=8)

    def test_rejects_load_outside_span(self):
        with self.assertRaisesRegex(ValueError, "within the beam span"):
            analyze_beam(
                BeamCase(
                    span_ft=20,
                    support="simple",
                    loads=(PointLoad(5, 21),),
                    section=SECTION_CATALOG["W12x26"],
                )
            )


if __name__ == "__main__":
    unittest.main()
