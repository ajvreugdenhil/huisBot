#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import logging
import datetime
import dateutil.parser
import calendar
import dateutil.relativedelta
import time

from task import task
from perpetualTimer import perpetualTimer
import telegraminterface
import webinterface
from houseDataManagement import *

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

# Main
def main():
    global houses
    houses = loadHousesFromFile()
    t = telegraminterface.telegramInterface()
    logging.info("starting")
    t.start()
    logging.info("started")
    time.sleep(2)
    logging.info("stopping")
    t.stopFlag = True
    t.join()
    logging.info("stopped")

if __name__ == '__main__':
    main()
