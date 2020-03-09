
import datetime
import dateutil.parser

class task:
    def __init__(self, taskName, assignee, startDate, startMessageTemplate):
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

    def __str__(self):
        return self.assignee +\
            " - " + self.taskName +\
            " - " + str(self.startDate)
