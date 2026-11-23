"""PDF calculation-sheet generation."""

from __future__ import annotations

from pathlib import Path

from matplotlib.figure import Figure

from beam_calculations import BeamCase, BeamResults, PointLoad
from beam_diagrams import draw_beam_diagrams


def save_calculation_sheet(
    path: str | Path, case: BeamCase, result: BeamResults
) -> None:
    page_height = max(11.0, 9.2 + 0.18 * len(case.loads))
    figure = Figure(figsize=(8.5, page_height), facecolor="white")
    title = "Beam Designer - Calculation Sheet"
    figure.text(
        0.08,
        (page_height - 0.48) / page_height,
        title,
        fontsize=15,
        weight="bold",
    )
    support = (
        "Simply supported"
        if case.support == "simple"
        else "Cantilever, fixed left"
    )
    figure.text(
        0.08,
        (page_height - 0.91) / page_height,
        f"Support: {support}    Span: {case.span_ft:g} ft",
        fontsize=9,
    )
    figure.text(
        0.08,
        (page_height - 1.24) / page_height,
        f"Section: {case.section.name}    "
        f"Deflection limit: L/{case.deflection_limit_ratio}",
        fontsize=9,
    )
    section = case.section
    figure.text(
        0.08,
        (page_height - 1.57) / page_height,
        f"Properties: E = {section.elastic_modulus_ksi:g} ksi; "
        f"I = {section.moment_of_inertia_in4:g} in^4; "
        f"S = {section.section_modulus_in3:g} in^3; "
        f"Fb = {section.allowable_bending_stress_ksi:g} ksi",
        fontsize=8,
    )

    load_heading_y = page_height - 1.92
    figure.text(
        0.08, load_heading_y / page_height, "Applied loads", fontsize=9, weight="bold"
    )
    first_load_y = page_height - 2.17
    if not case.loads:
        figure.text(0.1, first_load_y / page_height, "No applied loads", fontsize=8)
    for index, load in enumerate(case.loads, start=1):
        if isinstance(load, PointLoad):
            description = (
                f"{index}. Point load: {load.magnitude_kips:g} kips "
                f"at {load.position_ft:g} ft"
            )
        else:
            description = (
                f"{index}. Uniform load: {load.magnitude_kip_per_ft:g} kips/ft "
                f"from {load.start_ft:g} to {load.end_ft:g} ft"
            )
        figure.text(
            0.1,
            (first_load_y - 0.17 * (index - 1)) / page_height,
            description,
            fontsize=8,
        )

    checks_heading_y = first_load_y - 0.17 * max(1, len(case.loads)) - 0.2
    reaction_text = (
        f"Reactions: left {result.reaction_left_kips:.2f} k; "
        f"right {result.reaction_right_kips:.2f} k"
        if case.support == "simple"
        else f"Fixed reaction: {result.reaction_left_kips:.2f} k; "
        f"fixed-end moment: {result.fixed_end_moment_kip_ft:.2f} kip-ft"
    )
    check_lines = (
        reaction_text,
        f"Maximum |M|: {abs(result.max_moment_kip_ft):.2f} kip-ft "
        f"at {result.max_moment_position_ft:.2f} ft",
        f"Bending: {result.bending_stress_ksi:.2f} / "
        f"{section.allowable_bending_stress_ksi:.2f} ksi - "
        f"{'PASS' if result.bending_passes else 'FAIL'}",
        f"Deflection: {result.max_deflection_in:.3f} / "
        f"{result.allowable_deflection_in:.3f} in "
        f"(L/{case.deflection_limit_ratio}) - "
        f"{'PASS' if result.deflection_passes else 'FAIL'}",
    )
    figure.text(
        0.08, checks_heading_y / page_height, "Design checks", fontsize=9, weight="bold"
    )
    for index, line in enumerate(check_lines, start=1):
        figure.text(
            0.1,
            (checks_heading_y - 0.17 * index) / page_height,
            line,
            fontsize=8,
        )

    plot_bottom = 0.56
    plot_top = checks_heading_y - 0.86
    gap = 0.16
    axis_height = (plot_top - plot_bottom - 3 * gap) / 4
    axes = []
    for index in range(4):
        y = (plot_bottom + (3 - index) * (axis_height + gap)) / page_height
        axes.append(
            figure.add_axes(
                [0.13, y, 0.82, axis_height / page_height],
                sharex=axes[0] if axes else None,
            )
        )
    draw_beam_diagrams(axes, case, result)
    figure.text(
        0.08,
        0.2 / page_height,
        "Educational calculation only; not a substitute for complete engineering design.",
        fontsize=7,
        color="#687985",
    )
    figure.savefig(
        Path(path),
        format="pdf",
        metadata={"Title": title, "Subject": "Beam analysis calculation sheet"},
    )
