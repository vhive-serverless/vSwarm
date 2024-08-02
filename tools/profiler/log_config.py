import logging

class CustomFormatter(logging.Formatter):

    blue = "\x1b[34;20m"
    green = "\x1b[32;20m"
    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    bold_red_white_bg = "\x1b[1;37;41m"
    reset = "\x1b[0m"
    format = "%(asctime)s - %(levelname)s - (%(filename)s:%(lineno)d) - %(message)s"

    FORMATS = {
        logging.DEBUG: grey + format + reset,
        logging.INFO: green + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red_white_bg + format + reset,
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


log = logging.getLogger("Benchmark")
log.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setFormatter(CustomFormatter())
log.addHandler(ch)

def setLogLevel(level: str) -> None:
    if (level == "INFO"): log.setLevel(logging.INFO)
    elif (level == "DEBUG"): log.setLevel(logging.DEBUG)