from argparse import ArgumentParser, Namespace

import psutil
from loguru import logger


def get_params() -> Namespace:
    parser = ArgumentParser(
        description="Monitor and visualize a process' CPU and memory usage."
    )

    parser.add_argument(
        "--pid",
        action="store",
        type=int,
        help="PID of the process to monitor",
    )
    parser.add_argument(
        "--name",
        action="store",
        type=str,
        help="Process name to monitor (first matching process will be used if --pid is not provided)",
    )
    parser.add_argument(
        "--interval",
        action="store",
        type=float,
        default=1.0,
        help="Sampling interval in seconds (default: 1.0)",
    )
    parser.add_argument(
        "--duration",
        action="store",
        type=int,
        default=0,
        help="Run for N seconds (mutually exclusive with --samples). 0 means continuous until Ctrl+C",
    )
    parser.add_argument(
        "--samples",
        action="store",
        type=int,
        default=0,
        help="Collect exactly N samples (mutually exclusive with --duration). 0 uses duration/continuous",
    )
    parser.add_argument(
        "--out",
        action="store",
        type=str,
        help="Path to CSV output file (optional)",
    )
    parser.add_argument(
        "--save-plots",
        action="store",
        type=str,
        help="Directory path to save PNG plots (cpu.png, mem.png). If not set, plots are only shown unless --no-show is used.",
    )
    parser.add_argument(
        "--dpi",
        action="store",
        type=int,
        default=144,
        help="DPI for saved PNGs (default: 144)",
    )
    parser.add_argument(
        "--no-show",
        action="store_true",
        help="Do not display plots interactively (useful in headless runs or CI)",
    )
    parser.add_argument(
        "--extended",
        action="store_true",
        help="Collect extended metrics (IO, ctx switches, fds, threads, meta)",
    )
    args = parser.parse_args()

    if args.pid is None and not args.name:
        parser.error("You must provide either --pid or --name.")
    if args.pid is not None and args.pid < 0:
        parser.error("--pid must be a positive integer.")
    if args.interval <= 0:
        parser.error("--interval must be > 0.")
    if args.duration < 0 or args.samples < 0:
        parser.error("--duration and --samples must be >= 0.")
    if args.duration and args.samples:
        parser.error(
            "Provide only one of --duration or --samples (or neither for continuous mode)."
        )

    if args.pid is None and args.name:
        matches = []
        try:
            for proc in psutil.process_iter(attrs=["pid", "name", "cmdline"]):
                pname = proc.info.get("name") or ""
                if args.name.lower() in pname.lower():
                    cmd = " ".join(proc.info.get("cmdline") or [])
                    matches.append((proc.info["pid"], pname, cmd))
        except Exception:
            matches = []

        if not matches:
            parser.error(f"No running process found matching name: {args.name}")
        elif len(matches) == 1:
            args.pid = int(matches[0][0])
        else:
            print("Multiple processes matched:")
            for idx, (pid, pname, cmd) in enumerate(matches, start=1):
                display_cmd = f" - {cmd}" if cmd else ""
                print(f"[{idx}] pid={pid} name={pname}{display_cmd}")
            try:
                choice = int(input("Select a process by number: ").strip())
                if choice < 1 or choice > len(matches):
                    raise ValueError
                args.pid = int(matches[choice - 1][0])
            except Exception:
                parser.error("Invalid selection.")

    logger.info("Arguments Parsed:")
    logger.info(f"pid: {args.pid}")
    if getattr(args, "name", None):
        logger.info(f"name: {args.name}")
    logger.info(f"interval: {args.interval}")
    logger.info(f"duration: {args.duration}")
    logger.info(f"samples: {args.samples}")
    logger.info(f"out: {args.out}")
    logger.info(f"save-plots: {getattr(args, 'save_plots', None)}")
    logger.info(f"dpi: {getattr(args, 'dpi', None)}")
    logger.info(f"no-show: {getattr(args, 'no_show', False)}")
    logger.info(f"extended: {getattr(args, 'extended', False)}")

    return args
