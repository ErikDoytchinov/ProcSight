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
    logger.info(f"extended: {getattr(args, 'extended', False)}")

    return args
