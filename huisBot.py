#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from telegram.ext import Updater, CommandHandler
from telegram import Bot
import json
from threading import Timer
import time

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

def getToken():
    file = open("token.txt", "r") 
    token = file.read()
    return token

bot = Bot(getToken())
updater = Updater(bot=bot, use_context=True)
started = False
#scheduler = sched.scheduler(time.time, time.sleep)

# Task code

# dict info:
'''
    taskName
    assignee
    startTime
    startMessage
    stopTime
    stopMessage
    reminderInterval
    reminderMessage
'''

def getTaskList():
    file = open("tasks.txt", "r")
    taskText = file.read()
    return json.loads(taskText)


# Handlers

def notify(chat_id, task):
    message = "I am once again reminding " + task["assignee"] + " to do " + task["taskName"]
    bot.send_message(chat_id=chat_id, text=message)

def start(update, context):
    update.message.reply_text("The bot is starting!")
    
    chat_id = update.message.chat_id
    started = True
    tasks = getTaskList()
    for task in tasks:
        startTime = task["startTime"]
        currentTime = time.time()
        timeDifference = startTime - currentTime
        t = Timer(timeDifference, notify, kwargs={'chat_id': chat_id, 'task': task})
        t.start()

def set_timer(update, context):
    pass

def error(update, context):
    logger.warning('Update "%s" caused error "%s"', update, context.error)


# Main

def main():
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start,
                                  pass_args=True,
                                  pass_job_queue=True,
                                  pass_chat_data=True))
    dp.add_handler(CommandHandler("set", set_timer,
                                  pass_args=True,
                                  pass_job_queue=True,
                                  pass_chat_data=True))
    dp.add_error_handler(error)
    updater.start_polling()
    
    updater.idle()

if __name__ == '__main__':
    main()