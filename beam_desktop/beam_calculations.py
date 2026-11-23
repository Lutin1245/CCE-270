"""Beam statics and elastic response calculations, independent of the GUI."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import TypeAlias

import numpy as np


@dataclass(frozen=True)
class SectionProperties:
    key: str
    name: str
    elastic_modulus_ksi: float
    moment_of_inertia_in4: float
    section_modulus_in3: float
    allowable_bending_stress_ksi: float


@dataclass(frozen=True)
class PointLoad:
    magnitude_kips: float
    position_ft: float


@dataclass(frozen=True)
class UniformLoad:
    magnitude_kip_per_ft: float
    start_ft: float
    end_ft: float


Load: TypeAlias = PointLoad | UniformLoad


@dataclass(frozen=True)
class BeamCase:
    span_ft: float
    support: str
    loads: tuple[Load, ...]
    section: SectionProperties
    deflection_limit_ratio: int = 360


@dataclass(frozen=True)
class BeamResults:
    x_ft: np.ndarray
    shear_kips: np.ndarray
    moment_kip_ft: np.ndarray
    deflection_in: np.ndarray
    reaction_left_kips: float
    reaction_right_kips: float
    fixed_end_moment_kip_ft: float
    max_moment_kip_ft: float
    max_moment_position_ft: float
    max_deflection_in: float
    max_deflection_position_ft: float
    bending_stress_ksi: float
    allowable_deflection_in: float
    bending_passes: bool
    deflection_passes: bool


# W-shape Ix/Sx values are from AISC Shapes Database v16.0. Moduli and
# allowable stresses retain the educational assumptions in the web prototype.
SECTION_CATALOG = {
    "W12x26": SectionProperties(
        "W12x26", "Steel · W12x26", 29000.0, 204.0, 33.4, 30.0
    ),
    "W18x35": SectionProperties(
        "W18x35", "Steel · W18x35", 29000.0, 510.0, 57.6, 30.0
    ),
    "2x10": SectionProperties(
        "2x10", "Douglas Fir-Larch No. 2 · 2x10", 1600.0, 98.93, 21.39, 0.9
    ),
}


def _validate_case(case: BeamCase) -> None:
    if not isfinite(case.span_ft) or not 4 <= case.span_ft <= 40:
        raise ValueError("Span must be a finite value between 4 and 40 ft.")
    if case.support not in {"simple", "cantilever"}:
        raise ValueError("Support must be 'simple' or 'cantilever'.")
    if case.deflection_limit_ratio not in {240, 360}:
        raise ValueError("Deflection limit must be L/240 or L/360.")
    section = case.section
    if any(
        not isfinite(value) or value <= 0
        for value in (
            section.elastic_modulus_ksi,
            section.moment_of_inertia_in4,
            section.section_modulus_in3,
            section.allowable_bending_stress_ksi,
        )
    ):
        raise ValueError("Section properties must be finite and positive.")
    for load in case.loads:
        if isinstance(load, PointLoad):
            if not isfinite(load.magnitude_kips) or load.magnitude_kips < 0:
                raise ValueError("Point-load magnitude must be finite and non-negative.")
            if not isfinite(load.position_ft) or not 0 <= load.position_ft <= case.span_ft:
                raise ValueError("Point load must be located within the beam span.")
        elif isinstance(load, UniformLoad):
            if not isfinite(load.magnitude_kip_per_ft) or load.magnitude_kip_per_ft < 0:
                raise ValueError("Uniform-load magnitude must be finite and non-negative.")
            if (
                not isfinite(load.start_ft)
                or not isfinite(load.end_ft)
                or not 0 <= load.start_ft <= load.end_ft <= case.span_ft
            ):
                raise ValueError("Uniform load must satisfy 0 ≤ start ≤ end ≤ span.")
        else:
            raise TypeError("Loads must be PointLoad or UniformLoad instances.")


def _load_total_and_moment(load: Load) -> tuple[float, float]:
    if isinstance(load, PointLoad):
        return load.magnitude_kips, load.magnitude_kips * load.position_ft
    total = load.magnitude_kip_per_ft * (load.end_ft - load.start_ft)
    centroid = (load.start_ft + load.end_ft) / 2
    return total, total * centroid


def analyze_beam(case: BeamCase, step_ft: float = 0.025) -> BeamResults:
    """Analyze a beam; positive applied loads point downward.

    Moments use positive sagging for simply supported beams. Deflection is
    reported by magnitude for checks; the plotted sign follows the conventional
    positive-upward displacement convention.
    """
    _validate_case(case)
    if not isfinite(step_ft) or step_ft <= 0:
        raise ValueError("Sampling step must be a finite positive value.")

    span = case.span_ft
    section = case.section
    total_load = 0.0
    total_moment_left = 0.0
    for load in case.loads:
        load_total, load_moment = _load_total_and_moment(load)
        total_load += load_total
        total_moment_left += load_moment

    if case.support == "simple":
        reaction_right = total_moment_left / span
        reaction_left = total_load - reaction_right
        fixed_end_moment = 0.0
    else:
        reaction_left = total_load
        reaction_right = 0.0
        fixed_end_moment = -total_moment_left

    def moment_at(x: float) -> float:
        if case.support == "simple":
            moment = reaction_left * x
            for load in case.loads:
                if isinstance(load, PointLoad):
                    moment -= load.magnitude_kips * max(0.0, x - load.position_ft)
                else:
                    moment -= load.magnitude_kip_per_ft * (
                        max(0.0, x - load.start_ft) ** 2
                        - max(0.0, x - load.end_ft) ** 2
                    ) / 2
            return moment

        moment = 0.0
        for load in case.loads:
            if isinstance(load, PointLoad):
                moment -= load.magnitude_kips * max(0.0, load.position_ft - x)
            else:
                moment -= load.magnitude_kip_per_ft * (
                    max(0.0, load.end_ft - x) ** 2
                    - max(0.0, load.start_ft - x) ** 2
                ) / 2
        return moment

    def shear_at(x: float) -> float:
        if case.support == "simple":
            shear = reaction_left
            for load in case.loads:
                if isinstance(load, PointLoad) and load.position_ft < x:
                    shear -= load.magnitude_kips
                elif isinstance(load, UniformLoad):
                    loaded_length = max(
                        0.0, min(x, load.end_ft) - load.start_ft
                    )
                    shear -= load.magnitude_kip_per_ft * loaded_length
            return shear

        shear = 0.0
        for load in case.loads:
            if isinstance(load, PointLoad) and load.position_ft > x:
                shear += load.magnitude_kips
            elif isinstance(load, UniformLoad):
                unloaded_start = max(load.start_ft, x)
                shear += load.magnitude_kip_per_ft * max(
                    0.0, load.end_ft - unloaded_start
                )
        return shear

    intervals = max(1, int(np.ceil(span / step_ft)))
    x_ft = np.linspace(0.0, span, intervals + 1)
    boundaries = [0.0, span]
    for load in case.loads:
        if isinstance(load, PointLoad):
            boundaries.append(load.position_ft)
        else:
            boundaries.extend((load.start_ft, load.end_ft))
    x_ft = np.unique(np.concatenate((x_ft, np.asarray(boundaries))))

    moment = np.fromiter((moment_at(float(x)) for x in x_ft), dtype=float)
    shear = np.fromiter((shear_at(float(x)) for x in x_ft), dtype=float)

    critical_x = list(boundaries)
    breaks = sorted(set(boundaries))
    for left, right in zip(breaks, breaks[1:]):
        if right - left <= 1e-12:
            continue
        epsilon = min(1e-9, (right - left) * 1e-6)
        x1, x2 = left + epsilon, right - epsilon
        v1, v2 = shear_at(x1), shear_at(x2)
        if v1 == 0:
            critical_x.append(x1)
        if v2 == 0:
            critical_x.append(x2)
        if v1 * v2 < 0:
            critical_x.append(x1 + (x2 - x1) * (-v1) / (v2 - v1))
    if case.support == "cantilever":
        critical_x = [0.0, span]
    critical_moments = [abs(moment_at(x)) for x in critical_x]
    max_moment_index = int(np.argmax(critical_moments))
    max_moment_position = float(critical_x[max_moment_index])
    max_moment = moment_at(max_moment_position)

    # M is kip-ft; convert to kip-in before integrating curvature over inches.
    curvature_per_in = moment * 12.0 / (
        section.elastic_modulus_ksi * section.moment_of_inertia_in4
    )
    x_in = x_ft * 12.0
    slopes = np.zeros_like(x_in)
    deflection = np.zeros_like(x_in)
    dx = np.diff(x_in)
    slopes[1:] = np.cumsum((curvature_per_in[:-1] + curvature_per_in[1:]) * dx / 2)
    deflection[1:] = np.cumsum((slopes[:-1] + slopes[1:]) * dx / 2)
    if case.support == "simple":
        deflection -= deflection[-1] * (x_in / x_in[-1])

    max_deflection_index = int(np.argmax(np.abs(deflection)))
    stress_ksi = abs(max_moment) * 12.0 / section.section_modulus_in3
    allowable_deflection = span * 12.0 / case.deflection_limit_ratio

    return BeamResults(
        x_ft=x_ft,
        shear_kips=shear,
        moment_kip_ft=moment,
        deflection_in=deflection,
        reaction_left_kips=reaction_left,
        reaction_right_kips=reaction_right,
        fixed_end_moment_kip_ft=fixed_end_moment,
        max_moment_kip_ft=max_moment,
        max_moment_position_ft=max_moment_position,
        max_deflection_in=float(np.max(np.abs(deflection))),
        max_deflection_position_ft=float(x_ft[max_deflection_index]),
        bending_stress_ksi=stress_ksi,
        allowable_deflection_in=allowable_deflection,
        bending_passes=stress_ksi <= section.allowable_bending_stress_ksi,
        deflection_passes=float(np.max(np.abs(deflection))) <= allowable_deflection,
    )
