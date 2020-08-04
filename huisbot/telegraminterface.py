import logging
from telegram.ext import Updater, CommandHandler
from telegram import Bot
import json
import threading
import time
import datetime
import dateutil.parser
import calendar
import dateutil.relativedelta

from houseDataManagement import *
from task import task
from perpetualTimer import perpetualTimer


# check active tasks every x seconds
updateSpeed = 1
# I don't like it but houses are global for the 
# handler methods to access
# I bet there's a proper way to do it but idk
telegramHouses = []

def getToken():
    # FIXME ignore newline
    file = open("./token.txt", "r")
    token = file.read()
    return token


# Handlers

def handleActiveTasks():
    # TODO: move logic into house class?
    global telegramHouses
    for house in telegramHouses:
        for task in house.tasks:
            if (task.getSecondsToGo() <= 0):
                bot.send_message(chat_id=house.chatId,
                                 text=task.getStartMessage())
                taskIndex = house.tasks.index(task)
                del house.tasks[taskIndex]


def welcome(update, context):
    global telegramHouses
    chatId = update.message.chat_id
    currentHouse = getHouse(telegramHouses, update.message.chat_id)
    if currentHouse == None:
        update.message.reply_text("No house exists here!")
        return
    welcomeText = currentHouse.welcomeMessage
    update.message.reply_text(welcomeText, parse_mode="Markdown")

'''
def debug(update, context):
    currentHouse = getHouse(update.message.chat_id)
    if currentHouse == None:
        update.message.reply_text("No house exists here!")
        return
    returntext = ""
    returntext += str(currentHouse.chatId) + "\n"
    returntext += str(currentHouse.welcomeMessage) + "\n"
    returntext += "------------------------\n"
    returntext += json.dumps(currentHouse.taskSeedList, indent=2)
    update.message.reply_text(returntext)
'''
'''
def reload(update, context):
    global houses
    houses = []
    houses = loadHousesFromFile()
'''
'''
def updateHouse(update, context):
    global houses
    chatId = update.message.chat_id
    returnString = ""

    input = update.message.text
    splitInput = input.split(' ', 1)  # split into command and the rest
    if len(splitInput) < 2:
        returnString += "Not enough input! Add a welcome message."
        update.message.reply_text(returnString)
        return
    welcomeMessage = splitInput[1]

    for existinghouse in houses:
        if existinghouse.chatId == chatId:
            returnString += "House already exists! Only editing welcome text.\n"
            indexOfExistingHouse = houses.index(existinghouse)
            houses[indexOfExistingHouse].welcomeMessage = welcomeMessage
            update.message.reply_text(returnString)
            return
        else:
            returnString += "Starting new house.\n"

    newHouse = house(chatId, welcomeMessage, [])
    houses.append(newHouse)
    returnString += "bot creation successful."
    update.message.reply_text(returnString)
    saveHousesToFile(houses)
'''
'''
def updateTask(update, context):
    currentHouse = getHouse(update.message.chat_id)
    if currentHouse == None:
        update.message.reply_text("No house exists here!")
        return
    input = update.message.text
    splitInput = input.split(' ', 1)  # split into command and the rest
    if len(splitInput) < 2:
        update.message.reply_text("Not enough input. Add a task seed.")
        return
    taskSeedText = splitInput[1]
    # TODO: validate json input
    taskSeedDictionary = json.loads(taskSeedText)
    returnString = ""
    for task in currentHouse.taskSeedList:
        if task["taskName"] == taskSeedDictionary["taskName"]:
            returnString += "Removing existing task first"
            currentHouse.taskSeedList.remove(task)
            update.message.reply_text(returnString)
    currentHouse.taskSeedList.append(taskSeedDictionary)
    currentHouse.reloadTasks()
    update.message.reply_text("Added task")
    saveHousesToFile(houses)
'''
'''
def status(update, context):
    currentHouse = getHouse(update.message.chat_id)
    if currentHouse == None:
        update.message.reply_text("No house exists here!")
        return

    maximumTasks = 20
    statusString = ""
    statusString += "The following tasks are planned:\n"
    for task in currentHouse.tasks:
        startdate = str(task.startDate)
        statusString += ("%s will do %s starting at %s\n" %
                         (task.assignee, task.taskName, startdate))
        maximumTasks -= 1
        if maximumTasks < 0:
            break
    update.message.reply_text(statusString)
'''

def help(update, context):
    update.message.reply_text(
        "/welcome\n/status\n/initiate\n/task")


def error(update, context):
    logger.warning('Update "%s" caused error "%s"', update, context.error)


bot = Bot(getToken())
updater = Updater(bot=bot, use_context=True)
timer = perpetualTimer(updateSpeed, handleActiveTasks)

class telegramInterface (threading.Thread):
    def __init__(self):
        self.stopFlag = False
        self.reloadFlag = False
        dp = updater.dispatcher
        dp.add_error_handler(error)

        dp.add_handler(CommandHandler("help", help))
        dp.add_handler(CommandHandler("welcome", welcome))
        threading.Thread.__init__(self)

    def run(self):
        timer.start()
        updater.start_polling()
        while not self.stopFlag:
            if (self.reloadFlag):
                self.reloadFlag = False
                # None None is ugly but I dont think python has method overloading :/
                # also maybe the solution here is removing the /reload command but
                # that's a problem for future me
                
                #reload(None, None)
                # Lol maybe get rid of the entire concept of reloading
                # hmmm thread safety tho

        updater.stop()
        timer.cancel()


