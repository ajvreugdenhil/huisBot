
import datetime
import dateutil.parser

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
