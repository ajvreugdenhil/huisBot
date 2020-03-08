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
    file = open(userFileLocation + "token.txt", "r")
    token = file.read()
    return token

# Settings
# folder for the users' data
userFileLocation = "./userData/"
# check active tasks every x seconds
updateSpeed = 1
# days to plan ahead
planAheadTime = 15


# Task importation code

def getJsonFromFile(filename):
    file = open(userFileLocation + filename, "r")
    taskText = file.read()
    return json.loads(taskText)

def addStaticTaskSeed(chat_id, taskSeed):
    global tasks
    for instance in taskSeed["instances"]:
        taskToBeBuilt = task(chat_id,
                             taskSeed["taskName"],
                             instance["assignee"],
                             instance["startDate"],
                             taskSeed["startMessage"])
        if (taskToBeBuilt.getSecondsToGo() > 0):
            tasks.append(taskToBeBuilt)

def addGeneratorTaskSeed(chat_id, taskSeed):
    global tasks
    global planAheadTime
    assigneeCount = len(taskSeed["assignees"])
    seedStartDate = dateutil.parser.parse(taskSeed["startDate"])
    seedInterval = datetime.timedelta(seconds=taskSeed["interval"])
    i = 0
    while seedStartDate + datetime.timedelta(seedInterval.days * i) < datetime.datetime.now() + datetime.timedelta(days=planAheadTime):
        taskToBeBuilt = task(chat_id,
                             taskSeed["taskName"],
                             taskSeed["assignees"][i % assigneeCount],
                             instance["startDate"],
                             taskSeed["startMessage"])
        if (taskToBeBuilt.getSecondsToGo() > 0):
            tasks.append(taskToBeBuilt)
        #i += seedInterval
        i += 1

def importTasksFromFile(chat_id, filename):
    newtaskdata = getJsonFromFile(filename)
    seeds = newtaskdata["taskSeeds"]
    for seed in seeds:
        if seed["type"] == "static":
            pass
            addStaticTaskSeed(chat_id, seed)
        elif seed["type"] == "generated":
            addGeneratorTaskSeed(chat_id, seed)
        else:
            raise ValueError("bad task seed data")


# Handlers

def handleActiveTasks():
    global tasks
    for task in tasks:
        if (task.getSecondsToGo() <= 0):
            bot.send_message(chat_id=task.chat_id, text=task.getStartMessage())
            taskIndex = tasks.index(task)
            del tasks[taskIndex]

def welcome(update, context):
    file = open(userFileLocation + "welcome.txt", "r")
    welcomeText = file.read()
    update.message.reply_text(welcomeText, parse_mode="Markdown")


def debug(update, context):
    pass

def start(update, context):
    global tasks
    global started
    global timer
    if (len(tasks) > 0):
        del tasks[:]

    chat_id = update.message.chat_id
    logging.info("")
    # Get the way the system should import the tasks
    mode = ""
    if (len(context.args) == 0):
        mode = "file"
    else:
        # FIXME: check the arg
        mode = context.args[0]
    if (mode == "file"):
        if (len(context.args) == 2):
            importTasksFromFile(chat_id, context.args[1])
        else:
            importTasksFromFile(chat_id, "tasks.json")
    else:
        update.message.send_text("Invalid argument. Use /help for syntax.")

    if (started):
        update.message.reply_text("The bot was already started. Reloaded.")
    else:
        update.message.reply_text("The bot is starting!")
        #actually start the timer for checking active tasks
        timer.start()
        started = True


def status(update, context):
    global started
    global tasks
    if not started:
        update.message.reply_text("Bot is inactive")
    else:
        response = "Bot is active. " + str(len(tasks)) + " active task(s).\n"
        for task in tasks:
            response += task.toString() + "\n"
        update.message.reply_text(response)


def help(update, context):
    update.message.reply_text(
        "Commands: \n/start [file [filename] | wip ] to (re)load tasks. \n/help for help \n/status for status")


def error(update, context):
    logger.warning('Update "%s" caused error "%s"', update, context.error)


# Global variables
tasks = []
bot = Bot(getToken())
updater = Updater(bot=bot, use_context=True)
started = False
timer = perpetualTimer(updateSpeed, handleActiveTasks)

# Main
def main():
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("debug", debug))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("welcome", welcome))
    dp.add_handler(CommandHandler("status", status))
    dp.add_handler(CommandHandler("start", start,
                                  pass_args=True,
                                  pass_job_queue=True,
                                  pass_chat_data=True))
    #dp.add_error_handler(error)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
