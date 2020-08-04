import json
import dateutil.parser
import calendar
import dateutil.relativedelta
import datetime

from task import task
from perpetualTimer import perpetualTimer

# folder for the users' data
housesFileLocation = "./userData/"
# days to plan ahead
planAheadTime = 31

class house:
    def __init__(self, chatId, welcomeMessage, taskSeedList):
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
        
        while seedStartDate + datetime.timedelta(seconds=(seedInterval.total_seconds() * i)) < datetime.datetime.now() + datetime.timedelta(days=planAheadTime):
            j = 0
            for subtask in taskSeed["subtasks"]:
                startDate = str(
                    seedStartDate + datetime.timedelta(seconds=(seedInterval.total_seconds() * i)))
                taskname = taskSeed["taskName"] + ":" + subtask["taskName"]
                if len(taskSeed["subtasks"]) == 1:
                    taskname = subtask["taskName"]
                assignee = "everyone"
                if assigneeCount > 0:
                    assignee = taskSeed["assignees"][(j + (assigneeCount - i - 1)) % assigneeCount]
                taskToBeBuilt = task(taskname,
                                     assignee,
                                     startDate,
                                     subtask["startMessage"])
                if (taskToBeBuilt.getSecondsToGo() > 0):
                    self.tasks.append(taskToBeBuilt)
                j += 1
            i += 1
            if i > 200:
                return

    def initializeTasks(self):
        for seed in self.taskSeedList:
            for task in self.tasks:
                if task.taskName == seed["taskName"]:
                    raise "Task already exists!"
            if seed["type"] == "static":
                self.addStaticTaskSeed(seed)
            elif seed["type"] == "generated":
                self.addGeneratorTaskSeed(seed)
            else:
                raise ValueError("bad task seed data")
        self.tasks.sort(key=lambda task: task.startDate)

    def reloadTasks(self):
        self.tasks = []
        self.initializeTasks()

    def __str__(self):
        return str(self.chatId)

def getHouse(houses, chatId):
    for house in houses:
        if house.chatId == chatId:
            return house
    return None


# Data importation and exportation

def getJsonFromFile(filename):
    file = open(housesFileLocation + filename, "r")
    taskText = file.read()
    return json.loads(taskText)

def loadHousesFromFile(filename="houses.json"):
    housesdict = getJsonFromFile(filename)
    result = []
    for houseData in housesdict:
        # FIXME: check house data for validity
        newHouse = house(
            houseData["chatId"], houseData["welcomeMessage"], houseData["taskSeeds"])
        result.append(newHouse)
    return result

def saveHousesToFile(newHouses, filename="houses.json"):
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
