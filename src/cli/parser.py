from argparse import ArgumentParser

from loguru import logger


def get_params():
    parser = ArgumentParser()

    parser.add_argument("--pid", action="store", nargs=1, type=int)
    parser.add_argument("--interval", action="store", nargs=1, type=int)
    parser.add_argument("--out", action="store", nargs=1, type=str)
    args = parser.parse_args()

    logger.info("Arguments Parsed:")
    logger.info(f"pid: {args.pid[0]}")
    logger.info(f"interval: {args.interval[0]}")
    logger.info(f"out: {args.out[0] if args.out else ''}")

    return args
