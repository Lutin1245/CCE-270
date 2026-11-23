"""Versioned JSON persistence for beam cases."""

from __future__ import annotations

import csv
import json
from math import isfinite
from pathlib import Path
from typing import Any

from beam_calculations import (
    BeamCase,
    BeamResults,
    PointLoad,
    SECTION_CATALOG,
    UniformLoad,
    analyze_beam,
)

FORMAT_VERSION = 1
_CASE_KEYS = {
    "format_version",
    "span_ft",
    "support",
    "section",
    "deflection_limit_ratio",
    "loads",
}
_RESULT_HEADERS = ("x (ft)", "V (kips)", "M (kip-ft)", "Deflection (in)")


def save_beam_case(path: str | Path, case: BeamCase) -> None:
    if (
        not isinstance(case.section.key, str)
        or case.section.key not in SECTION_CATALOG
        or SECTION_CATALOG[case.section.key] != case.section
    ):
        raise ValueError("Only catalog sections can be saved.")
    analyze_beam(case)

    loads: list[dict[str, Any]] = []
    for load in case.loads:
        if isinstance(load, PointLoad):
            loads.append(
                {
                    "kind": "point",
                    "magnitude_kips": load.magnitude_kips,
                    "position_ft": load.position_ft,
                }
            )
        elif isinstance(load, UniformLoad):
            loads.append(
                {
                    "kind": "uniform",
                    "magnitude_kip_per_ft": load.magnitude_kip_per_ft,
                    "start_ft": load.start_ft,
                    "end_ft": load.end_ft,
                }
            )
        else:
            raise TypeError("Loads must be PointLoad or UniformLoad instances.")

    data = {
        "format_version": FORMAT_VERSION,
        "span_ft": case.span_ft,
        "support": case.support,
        "section": case.section.key,
        "deflection_limit_ratio": case.deflection_limit_ratio,
        "loads": loads,
    }
    with Path(path).open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2, allow_nan=False)
        file.write("\n")


def load_beam_case(path: str | Path) -> BeamCase:
    try:
        with Path(path).open("r", encoding="utf-8") as file:
            data = json.load(file)
    except json.JSONDecodeError as error:
        raise ValueError(f"Invalid beam JSON: {error.msg}.") from error

    if not isinstance(data, dict) or set(data) != _CASE_KEYS:
        raise ValueError("Beam file has an invalid case structure.")
    if (
        type(data["format_version"]) is not int
        or data["format_version"] != FORMAT_VERSION
    ):
        raise ValueError(
            f"Unsupported beam file version: {data['format_version']!r}."
        )

    support = data["support"]
    if not isinstance(support, str) or support not in {"simple", "cantilever"}:
        raise ValueError("Beam file has an unsupported support type.")
    section_key = data["section"]
    if not isinstance(section_key, str) or section_key not in SECTION_CATALOG:
        raise ValueError("Beam file has an unsupported section.")
    limit = data["deflection_limit_ratio"]
    if type(limit) is not int or limit not in {240, 360}:
        raise ValueError("Beam file deflection limit must be 240 or 360.")

    raw_loads = data["loads"]
    if not isinstance(raw_loads, list):
        raise ValueError("Beam file loads must be a list.")
    loads = []
    for raw_load in raw_loads:
        if not isinstance(raw_load, dict):
            raise ValueError("Each beam load must be an object.")
        kind = raw_load.get("kind")
        if kind == "point" and set(raw_load) == {
            "kind",
            "magnitude_kips",
            "position_ft",
        }:
            loads.append(
                PointLoad(
                    _read_number(raw_load["magnitude_kips"], "point-load magnitude"),
                    _read_number(raw_load["position_ft"], "point-load position"),
                )
            )
        elif kind == "uniform" and set(raw_load) == {
            "kind",
            "magnitude_kip_per_ft",
            "start_ft",
            "end_ft",
        }:
            loads.append(
                UniformLoad(
                    _read_number(
                        raw_load["magnitude_kip_per_ft"], "uniform-load magnitude"
                    ),
                    _read_number(raw_load["start_ft"], "uniform-load start"),
                    _read_number(raw_load["end_ft"], "uniform-load end"),
                )
            )
        else:
            raise ValueError("Beam file contains an invalid load.")

    case = BeamCase(
        span_ft=_read_number(data["span_ft"], "span"),
        support=support,
        loads=tuple(loads),
        section=SECTION_CATALOG[section_key],
        deflection_limit_ratio=limit,
    )
    analyze_beam(case)
    return case


def export_results_csv(path: str | Path, results: BeamResults) -> None:
    columns = (
        results.x_ft,
        results.shear_kips,
        results.moment_kip_ft,
        results.deflection_in,
    )
    if len({len(column) for column in columns}) != 1:
        raise ValueError("Beam result columns must have matching lengths.")
    with Path(path).open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(_RESULT_HEADERS)
        for row in zip(*columns):
            writer.writerow(float(value) for value in row)


def _read_number(value: object, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"Beam file {label} must be a number.")
    try:
        number = float(value)
    except OverflowError as error:
        raise ValueError(f"Beam file {label} is outside the supported range.") from error
    if not isfinite(number):
        raise ValueError(f"Beam file {label} must be finite.")
    return number
