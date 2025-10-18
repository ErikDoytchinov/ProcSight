from argparse import ArgumentParser

from loguru import logger


def get_params():
    parser = ArgumentParser()

    parser.add_argument("--pid", action="store", type=int)
    parser.add_argument("--interval", action="store", type=int)
    parser.add_argument("--duration", action="store", type=int, default=0)
    parser.add_argument("--samples", action="store", type=int, default=0)
    parser.add_argument("--out", action="store", type=str)
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

    logger.info("Arguments Parsed:")
    logger.info(f"pid: {args.pid}")
    logger.info(f"interval: {args.interval}")
    logger.info(f"duration: {args.duration}")
    logger.info(f"samples: {args.samples}")
    logger.info(f"out: {args.out}")
    logger.info(f"save-plots: {getattr(args, 'save_plots', None)}")
    logger.info(f"dpi: {getattr(args, 'dpi', None)}")
    logger.info(f"no-show: {getattr(args, 'no_show', False)}")
    logger.info(f"extended: {getattr(args, 'extended', False)}")

    return args
