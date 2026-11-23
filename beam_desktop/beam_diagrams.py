"""Shared beam and response diagram rendering."""

from __future__ import annotations

from collections.abc import Iterable

import numpy as np
from matplotlib.axes import Axes

from beam_calculations import BeamCase, BeamResults, PointLoad


def draw_beam_diagrams(
    axes: Iterable[Axes], case: BeamCase, result: BeamResults
) -> None:
    plot_axes = tuple(axes)
    if len(plot_axes) != 4:
        raise ValueError("Beam diagrams require exactly four axes.")
    for axis in plot_axes:
        axis.clear()
        axis.grid(True, color="#e5ebef", linewidth=0.7)
        axis.tick_params(labelsize=8)

    span = case.span_ft
    beam_axis = plot_axes[0]
    beam_axis.plot([0, span], [0, 0], color="#29495a", linewidth=5)
    beam_axis.set_title("Beam and applied loads", loc="left", fontsize=10)
    beam_axis.set_ylim(-1.0, 1.25)
    beam_axis.set_yticks([])
    beam_axis.set_xlim(-span * 0.04, span * 1.04)
    if case.support == "simple":
        beam_axis.scatter(
            [0, span], [-0.16, -0.16], marker="^", s=95, color="#566c79", zorder=3
        )
        beam_axis.plot([0, span], [-0.27, -0.27], color="#8798a1", linewidth=1)
    else:
        beam_axis.axvline(0, color="#566c79", linewidth=5)
        for y in np.linspace(-0.75, 0.65, 8):
            beam_axis.plot([-span * 0.025, 0], [y - 0.12, y], color="#8798a1", lw=1)
    for load in case.loads:
        if isinstance(load, PointLoad):
            beam_axis.annotate(
                "",
                xy=(load.position_ft, 0.06),
                xytext=(load.position_ft, 0.72),
                arrowprops={"arrowstyle": "-|>", "color": "#176b87", "lw": 1.7},
            )
            beam_axis.text(
                load.position_ft,
                0.78,
                f"{load.magnitude_kips:g} k",
                ha="center",
                fontsize=8,
                color="#176b87",
            )
        else:
            positions = np.linspace(load.start_ft, load.end_ft, 11)
            for position in positions:
                beam_axis.annotate(
                    "",
                    xy=(position, 0.06),
                    xytext=(position, 0.58),
                    arrowprops={"arrowstyle": "-|>", "color": "#176b87", "lw": 1.1},
                )
            beam_axis.text(
                (load.start_ft + load.end_ft) / 2,
                0.65,
                f"{load.magnitude_kip_per_ft:g} k/ft",
                ha="center",
                fontsize=8,
                color="#176b87",
            )

    x = result.x_ft
    diagrams = (
        (plot_axes[1], result.shear_kips, "Shear", "kips"),
        (plot_axes[2], result.moment_kip_ft, "Bending moment", "kip-ft"),
        (plot_axes[3], result.deflection_in, "Deflection", "in"),
    )
    for axis, values, title, unit in diagrams:
        axis.axhline(0, color="#70838d", lw=0.8)
        axis.plot(x, values, color="#176b87", linewidth=1.8)
        axis.fill_between(x, values, 0, color="#dceef2", alpha=0.75)
        axis.set_ylabel(unit, fontsize=8)
        axis.set_title(title, loc="left", fontsize=9)
    plot_axes[3].set_xlabel("Position along span (ft)", fontsize=8)
