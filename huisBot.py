#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from telegram.ext import Updater, CommandHandler
from telegram import Bot
import json
from threading import Timer
import time
import datetime
import dateutil.parser

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


def getToken():
    file = open("token.txt", "r")
    token = file.read()
    return token


tasks = []
bot = Bot(getToken())
updater = Updater(bot=bot, use_context=True)
started = False

# Task code


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

    def setTimer(self):
        if (self.getSecondsToGo() > 0):
            self.timer = Timer(self.getSecondsToGo(),
                               notify, kwargs={'task': self})
            self.timer.start()
            self.active = True
        else:
            self.active = False

    def toString(self):
        return self.assignee +\
            " will do " + self.taskName +\
            " at " + str(self.startDate.year) +\
            "/" + str(self.startDate.month) +\
            "/" + str(self.startDate.day)


def getTasksFromFile(filename):
    file = open(filename, "r")
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
            taskToBeBuilt.setTimer()
            tasks.append(taskToBeBuilt)


# Handlers

def notify(task):
    global tasks
    bot.send_message(chat_id=task.chat_id, text=task.getStartMessage())
    taskIndex = tasks.index(task)
    del tasks[taskIndex]


def start(update, context):
    global tasks
    global started
    if (len(tasks) > 0):
        for task in tasks:
            task.timer.cancel()
        del tasks[:]

    if (started):
        update.message.reply_text("The bot is already started. reloading.")
    else:
        update.message.reply_text("The bot is starting!")

    chat_id = update.message.chat_id
    started = True
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
        update.message.send_text("Invalid argument. Use /help for syntax")


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
        "Commands: \n/start [file | wip | wip] to (re)load tasks. \n/help for help \n/status for status")


def error(update, context):
    logger.warning('Update "%s" caused error "%s"', update, context.error)


# Main
def main():
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("help", help))
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
