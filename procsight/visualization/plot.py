from __future__ import annotations

from itertools import accumulate
from typing import Sequence, Tuple

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.ticker import MaxNLocator

from procsight.models.metrics import CpuUsage, MemoryUsage, ProcessSample
from procsight.visualization.style import Theme, apply_style


def _finalize(fig: Figure, ax: Axes, *, title: str | None = None) -> None:
    if title:
        ax.set_title(title, pad=10)
    ax.legend(loc="best", frameon=False)
    ax.margins(x=0.02)
    ax.xaxis.set_major_locator(MaxNLocator(integer=False, nbins="auto", prune=None))
    fig.tight_layout()


def plot_cpu_usage(
    data: Sequence[Tuple[CpuUsage, MemoryUsage]],
    times: Sequence[float],
    *,
    show: bool = True,
    save_path: str | None = None,
    dpi: int = 144,
    transparent: bool = False,
    theme: Theme = "light",
):
    apply_style(theme=theme)  # ensure consistent look
    fig, ax = plt.subplots(figsize=(9, 4))
    ax.plot(times, [cpu.process for cpu, _ in data], label="CPU % (per core)")
    ax.set_ylabel("CPU per-core usage (%)")
    ax.set_xlabel("Time (s)")
    _finalize(fig, ax, title="CPU Utilization Over Time")

    if save_path:
        fig.savefig(save_path, dpi=dpi, bbox_inches="tight", transparent=transparent)

    if show:
        plt.show()

    plt.close(fig)


def plot_memory_usage(
    data: Sequence[Tuple[CpuUsage, MemoryUsage]] | Sequence[ProcessSample],
    times: Sequence[float],
    *,
    show: bool = True,
    save_path: str | None = None,
    dpi: int = 144,
    transparent: bool = False,
    theme: Theme = "light",
):
    apply_style(theme=theme)
    fig, ax = plt.subplots(figsize=(9, 4))

    # When called from basic mode, data is tuples; from extended, it's ProcessSample
    def _rss_mb(item) -> float:
        if isinstance(item, tuple):
            return item[1].rss
        return item.memory.rss

    ax.plot(times, [_rss_mb(i) for i in data], label="RSS MB")
    ax.set_ylabel("Memory RSS (MB)")
    ax.set_xlabel("Time (s)")
    _finalize(fig, ax, title="Resident Memory Over Time")

    if save_path:
        fig.savefig(save_path, dpi=dpi, bbox_inches="tight", transparent=transparent)

    if show:
        plt.show()

    plt.close(fig)


def plot_cpu_components(
    samples: Sequence[ProcessSample],
    times: Sequence[float],
    *,
    show: bool = True,
    save_path: str | None = None,
    dpi: int = 144,
    transparent: bool = False,
    theme: Theme = "light",
):
    apply_style(theme=theme)
    fig, ax = plt.subplots(figsize=(9, 4))
    ax.plot(times, [s.cpu.user or 0 for s in samples], label="User (s)")
    ax.plot(times, [s.cpu.system or 0 for s in samples], label="System (s)")
    ax.plot(
        times, [s.cpu.process for s in samples], label="Total % (per core)", alpha=0.7
    )
    ax.set_ylabel("CPU (per-core % / seconds)")
    ax.set_xlabel("Time (s)")
    _finalize(fig, ax, title="CPU Breakdown")
    if save_path:
        fig.savefig(save_path, dpi=dpi, bbox_inches="tight", transparent=transparent)
    if show:
        plt.show()
    plt.close(fig)


