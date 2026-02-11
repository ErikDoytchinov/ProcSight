# ProcSight

![python](https://img.shields.io/badge/python-3.11%2B-blue)
![ruff](https://img.shields.io/badge/code%20style-ruff-5A9FD4)
![coverage](https://img.shields.io/badge/coverage-pytest--cov-lightgrey)
[![PyPI](https://img.shields.io/pypi/v/procsight?color=blue)](https://pypi.org/project/procsight/)
[
![license](https://img.shields.io/badge/license-MIT-green)
](./LICENSE)

Monitor and visualize a single process' resource usage (CPU, memory, I/O, context switches, threads, descriptors) with easy CSV export and publication‑ready plots.

Built on psutil, pandas, matplotlib, seaborn, and pydantic. Runs on macOS, Linux, and Windows.

## Features

- Track a running process by PID or by name (with interactive disambiguation)
- Sampling by fixed interval for a fixed duration, fixed number of samples, or continuously until Ctrl+C
- Two modes:
    - Basic: CPU per‑core percent and memory RSS/VMS
    - Extended: adds CPU breakdown, memory breakdown, I/O bytes, context switches, descriptors, threads, and process metadata
- Save plots to PNG/SVG/PDF with light/dark themes and configurable DPI
- Export measurements to CSV (includes an "avg" summary row)
- Clean programmatic API for integration in your own scripts/notebooks

## Requirements

- Python 3.11+
- Poetry (for development/packaging)
- Platforms: macOS, Linux, Windows (feature availability depends on OS and permissions)

Key dependencies (installed via Poetry): psutil, pandas, matplotlib, seaborn, pydantic, loguru, schedule.

## Installation (with Poetry)

```bash
# 1) Install Poetry if you don't have it
# macOS/Linux (official)
curl -sSL https://install.python-poetry.org | python3 -

# 2) Clone and install dependencies
git clone https://github.com/ErikDoytchinov/ProcSight.git
cd ProcSight
poetry install
```

If you prefer not to use Poetry, you can inspect `pyproject.toml` and install the listed dependencies with your own workflow.

## Quick start

Identify a PID you want to monitor, then run:

```bash
poetry run python main.py --pid 12345 --samples 60 --save-plots ./plots --no-show
```

- `--samples 60` collects exactly 60 samples
- `--save-plots ./plots` writes plots to the given directory
- `--no-show` avoids opening GUI windows (useful in headless/CI)

You can also select by name (first match or interactive if multiple):

```bash
poetry run python main.py --name python --duration 30 --interval 0.5 --save-plots ./plots
```

Extended mode (richer metrics + multiple plots):

```bash
poetry run python main.py --pid 12345 \
  --samples 120 --interval 0.5 \
  --extended --save-plots ./plots_ext --format svg --dpi 144 --theme dark --no-show
```

CSV export (basic or extended):

```bash
poetry run python main.py --pid 12345 --samples 30 --out out.csv --no-show
```

### Optional local workload generator

This repo includes a helper script to generate CPU/memory/I/O load in a single PID you can monitor:

```bash
chmod +x scripts/stress.sh
./scripts/stress.sh -d 60 -m 512 -i 128
# The script prints: PID=<pid>; use that value with --pid
```

## CLI reference

All options (from `procsight/cli/parser.py`):

- `--pid <int>`: PID of the process to monitor
- `--name <str>`: Process name to monitor (first matching process is used if `--pid` isn’t provided)
- `--interval <float>`: Sampling interval seconds (default: 1.0)
- `--duration <int>`: Run for N seconds (mutually exclusive with `--samples`). 0 means continuous until Ctrl+C
- `--samples <int>`: Collect exactly N samples (mutually exclusive with `--duration`). 0 defers to duration/continuous
- `--out <path>`: Path to CSV output file (optional)
- `--save-plots <dir>`: Directory to save plots (if omitted, plots are only shown unless `--no-show` is used)
- `--format {png,svg,pdf}`: Image format for saved plots (default: png)
- `--dpi <int>`: DPI for saved images (default: 144)
- `--transparent` (flag): Save figures with transparent background
- `--no-show` (flag): Do not display plots (useful in headless runs or CI)
- `--extended` (flag): Collect extended metrics (I/O, context switches, file descriptors, threads, meta)
- `--theme {light,dark}`: Plot theme (default: light)

Notes:

- You must provide either `--pid` or `--name`.
- If multiple processes match `--name`, you’ll be prompted to select one.

## Outputs

### Plots

- Basic mode saves up to two figures when `--save-plots` is provided:

    - `cpu_pid<PID>.<ext>` — CPU per‑core utilization over time
    - `mem_pid<PID>.<ext>` — Resident memory (RSS MB) over time

- Extended mode saves a suite of figures to the directory you provide:
    - `cpu_components.<ext>` — user/system/total CPU breakdown
    - `memory_breakdown.<ext>` — stacked RSS/Shared/Data/Text memory
    - `io_cumulative.<ext>` — cumulative I/O read/write MB
    - `ctx_switches.<ext>` — voluntary/involuntary context switches
    - `descriptors_threads.<ext>` — open files, file descriptors, threads
    - `distributions.<ext>` — histograms/KDEs of key metrics
    - `corr_heatmap.<ext>` — correlation heatmap across numeric metrics

Use `--theme dark` and `--transparent` for presentation‑friendly assets.

### CSV (via `--out <file>`)

- Basic mode columns: `sample, cpu_percent, rss_mb, vms_mb`
- Extended mode columns (subset shown; depends on OS support):
    - `sample, uptime_sec, status, cpu_percent, cpu_user, cpu_system, rss_mb, vms_mb, shared_mb, data_mb, text_mb, read_count, write_count, read_bytes, write_bytes, read_chars, write_chars, ctx_voluntary, ctx_involuntary, open_files, fds, threads, cpu_affinity`
- An extra final `avg` row is appended with numeric averages (non-numeric columns are ignored).

## Programmatic API

You can use ProcSight as a library in your own scripts:

```python
from procsight.core.monitor import Monitor
from procsight.visualization.plot import plot_cpu_usage, plot_memory_usage, plot_from_extended

m = Monitor(pid=12345, interval=0.5)
# Basic tuples: List[Tuple[CpuUsage, MemoryUsage]]
basic = m.get_process_usage_by_interval(duration=10, samples=0, extended=False)
# Extended samples: List[ProcessSample]
extended = m.get_process_usage_by_interval(duration=10, samples=0, extended=True)

# Plotting
plot_cpu_usage(basic, m.sample_times, show=True)
plot_memory_usage(basic, m.sample_times, show=True)
plot_from_extended(extended, m.sample_times, out_dir="./plots", show=False)
```

CSV export helper:

```python
from procsight.core.file_export import export_to_csv
export_to_csv(SimpleNamespace(extended=True, out="out.csv"), extended)
```

## Development

- Lint/format: Ruff is included. Run:
    ```bash
    poetry run ruff check .
    poetry run ruff format .  # optional if you enable Ruff formatter
    ```
- Tests + coverage:
    ```bash
    poetry run pytest
    # Coverage HTML report at htmlcov/index.html
    ```

Project layout uses `procsight/` with modules under:

- `procsight/core` — sampling, monitor, CSV export
- `procsight/models` — pydantic models for metrics
- `procsight/visualization` — plotting and themes
- `procsight/cli` — argument parsing

## Troubleshooting

- psutil permissions: some metrics (e.g., open files, affinity) may require elevated permissions or are unavailable on certain platforms; the tool falls back gracefully.
- Headless environments: use `--no-show` to suppress GUI popups and rely on `--save-plots`.
- Name matching finds multiple processes: the CLI will list matches and prompt for a selection.
- macOS security dialogs: accessing process info may trigger system prompts; grant access if needed.

## Acknowledgements

- [psutil](https://github.com/giampaolo/psutil)
- [pandas](https://pandas.pydata.org)
- [matplotlib](https://matplotlib.org)
- [seaborn](https://seaborn.pydata.org)
- [pydantic](https://docs.pydantic.dev)
- [loguru](https://github.com/Delgan/loguru)

## License

This project is licensed under the MIT License — see [LICENSE](./LICENSE) for details.
