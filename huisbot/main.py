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
planAheadTime = 5


# House logic

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

    # FIXME
    def addGeneratorTaskSeed(self, taskSeed):
        global planAheadTime
        assigneeCount = len(taskSeed["assignees"])
        seedStartDate = dateutil.parser.parse(taskSeed["startDate"])
        seedInterval = datetime.timedelta(seconds=taskSeed["interval"])
        print(seedInterval)
        i = 0
        while seedStartDate + datetime.timedelta(seconds=(seedInterval.total_seconds() * i )) < datetime.datetime.now() + datetime.timedelta(days=planAheadTime):
            j = 0
            for subtask in taskSeed["subtasks"]:
                startDate = str(seedStartDate + datetime.timedelta(seconds=(seedInterval.total_seconds() * i )))
                print(startDate)
                taskToBeBuilt = task(taskSeed["taskName"] + ":" + subtask["taskName"],
                                    taskSeed["assignees"][(i + j) % assigneeCount],
                                    startDate,
                                    subtask["startMessage"])
                if (taskToBeBuilt.getSecondsToGo() > 0):
                    self.tasks.append(taskToBeBuilt)
                j += 1
            i += 1
            if i > 50:
                return

    def initializeTasks(self):
        for seed in self.taskSeedList:
            # TODO: check if taskname already exists
            if seed["type"] == "static":
                self.addStaticTaskSeed(seed)
            elif seed["type"] == "generated":
                self.addGeneratorTaskSeed(seed)
            else:
                raise ValueError("bad task seed data")
    
    def reloadTasks(self):
        self.tasks = []
        self.initializeTasks()

    def __str__(self):
        return str(self.chatId)




# Data importation and exportation

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

def saveHousesToFile(newHouses, filename = "houses.json"):
    result = []
    for house in newHouses:
        houseDict = {}
        houseDict["chatId"] = house.chatId
        houseDict["welcomeMessage"] = house.welcomeMessage
        houseDict["taskSeeds"] = house.taskSeedList
        result.append(houseDict)
    resultAsJson = json.dumps(result, indent=4)
    file = open(housesFileLocation + filename, "w")
    file.write(resultAsJson)





# Handlers

def handleActiveTasks():
    # FIXME move logic into house class
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
    global houses
    saveHousesToFile(houses)
    loadHousesFromFile()

def reload(update, context):
    print("reloading")
    global houses
    houses = []
    houses = loadHousesFromFile()

def updateHouse(update, context):
    raise NotImplemented
    
def updateTask(update, context):
    raise NotImplemented

def status(update, context):
    house = getHouse(update.message.chat_id)
    if house == None:
        update.message.reply_text("No house exists here!")
        return

    maximumTasks = 20
    statusString = ""
    statusString += "The following tasks are planned:\n"
    for task in house.tasks:
        startdate = str(task.startDate)
        statusString += ("%s will do %s at %s\n" % (task.assignee, task.taskName, startdate))
        maximumTasks -= 1
        if maximumTasks < 0:
            break
    update.message.reply_text(statusString)


def help(update, context):
    update.message.reply_text(
        "WIP")


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
    dp.add_handler(CommandHandler("debug", debug, pass_args=True))
    dp.add_handler(CommandHandler("reload", reload, pass_args=True))
    dp.add_error_handler(error)

    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("welcome", welcome))
    dp.add_handler(CommandHandler("status", status, pass_args=True))
    dp.add_handler(CommandHandler("initiate", updateHouse, pass_args=True))
    dp.add_handler(CommandHandler("task", updateTask, pass_args=True))
    

    timer.start()
    updater.start_polling()
    updater.idle()
    timer.cancel()


if __name__ == '__main__':
    main()
