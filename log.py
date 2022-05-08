#!/usr/bin/env python
# -*- encoding=utf8 -*-
import logging
import logging.handlers
from time import strftime
import os
import os.path as osp

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILENAME = strftime(osp.join(LOG_DIR, "cc-shoping_%Y_%m_%d_%H.log"))

name = "cc-shoping"
formatter = logging.Formatter('%(asctime)s %(filename)s：%(lineno)d %(levelname)s : %(message)s')

handler = logging.StreamHandler()
file_handler = logging.handlers.RotatingFileHandler(
    LOG_FILENAME, maxBytes=10485760, backupCount=5, encoding="utf-8")

file_handler.setFormatter(formatter)
handler.setFormatter(formatter)

logger = logging.getLogger(name)
logger.setLevel(logging.INFO)
logger.addHandler(handler)
logger.addHandler(file_handler)
