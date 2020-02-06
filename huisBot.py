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

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

def getToken():
    file = open(userFileLocation + "token.txt", "r")
    token = file.read()
    return token

# Classes

class perpetualTimer():
   def __init__(self,t,method):
      self.t=t
      self.method = method
      self.thread = Timer(self.t,self.handle_function)

   def handle_function(self):
      self.method()
      self.thread = Timer(self.t,self.handle_function)
      self.thread.start()

   def start(self):
      self.thread.start()

   def cancel(self):
      self.thread.cancel()


class task:
    def __init__(self, chat_id, taskName, assignee, startDate, startMessageTemplate):
        self.chat_id = chat_id
        self.taskName = taskName
        self.assignee = assignee
        self.startDate = dateutil.parser.parse(startDate)
        self.startMessageTemplate = startMessageTemplate
        self.active = False

    def getStartMessage(self):
        startMessage = self.startMessageTemplate.replace(
            "{assignee}", self.assignee)
        return startMessage

    def getSecondsToGo(self):
        currentDate = datetime.datetime.now()
        timeDifference = (self.startDate - currentDate).total_seconds()
        return timeDifference

    def toString(self):
        return self.assignee +\
            " will do " + self.taskName +\
            " at " + str(self.startDate.year) +\
            "/" + str(self.startDate.month) +\
            "/" + str(self.startDate.day)


# Settings
# folder for the users' data
userFileLocation = "./userData/"
# check active tasks every x seconds
updateSpeed = 5


# Task importation code

def getTasksFromFile(filename):
    file = open(userFileLocation + filename, "r")
    taskText = file.read()
    return json.loads(taskText)


def startTasksFromFile(chat_id, filename="tasks.json"):
    global tasks
    newtaskdata = getTasksFromFile(filename)
    newtasks = newtaskdata["instances"]
    for newtask in newtasks:
        taskToBeBuilt = task(chat_id,
                             newtaskdata["taskName"],
                             newtask["assignee"],
                             newtask["startDate"],
                             newtaskdata["startMessage"])
        if (taskToBeBuilt.getSecondsToGo() > 0):
            tasks.append(taskToBeBuilt)
    

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
    
    # Get the way the system should import the tasks
    mode = ""
    if (len(context.args) == 0):
        mode = "file"
    else:
        # FIXME: check the arg
        mode = context.args[0]
    if (mode == "file"):
        if (len(context.args) == 2):
            startTasksFromFile(chat_id, context.args[1])
        else:
            startTasksFromFile(chat_id)
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
    dp.add_error_handler(error)
    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
