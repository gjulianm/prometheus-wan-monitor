import logging
import coloredlogs


def configure_log(args=None, loglevel=None):
    """Configures the log output format.

    :param args: what argparse returned.
    :param loglevel: it must be a logging level or None.
    """
    extra_debug_format = ""

    if not loglevel:
        if args is not None and args.verbose:
            loglevel = logging.DEBUG
        else:
            loglevel = logging.INFO

    if logging.DEBUG == loglevel:
        extra_debug_format = "(%(module)s.%(funcName)s:%(lineno)d) "

    log_format = "[ %(asctime)s %(levelname)s ] " + \
        extra_debug_format + "%(message)s"

    logging.captureWarnings(True)

    coloredlogs.install(level=loglevel, fmt=log_format)
