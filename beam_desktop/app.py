"""Tkinter front end for the Beam Designer."""

from __future__ import annotations

import tkinter as tk
from dataclasses import dataclass
from tkinter import filedialog, messagebox, ttk

import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from beam_calculations import (
    BeamCase,
    BeamResults,
    Load,
    PointLoad,
    SECTION_CATALOG,
    UniformLoad,
    analyze_beam,
)
from beam_io import load_beam_case, save_beam_case

SUPPORT_CHOICES = {
    "Simply supported": "simple",
    "Cantilever · fixed left": "cantilever",
}
SUPPORT_LABELS = {support: label for label, support in SUPPORT_CHOICES.items()}


@dataclass
class LoadRow:
    kind: str
    magnitude: tk.StringVar
    position: tk.StringVar | None = None
    start: tk.StringVar | None = None
    end: tk.StringVar | None = None


class ScrollableFrame(ttk.Frame):
    def __init__(self, parent: tk.Widget) -> None:
        super().__init__(parent)
        self.canvas = tk.Canvas(self, highlightthickness=0, width=330)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.content = ttk.Frame(self.canvas, padding=(12, 12, 10, 12))
        self.window_id = self.canvas.create_window(
            (0, 0), window=self.content, anchor="nw"
        )
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.content.bind("<Configure>", self._update_scroll_region)
        self.canvas.bind("<Configure>", self._resize_content)
        self.canvas.bind("<Enter>", self._bind_mousewheel)
        self.canvas.bind("<Leave>", self._unbind_mousewheel)

    def _update_scroll_region(self, _event: tk.Event) -> None:
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _resize_content(self, event: tk.Event) -> None:
        self.canvas.itemconfigure(self.window_id, width=event.width)

    def _scroll(self, event: tk.Event) -> None:
        if self.winfo_exists():
            self.canvas.yview_scroll(int(-event.delta / 120), "units")

    def _bind_mousewheel(self, _event: tk.Event) -> None:
        self.canvas.bind_all("<MouseWheel>", self._scroll)

    def _unbind_mousewheel(self, _event: tk.Event) -> None:
        self.canvas.unbind_all("<MouseWheel>")


class BeamDesignerApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Beam Designer")
        self.root.geometry("1320x850")
        self.root.minsize(1000, 650)
        self.root.configure(background="#f3f6f8")

        self.pending_update: str | None = None
        self.load_rows: list[LoadRow] = []
        self.span_var = tk.StringVar(value="20")
        self.support_var = tk.StringVar(value="Simply supported")
        self.section_var = tk.StringVar(value="W12x26")
        self.limit_var = tk.StringVar(value="360")
        self.error_var = tk.StringVar()
        self.summary_var = tk.StringVar()

        self._build_file_menu()
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=1)
        self.controls = ScrollableFrame(root)
        self.controls.grid(row=0, column=0, sticky="nsew")
        self.controls.configure(width=360)
        self.controls.grid_propagate(False)

        self.results = ttk.Frame(root, padding=(12, 12, 12, 12))
        self.results.grid(row=0, column=1, sticky="nsew")
        self.results.rowconfigure(1, weight=1)
        self.results.columnconfigure(0, weight=1)
        self._build_controls()
        self._build_results()
        self._add_load("uniform", magnitude="1", start="0", end="20")
        self._recalculate()

    def _build_file_menu(self) -> None:
        self.menu_bar = tk.Menu(self.root)
        self.file_menu = tk.Menu(self.menu_bar, tearoff=False)
        self.file_menu.add_command(label="Open...", command=self._open_beam)
        self.file_menu.add_command(label="Save...", command=self._save_beam)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        self.root.configure(menu=self.menu_bar)

    def _build_controls(self) -> None:
        panel = self.controls.content
        setup = ttk.LabelFrame(panel, text="Beam setup", padding=10)
        setup.pack(fill="x", pady=(0, 10))
        ttk.Label(setup, text="Support condition").grid(row=0, column=0, sticky="w")
        support = ttk.Combobox(
            setup,
            textvariable=self.support_var,
            state="readonly",
            values=tuple(SUPPORT_CHOICES),
        )
        support.grid(row=1, column=0, sticky="ew", pady=(3, 8))
        support.bind("<<ComboboxSelected>>", self._schedule_recalculation)
        ttk.Label(setup, text="Span (ft), 4–40").grid(row=2, column=0, sticky="w")
        span = ttk.Entry(setup, textvariable=self.span_var, width=12)
        span.grid(row=3, column=0, sticky="ew", pady=(3, 0))
        span.bind("<KeyRelease>", self._schedule_recalculation)
        span.bind("<FocusOut>", self._schedule_recalculation)
        setup.columnconfigure(0, weight=1)

        loads = ttk.LabelFrame(panel, text="Loads (downward)", padding=10)
        loads.pack(fill="x", pady=(0, 10))
        self.load_container = ttk.Frame(loads)
        self.load_container.pack(fill="x")
        buttons = ttk.Frame(loads)
        buttons.pack(fill="x", pady=(8, 0))
        ttk.Button(buttons, text="+ Point load", command=self._add_point_load).pack(
            side="left", padx=(0, 5)
        )
        ttk.Button(
            buttons, text="+ Uniform load", command=self._add_uniform_load
        ).pack(side="left")

        section = ttk.LabelFrame(panel, text="Section and limit", padding=10)
        section.pack(fill="x", pady=(0, 10))
        ttk.Label(section, text="Material / section").pack(anchor="w")
        section_select = ttk.Combobox(
            section,
            textvariable=self.section_var,
            state="readonly",
            values=tuple(SECTION_CATALOG),
        )
        section_select.pack(fill="x", pady=(3, 8))
        section_select.bind("<<ComboboxSelected>>", self._schedule_recalculation)
        ttk.Label(section, text="Deflection limit").pack(anchor="w")
        limit = ttk.Combobox(
            section,
            textvariable=self.limit_var,
            state="readonly",
            values=("360", "240"),
        )
        limit.pack(fill="x", pady=(3, 8))
        limit.bind("<<ComboboxSelected>>", self._schedule_recalculation)
        self.properties_label = ttk.Label(section, justify="left")
        self.properties_label.pack(anchor="w", pady=(2, 8))
        ttk.Button(section, text="Restore example", command=self._restore_example).pack(
            anchor="w"
        )
        ttk.Label(
            panel,
            textvariable=self.error_var,
            foreground="#a02e2e",
            wraplength=320,
            justify="left",
        ).pack(fill="x", pady=(2, 8))

    def _build_results(self) -> None:
        summary = ttk.Label(
            self.results,
            textvariable=self.summary_var,
            justify="left",
            wraplength=900,
            font=("Segoe UI", 10, "bold"),
        )
        summary.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        self.figure = Figure(figsize=(10, 7), dpi=100, facecolor="white")
        self.axes = self.figure.subplots(4, 1, sharex=True)
        self.figure.subplots_adjust(
            left=0.09, right=0.98, top=0.97, bottom=0.08, hspace=0.55
        )
        self.plot_frame = ttk.Frame(self.results)
        self.plot_frame.grid(row=1, column=0, sticky="nsew")
        self.plot_frame.rowconfigure(0, weight=1)
        self.plot_frame.columnconfigure(0, weight=1)
        self.figure_canvas = FigureCanvasTkAgg(self.figure, master=self.plot_frame)
        self.figure_canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")
        ttk.Label(
            self.results,
            text=(
                "Educational calculator only. Buckling, self-weight, and code load "
                "combinations are not included."
            ),
            foreground="#687985",
        ).grid(row=2, column=0, sticky="w", pady=(6, 0))

    def _add_point_load(self) -> None:
        try:
            position = float(self.span_var.get()) / 2
        except ValueError:
            position = 10.0
        self._add_load("point", magnitude="5", position=f"{position:g}")
        self._schedule_recalculation()

    def _add_uniform_load(self) -> None:
        try:
            end = float(self.span_var.get())
        except ValueError:
            end = 20.0
        self._add_load("uniform", magnitude="0.5", start="0", end=f"{end:g}")
        self._schedule_recalculation()

    def _add_load(self, kind: str, **values: str) -> None:
        if kind == "point":
            row = LoadRow(
                kind,
                tk.StringVar(value=values["magnitude"]),
                position=tk.StringVar(value=values["position"]),
            )
        else:
            row = LoadRow(
                kind,
                tk.StringVar(value=values["magnitude"]),
                start=tk.StringVar(value=values["start"]),
                end=tk.StringVar(value=values["end"]),
            )
        self.load_rows.append(row)
        self._refresh_load_rows()

    def _refresh_load_rows(self) -> None:
        for child in self.load_container.winfo_children():
            child.destroy()
        for index, row in enumerate(self.load_rows):
            kind = row.kind
            card = ttk.Frame(self.load_container, padding=(0, 5, 0, 7))
            card.pack(fill="x")
            title = "Point load" if kind == "point" else "Uniform load"
            ttk.Label(card, text=title, font=("Segoe UI", 9, "bold")).grid(
                row=0, column=0, columnspan=2, sticky="w", pady=(0, 4)
            )
            ttk.Button(
                card,
                text="Remove",
                command=lambda selected=index: self._remove_load(selected),
            ).grid(row=0, column=2, sticky="e", pady=(0, 4))
            fields = (
                [("magnitude", "Load (kips)")]
                if kind == "point"
                else [("magnitude", "Load (kips/ft)")]
            )
            fields.extend(
                [("position", "Position (ft)")]
                if kind == "point"
                else [("start", "Start (ft)"), ("end", "End (ft)")]
            )
            for col, (key, label) in enumerate(fields):
                variable = getattr(row, key)
                field_frame = ttk.Frame(card)
                field_frame.grid(row=1, column=col, sticky="ew", padx=(0, 5))
                ttk.Label(field_frame, text=label).pack(anchor="w")
                entry = ttk.Entry(field_frame, textvariable=variable, width=11)
                entry.pack(fill="x", pady=(2, 0))
                entry.bind("<KeyRelease>", self._schedule_recalculation)
                entry.bind("<FocusOut>", self._schedule_recalculation)
                card.columnconfigure(col, weight=1)
            ttk.Separator(self.load_container).pack(fill="x", pady=(3, 0))

    def _remove_load(self, index: int) -> None:
        del self.load_rows[index]
        self._refresh_load_rows()
        self._schedule_recalculation()

    def _restore_example(self) -> None:
        self.support_var.set("Simply supported")
        self.span_var.set("20")
        self.section_var.set("W12x26")
        self.limit_var.set("360")
        self.load_rows.clear()
        self._add_load("uniform", magnitude="1", start="0", end="20")
        self._recalculate()

    def _save_beam(self) -> None:
        try:
            case = self._read_case()
            analyze_beam(case)
        except (KeyError, ValueError) as error:
            messagebox.showerror("Cannot save beam", str(error), parent=self.root)
            return
        path = filedialog.asksaveasfilename(
            parent=self.root,
            title="Save beam case",
            defaultextension=".json",
            filetypes=(("Beam case JSON", "*.json"), ("All files", "*.*")),
        )
        if not path:
            return
        try:
            save_beam_case(path, case)
        except (OSError, ValueError, TypeError) as error:
            messagebox.showerror("Cannot save beam", str(error), parent=self.root)
            return
        messagebox.showinfo("Beam saved", "Beam case saved successfully.", parent=self.root)

    def _open_beam(self) -> None:
        path = filedialog.askopenfilename(
            parent=self.root,
            title="Open beam case",
            filetypes=(("Beam case JSON", "*.json"), ("All files", "*.*")),
        )
        if not path:
            return
        try:
            case = load_beam_case(path)
        except (OSError, ValueError) as error:
            messagebox.showerror("Cannot open beam", str(error), parent=self.root)
            return
        self._apply_case(case)

    def _apply_case(self, case: BeamCase) -> None:
        self.support_var.set(SUPPORT_LABELS[case.support])
        self.span_var.set(str(case.span_ft))
        self.section_var.set(case.section.key)
        self.limit_var.set(str(case.deflection_limit_ratio))
        self.load_rows.clear()
        for load in case.loads:
            if isinstance(load, PointLoad):
                self.load_rows.append(
                    LoadRow(
                        "point",
                        tk.StringVar(value=str(load.magnitude_kips)),
                        position=tk.StringVar(value=str(load.position_ft)),
                    )
                )
            else:
                self.load_rows.append(
                    LoadRow(
                        "uniform",
                        tk.StringVar(value=str(load.magnitude_kip_per_ft)),
                        start=tk.StringVar(value=str(load.start_ft)),
                        end=tk.StringVar(value=str(load.end_ft)),
                    )
                )
        self._refresh_load_rows()
        self.error_var.set("")
        self._recalculate()

    def _schedule_recalculation(self, _event: tk.Event | None = None) -> None:
        if self.pending_update is not None:
            self.root.after_cancel(self.pending_update)
        self.pending_update = self.root.after(120, self._recalculate)

    def _read_case(self) -> BeamCase:
        span = float(self.span_var.get())
        loads: list[Load] = []
        for row in self.load_rows:
            magnitude = float(row.magnitude.get())
            if row.kind == "point":
                if row.position is None:
                    raise ValueError("Point load is missing its position.")
                loads.append(PointLoad(magnitude, float(row.position.get())))
            else:
                if row.start is None or row.end is None:
                    raise ValueError("Uniform load is missing a start or end position.")
                loads.append(
                    UniformLoad(
                        magnitude,
                        float(row.start.get()),
                        float(row.end.get()),
                    )
                )
        return BeamCase(
            span_ft=span,
            support=SUPPORT_CHOICES[self.support_var.get()],
            loads=tuple(loads),
            section=SECTION_CATALOG[self.section_var.get()],
            deflection_limit_ratio=int(self.limit_var.get()),
        )

    def _recalculate(self) -> None:
        self.pending_update = None
        try:
            case = self._read_case()
            result = analyze_beam(case)
        except (ValueError, KeyError) as error:
            self.error_var.set(str(error) or "Enter valid finite numeric values.")
            return
        self.error_var.set("")
        section = case.section
        self.properties_label.configure(
            text=(
                f"E = {section.elastic_modulus_ksi:g} ksi\n"
                f"I = {section.moment_of_inertia_in4:g} in⁴   "
                f"S = {section.section_modulus_in3:g} in³\n"
                f"Allowable bending stress = "
                f"{section.allowable_bending_stress_ksi:g} ksi"
            )
        )
        self.summary_var.set(
            f"Reactions: left {result.reaction_left_kips:.2f} k"
            + (
                f"  |  right {result.reaction_right_kips:.2f} k"
                if case.support == "simple"
                else f"  |  fixed moment {result.fixed_end_moment_kip_ft:.2f} kip-ft"
            )
            + f"     Max moment: {abs(result.max_moment_kip_ft):.2f} kip-ft "
            f"at {result.max_moment_position_ft:.2f} ft"
            f"     Max deflection: {result.max_deflection_in:.3f} in"
            f"     Bending {'PASS' if result.bending_passes else 'FAIL'}"
            f"  |  Deflection {'PASS' if result.deflection_passes else 'FAIL'}"
        )
        self._draw(case, result)

    def _draw(self, case: BeamCase, result: BeamResults) -> None:
        axes = self.axes
        for axis in axes:
            axis.clear()
            axis.grid(True, color="#e5ebef", linewidth=0.7)
            axis.tick_params(labelsize=8)
        span = case.span_ft
        beam_axis = axes[0]
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
        data = (
            (axes[1], result.shear_kips, "Shear", "kips"),
            (axes[2], result.moment_kip_ft, "Bending moment", "kip-ft"),
            (axes[3], result.deflection_in, "Deflection", "in"),
        )
        for axis, values, title, unit in data:
            axis.axhline(0, color="#70838d", lw=0.8)
            axis.plot(x, values, color="#176b87", linewidth=1.8)
            axis.fill_between(x, values, 0, color="#dceef2", alpha=0.75)
            axis.set_ylabel(unit, fontsize=8)
            axis.set_title(title, loc="left", fontsize=9)
        axes[3].set_xlabel("Position along span (ft)", fontsize=8)
        self.figure_canvas.draw_idle()


def main() -> None:
    root = tk.Tk()
    BeamDesignerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