def plot_memory_breakdown(
    samples: Sequence[ProcessSample],
    times: Sequence[float],
    *,
    show: bool = True,
    save_path: str | None = None,
    dpi: int = 144,
    transparent: bool = False,
    theme: Theme = "light",
):
    apply_style(theme=theme)
    fig, ax = plt.subplots(figsize=(9, 4))
    rss = [s.memory.rss for s in samples]
    shared = [s.memory.shared or 0 for s in samples]
    data = [s.memory.data or 0 for s in samples]
    text = [s.memory.text or 0 for s in samples]

    ax.stackplot(
        times,
        rss,
        shared,
        data,
        text,
        labels=["RSS", "Shared", "Data", "Text"],
        alpha=0.8,
    )
    ax.set_ylabel("Memory (MB)")
    ax.set_xlabel("Time (s)")
    _finalize(fig, ax, title="Memory Breakdown (Stacked)")
    if save_path:
        fig.savefig(save_path, dpi=dpi, bbox_inches="tight", transparent=transparent)
    if show:
        plt.show()
    plt.close(fig)


def plot_io_bytes_cumulative(
    samples: Sequence[ProcessSample],
    times: Sequence[float],
    *,
    show: bool = True,
    save_path: str | None = None,
    dpi: int = 144,
    transparent: bool = False,
    theme: Theme = "light",
):
    apply_style(theme=theme)
    fig, ax = plt.subplots(figsize=(9, 4))
    read_b = [s.io.read_bytes for s in samples]
    write_b = [s.io.write_bytes for s in samples]

    def is_monotonic(xs: Sequence[int]) -> bool:
        return all(b >= a for a, b in zip(xs, xs[1:]))

    if not is_monotonic(read_b):
        read_b = list(accumulate(read_b))
    if not is_monotonic(write_b):
        write_b = list(accumulate(write_b))

    ax.plot(times, [rb / (1024**2) for rb in read_b], label="Read MB")
    ax.plot(times, [wb / (1024**2) for wb in write_b], label="Write MB")
    ax.set_ylabel("I/O (MB)")
    ax.set_xlabel("Time (s)")
    _finalize(fig, ax, title="Cumulative I/O Bytes")
    if save_path:
        fig.savefig(save_path, dpi=dpi, bbox_inches="tight", transparent=transparent)
    if show:
        plt.show()
    plt.close(fig)


def plot_ctx_switches(
    samples: Sequence[ProcessSample],
    times: Sequence[float],
    *,
    show: bool = True,
    save_path: str | None = None,
    dpi: int = 144,
    transparent: bool = False,
    theme: Theme = "light",
):
    apply_style(theme=theme)
    fig, ax = plt.subplots(figsize=(9, 4))
    ax.plot(times, [s.ctx.voluntary for s in samples], label="Voluntary")
    ax.plot(times, [s.ctx.involuntary for s in samples], label="Involuntary")
    ax.set_ylabel("Context Switches")
    ax.set_xlabel("Time (s)")
    _finalize(fig, ax, title="Context Switches Over Time")
    if save_path:
        fig.savefig(save_path, dpi=dpi, bbox_inches="tight", transparent=transparent)
    if show:
        plt.show()
    plt.close(fig)


def plot_descriptors_threads(
    samples: Sequence[ProcessSample],
    times: Sequence[float],
    *,
    show: bool = True,
    save_path: str | None = None,
    dpi: int = 144,
    transparent: bool = False,
    theme: Theme = "light",
):
    apply_style(theme=theme)
    fig, ax = plt.subplots(figsize=(9, 4))
    ax.plot(times, [s.descriptors.open_files for s in samples], label="Open files")
    ax.plot(times, [s.descriptors.fds for s in samples], label="FDs")
    ax.plot(times, [s.threads.threads for s in samples], label="Threads")
    ax.set_ylabel("Count")
    ax.set_xlabel("Time (s)")
    _finalize(fig, ax, title="Descriptors and Threads")
    if save_path:
        fig.savefig(save_path, dpi=dpi, bbox_inches="tight", transparent=transparent)
    if show:
        plt.show()
    plt.close(fig)


