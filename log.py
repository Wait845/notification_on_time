import logging
from logging import handlers
import os

LOG_FORMAT = logging.Formatter("%(levelname)s %(asctime)s %(pathname)s %(lineno)d %(message)s")
LOG_LEVEL = logging.DEBUG

logger = logging.getLogger("main logger")
logger.setLevel(LOG_LEVEL)

sh = logging.StreamHandler()
sh.setFormatter(LOG_FORMAT)

if not os.path.isdir("./logs"):
    os.mkdir("./logs")

th = handlers.TimedRotatingFileHandler(filename="./logs/nofitication.log", when="D", encoding="utf-8")
th.setFormatter(LOG_FORMAT)

logger.addHandler(sh)
logger.addHandler(th)

