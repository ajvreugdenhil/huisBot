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

from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


@app.route('/<groupid>')
def index(groupid):
    allHouses = telegraminterface.telegramHouses
    house = getHouse(allHouses, int(groupid))
    if house == None:
        return "oopsie woopsie we made a fucky wucky"
    else:
        return render_template('index.html', tasks=house.tasks, seed=json.dumps(house.taskSeedList, indent=1), groupid = groupid)

@app.route('/submit', methods = ['POST'])
def submit():
    groupid = request.form["groupid"]
    # TODO: verify key request.form['key']
    # FIXME: verify json
    
    found = False
    for house in telegraminterface.telegramHouses:
        if house.chatId == int(groupid):
            house.taskSeedList = json.loads(request.form['seedData'])
            house.reloadTasks()
            saveHousesToFile(telegraminterface.telegramHouses)
            found = True
    if (not found):
        return "Oh fuck"
    else:
        return redirect(url_for("index", groupid=groupid))

# Main
def main():
    houses = loadHousesFromFile()
    telegraminterface.telegramHouses = houses
    t = telegraminterface.telegramInterface()
    
    t.start()
    '''
    logging.info("starting")
    
    logging.info("started")
    time.sleep(2)
    logging.info("stopping")
    t.stopFlag = True
    t.join()
    logging.info("stopped")
    '''
    app.run(debug=True, port=5000, use_reloader=False)

if __name__ == '__main__':
    main()
