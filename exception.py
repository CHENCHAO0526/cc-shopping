#!/usr/bin/env python
# -*- encoding=utf8 -*-
from log import logger


class CCShoppingException(Exception):

    def __init__(self, message):
        super().__init__(message)
        logger.error(message)
