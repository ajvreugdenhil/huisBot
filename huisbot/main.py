#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from telegram.ext import Updater, CommandHandler
from telegram import Bot
import json
from threading import Timer, Thread, Event
import time
import datetime
import dateutil.parser
import calendar
import dateutil.relativedelta

from task import task
from perpetualTimer import perpetualTimer

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

def getToken():
    file = open("./token.txt", "r")
    token = file.read()
    return token

# Settings 
# folder for the users' data
housesFileLocation = "./userData/"
# check active tasks every x seconds
updateSpeed = 1
# days to plan ahead
planAheadTime = 15

# House shit

def getHouse(chatId):
    global houses
    for house in houses:
        if house.chatId == chatId:
            return house
    return None

class house:
    def __init__(self, chatId, welcomeMessage = "Welcome!", taskSeedList = []):
        self.chatId = chatId
        self.welcomeMessage = welcomeMessage
        self.taskSeedList = taskSeedList
        self.tasks = []
        self.initializeTasks()

    def addStaticTaskSeed(self, taskSeed):
        for instance in taskSeed["instances"]:
            taskToBeBuilt = task(taskSeed["taskName"],
                                instance["assignee"],
                                instance["startDate"],
                                taskSeed["startMessage"])
            if (taskToBeBuilt.getSecondsToGo() > 0):
                self.tasks.append(taskToBeBuilt)

    def addGeneratorTaskSeed(self, taskSeed):
        global planAheadTime
        assigneeCount = len(taskSeed["assignees"])
        seedStartDate = dateutil.parser.parse(taskSeed["startDate"])
        seedInterval = datetime.timedelta(seconds=taskSeed["interval"])
        i = 0
        while seedStartDate + datetime.timedelta(seedInterval.days * i) < datetime.datetime.now() + datetime.timedelta(days=planAheadTime):
            taskToBeBuilt = task(taskSeed["taskName"],
                                taskSeed["assignees"][i % assigneeCount],
                                instance["startDate"],
                                taskSeed["startMessage"])
            if (taskToBeBuilt.getSecondsToGo() > 0):
                self.tasks.append(taskToBeBuilt)
            #i += seedInterval
            i += 1

    def initializeTasks(self):
        for seed in self.taskSeedList:
            # TODO: check if taskname already exists
            if seed["type"] == "static":
                self.addStaticTaskSeed(seed)
            elif seed["type"] == "generated":
                #self.addGeneratorTaskSeed(seed)
                print("NOT IMPLEMENTED sorry for not throwing exception or whatev")
            else:
                raise ValueError("bad task seed data")
    
    def reloadTasks(self):
        self.tasks = []
        self.initializeTasks()

    def toString(self):
        return self.chatId




# Data importation code

def getJsonFromFile(filename):
    file = open(housesFileLocation + filename, "r")
    taskText = file.read()
    return json.loads(taskText)

def loadHousesFromFile(filename = "houses.json"):
    housesdict = getJsonFromFile(filename)
    result = []
    for houseData in housesdict:
        # TODO check house data for validity
        newHouse = house(houseData["chatId"], houseData["welcomeMessage"], houseData["taskSeeds"])
        result.append(newHouse)
    return result



# Handlers

def handleActiveTasks():
    global houses
    for house in houses:
        for task in house.tasks:
            if (task.getSecondsToGo() <= 0):
                bot.send_message(chat_id=house.chatId, text=task.getStartMessage())
                taskIndex = house.tasks.index(task)
                del house.tasks[taskIndex]

def welcome(update, context):
    chatId = update.message.chat_id
    welcomeText = getHouse(chatId).welcomeMessage
    update.message.reply_text(welcomeText, parse_mode="Markdown")

def debug(update, context):
    print(update.message.chat_id)
    pass

def status(update, context):
    house = getHouse(update.message.chat_id)
    #house.reloadTasks()
    print(house.chatId)
    print("______________")
    print(house.taskSeedList)
    print("______________")
    print(house.tasks[0].toString())


def help(update, context):
    update.message.reply_text(
        "Commands: \n/start [file [filename] | wip ] to (re)load tasks. \n/help for help \n/status for status")


def error(update, context):
    logger.warning('Update "%s" caused error "%s"', update, context.error)


# Global variables
houses = []
bot = Bot(getToken())
updater = Updater(bot=bot, use_context=True)
timer = perpetualTimer(updateSpeed, handleActiveTasks)



# Main
def main():
    global houses
    houses = loadHousesFromFile()
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("debug", debug))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("welcome", welcome))
    dp.add_handler(CommandHandler("status", status, pass_args=True))
    dp.add_error_handler(error)

    timer.start()

    updater.start_polling()
    updater.idle()

    timer.cancel()


if __name__ == '__main__':
    main()
