from __future__ import annotations

from typing import Literal

import matplotlib as mpl
import seaborn as sns

Theme = Literal["light", "dark"]


def apply_style(theme: Theme = "light", base_font_size: int = 10) -> None:
    palette = "crest" if theme == "light" else "rocket"
    sns.set_theme(
        context="notebook",
        style="whitegrid",
        palette=palette,
        font_scale=max(0.8, base_font_size / 10.0),
    )

    rc = mpl.rcParams

    # fonts and text
    rc["font.size"] = base_font_size
    rc["axes.titlesize"] = base_font_size + 2
    rc["axes.labelsize"] = base_font_size + 1
    rc["xtick.labelsize"] = base_font_size
    rc["ytick.labelsize"] = base_font_size
    rc["legend.fontsize"] = base_font_size
    rc["figure.titlesize"] = base_font_size + 3

    # figure sizing and DPI defaults
    rc["figure.dpi"] = 144
    rc["savefig.dpi"] = 144

    # lines and grid
    rc["axes.grid"] = True
    rc["grid.linestyle"] = "--"
    rc["grid.linewidth"] = 0.6
    rc["lines.linewidth"] = 2.0
    rc["lines.markersize"] = 3.5

    if theme == "dark":
        rc["figure.facecolor"] = "#0f172a"
        rc["axes.facecolor"] = "#0b1220"
        rc["axes.edgecolor"] = "#cbd5e1"
        rc["text.color"] = "#e2e8f0"
        rc["axes.labelcolor"] = "#e2e8f0"
        rc["xtick.color"] = "#cbd5e1"
        rc["ytick.color"] = "#cbd5e1"
        rc["grid.color"] = "#334155"
        rc["savefig.facecolor"] = rc["figure.facecolor"]
        rc["savefig.edgecolor"] = rc["figure.facecolor"]
    else:
        rc["figure.facecolor"] = "#ffffff"
        rc["axes.facecolor"] = "#ffffff"
        rc["axes.edgecolor"] = "#0f172a"
        rc["text.color"] = "#0f172a"
        rc["axes.labelcolor"] = "#0f172a"
        rc["xtick.color"] = "#1f2937"
        rc["ytick.color"] = "#1f2937"
        rc["grid.color"] = "#e5e7eb"
        rc["savefig.facecolor"] = rc["figure.facecolor"]
        rc["savefig.edgecolor"] = rc["figure.facecolor"]