def plot_from_extended(
    samples: Sequence[ProcessSample],
    times: Sequence[float],
    out_dir: str | None = None,
    *,
    show: bool = True,
    dpi: int = 144,
    theme: Theme = "light",
    ext: str = "png",
):
    """Convenience to render a suite of plots from extended samples."""
    cpu_path = f"{out_dir}/cpu_components.{ext}" if out_dir else None
    mem_path = f"{out_dir}/memory_breakdown.{ext}" if out_dir else None
    io_path = f"{out_dir}/io_cumulative.{ext}" if out_dir else None
    ctx_path = f"{out_dir}/ctx_switches.{ext}" if out_dir else None
    dt_path = f"{out_dir}/descriptors_threads.{ext}" if out_dir else None
    dist_path = f"{out_dir}/distributions.{ext}" if out_dir else None
    corr_path = f"{out_dir}/corr_heatmap.{ext}" if out_dir else None

    plot_cpu_components(
        samples, times, show=show, save_path=cpu_path, dpi=dpi, theme=theme
    )
    plot_memory_breakdown(
        samples, times, show=show, save_path=mem_path, dpi=dpi, theme=theme
    )
    plot_io_bytes_cumulative(
        samples, times, show=show, save_path=io_path, dpi=dpi, theme=theme
    )
    plot_ctx_switches(
        samples, times, show=show, save_path=ctx_path, dpi=dpi, theme=theme
    )
    plot_descriptors_threads(
        samples, times, show=show, save_path=dt_path, dpi=dpi, theme=theme
    )
    plot_distributions(samples, show=show, save_path=dist_path, dpi=dpi, theme=theme)
    plot_correlation_heatmap(
        samples, show=show, save_path=corr_path, dpi=dpi, theme=theme
    )


def plot_distributions(
    samples: Sequence[ProcessSample],
    *,
    show: bool = True,
    save_path: str | None = None,
    dpi: int = 144,
    theme: Theme = "light",
):
    """Plot histogram/KDE distributions for CPU%, RSS MB, and VMS MB."""
    apply_style(theme=theme)
    fig, axes = plt.subplots(1, 3, figsize=(12, 3.8))

    cpu = [s.cpu.process for s in samples]
    rss = [s.memory.rss for s in samples]
    vms = [s.memory.vms for s in samples]

    sns.histplot(cpu, kde=True, ax=axes[0])
    axes[0].set_title("CPU % (per core)")
    sns.histplot(rss, kde=True, ax=axes[1])
    axes[1].set_title("RSS (MB)")
    sns.histplot(vms, kde=True, ax=axes[2])
    axes[2].set_title("VMS (MB)")

    for ax in axes:
        ax.grid(True, linestyle="--", linewidth=0.6)
        ax.set_xlabel("")
        ax.set_ylabel("Count")

    fig.suptitle("Distributions of Key Metrics", y=1.02)
    fig.tight_layout()
    if save_path:
        fig.savefig(save_path, dpi=dpi, bbox_inches="tight")
    if show:
        plt.show()
    plt.close(fig)


def plot_correlation_heatmap(
    samples: Sequence[ProcessSample],
    *,
    show: bool = True,
    save_path: str | None = None,
    dpi: int = 144,
    theme: Theme = "light",
):
    """Compute numeric correlation across extended metrics and render a heatmap."""
    apply_style(theme=theme)
    rows = [s.model_dump() for s in samples]
    df = pd.json_normalize(rows)
    num_df = df.select_dtypes(include=["number"]).copy()

    rename = {
        "cpu.percent": "cpu% (per-core)",
        "cpu.user": "cpu_user",
        "cpu.system": "cpu_system",
        "memory.rss": "rss_mb",
        "memory.vms": "vms_mb",
        "ctx.voluntary": "ctx_vol",
        "ctx.involuntary": "ctx_invol",
    }
    num_df = num_df.rename(columns=rename)
    corr = num_df.corr(numeric_only=True)

    fig, ax = plt.subplots(figsize=(7, 6))

    sns.heatmap(corr, cmap="vlag", center=0, annot=False, ax=ax)

    ax.set_title("Correlation Heatmap (Numeric Metrics)")
    fig.tight_layout()
    if save_path:
        fig.savefig(save_path, dpi=dpi, bbox_inches="tight")
    if show:
        plt.show()
    plt.close(fig)
