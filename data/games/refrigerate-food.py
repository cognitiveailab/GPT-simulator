# refridgerate-food.py
# based on make-ice-cubes.py
### peter jansen (feb 15/2023)

# Task: Create a micro-simulation that models how to use a fridge to prevent food from spoiling.
# Environment: emergency room
# Task-critical Objects: Fridge, FoodItem, Counter
# High-level object classes: Container (Fridge, Counter), Device (Fridge)
# Critical properties: minTemperature (Fridge), tempDecreasePerTick (Fridge), temperature (GameObject), spoilTime (FoodItem), maxTemperature (FoodItem, the max temperature that prevent the food from spoiling), timeAboveMaxTemp (FoodItem, number of ticks that the food in placed in a high temperature environment), isSpoiled (FoodItem), isAboveMaxTemp (FoodItem)
# Actions: look, inventory, examine, take/put object, open/close container, turn on/off device, use X on Y
# Distractor Items: None
# Distractor Actions: use X on Y
# High-level solution procedure: take all food, open the fridge, put all food in fridge, close fridge, wait till the game won

import random

UUID = 0
randomSeed = 0
#
# Abstract class for all game objects
#
class GameObject():
    def __init__(self, name):
        # Prevent this constructor from running if it's already been run during multiple inheritance
        if hasattr(self, "constructorsRun"):
            return
        # Otherwise, keep a list of constructors that have already been run
        self.constructorsRun = ["GameObject"]
        global UUID
        self.uuid = UUID
        UUID += 1

        self.name = f"{name} (ID: {self.uuid})"
        self.parentContainer = None
        self.contains = []
        self.properties = {}

        # Set critical properties
        self.properties["isContainer"] = False    # By default, objects are not containers
        self.properties["isMoveable"] = True     # By default, objects are moveable
        self.properties["temperature"] = 20.0   # Initialize everything to have a starting temperature of 20 degrees C

    # Get a property of the object (safely), returning None if the property doesn't exist
    def getProperty(self, propertyName):
        if propertyName in self.properties:
            return self.properties[propertyName]
        else:
            return None

    # Add an object to this container, removing it from its previous container
    def addObject(self, obj):
        obj.removeSelfFromContainer()
        self.contains.append(obj)
        obj.parentContainer = self

    # Remove an object from this container
    def removeObject(self, obj):
        self.contains.remove(obj)
        obj.parentContainer = None

    # Remove the current object from whatever container it's currently in
    def removeSelfFromContainer(self):
        if self.parentContainer != None:
            self.parentContainer.removeObject(self)

    # Get all contained objects, recursively
    def getAllContainedObjectsRecursive(self):
        outList = []
        for obj in self.contains:
            # Add self
            outList.append(obj)
            # Add all contained objects
            outList.extend(obj.getAllContainedObjectsRecursive())
        return outList

    # Get all contained objects that have a specific name (not recursively)
    def containsItemWithName(self, name):
        foundObjects = []
        for obj in self.contains:
            if obj.name == name:
                foundObjects.append(obj)
        return foundObjects

    # Game tick: Perform any internal updates that need to be performed at each step of the game.
    def tick(self):
        pass

    # Get a list of referents (i.e. names that this object can be called by)
    def getReferents(self):
        return [self.name]

    # Make a human-readable string that describes this object
    def makeDescriptionStr(self, makeDetailed=False):
        return self.name


#
#   Abstract Game-object Classes
#


# Abstract class for things that can be considered 'containers' (e.g. a drawer, a box, a table, a shelf, etc.)
class Container(GameObject):
    def __init__(self, name):
        # Prevent this constructor from running if it's already been run during multiple inheritance
        if hasattr(self, "constructorsRun"):
            if "Container" in self.constructorsRun:
                return

        GameObject.__init__(self, name)
        # Otherwise, mark this constructor as having been run
        self.constructorsRun.append("Container")
        # Set critical properties
        self.properties["isContainer"] = True
        self.properties["isOpenable"] = False  # Can the container be opened (e.g. a drawer, a door, a box, etc.), or is it always 'open' (e.g. a table, a shelf, etc.)
        self.properties["isOpen"] = True      # Is the container open or closed (if it is openable)
        self.properties["containerPrefix"] = "in" # The prefix to use when referring to the container (e.g. "in the drawer", "on the table", etc.)

    # Try to open the container
    # Returns an observation string, and a success flag (boolean)
    def openContainer(self):
        # First, check to see if this object is openable
        if not self.getProperty("isOpenable"):
            # If not, then it can't be opened
            return ("The " + self.name + " can't be opened.", False)

        # If this object is openable, then check to see if it is already open
        if self.getProperty("isOpen"):
            # If so, then it can't be opened
            return ("The " + self.name + " is already open.", False)

        # If this object is openable and it is closed, then open it
        self.properties["isOpen"] = True
        return ("The " + self.name + " is now open.", True)

    # Try to close the container
    # Returns an observation string, and a success flag (boolean)
    def closeContainer(self):
        # First, check to see if this object is openable
        if not (self.getProperty("isOpenable") == True):
            # If not, then it can't be closed
            return ("The " + self.name + " can't be closed.", False)

        # If this object is openable, then check to see if it is already closed
        if not (self.getProperty("isOpen") == True):
            # If so, then it can't be closed
            return ("The " + self.name + " is already closed.", False)

        # If this object is openable and it is open, then close it
        self.properties["isOpen"] = False
        return ("The " + self.name + " is now closed.", True)

    # Try to place the object in a container.
    # Returns an observation string, and a success flag (boolean)
    def placeObjectInContainer(self, obj):
        # First, check to see if this object is a container
        if not (self.getProperty("isContainer") == True):
            # If not, then it can't be placed in a container
            return ("The " + self.name + " is not a container, so things can't be placed there.", False)

        # Check to see if the object is moveable
        if not (obj.getProperty("isMoveable") == True):
            # If not, then it can't be removed from a container
            return ("The " + obj.name + " is not moveable.", None, False)

        # If this object is a container, then check to see if it is open
        if not (self.getProperty("isOpen") == True):
            # If not, then it can't be placed in a container
            return ("The " + self.name + " is closed, so things can't be placed there.", False)

        # If this object is a container and it is open, then place the object in the container
        self.addObject(obj)
        return ("The " + obj.getReferents()[0] + " is placed in the " + self.name + ".", True)

    # Try to remove the object from a container.
    # Returns an observation string, a reference to the object being taken, and a success flag (boolean)
    def takeObjectFromContainer(self, obj):
        # First, check to see if this object is a container
        if not (self.getProperty("isContainer") == True):
            # If not, then it can't be removed from a container
            return ("The " + self.name + " is not a container, so things can't be removed from it.", None, False)

        # Check to see if the object is moveable
        if not (obj.getProperty("isMoveable") == True):
            # If not, then it can't be removed from a container
            return ("The " + obj.name + " is not moveable.", None, False)

        # If this object is a container, then check to see if it is open
        if not (self.getProperty("isOpen") == True):
            # If not, then it can't be removed from a container
            return ("The " + self.name + " is closed, so things can't be removed from it.", None, False)

        # Check to make sure that the object is contained in this container
        if obj not in self.contains:
            return ("The " + obj.name + " is not contained in the " + self.name + ".", None, False)

        # If this object is a container and it is open, then remove the object from the container
        obj.removeSelfFromContainer()
        return ("The " + obj.getReferents()[0] + " is removed from the " + self.name + ".", obj, True)

    # Set the temperature of anything in the container to be closer to the temperature of the container.
    # This functionally simulates heat transfer between the container and the objects inside it.
    def tick(self):
        # Get a list of all objects in the fridge
        objectsInContainer = self.getAllContainedObjectsRecursive()

        maxTempChangePerTick = 5.0      # Maximum temperature change per tick
        # Change the objects in the container's temperature to be closer to the containers temperature
        for obj in objectsInContainer:
            # Case 1: The object's temperature is higher than the container's temperature
            if (obj.properties["temperature"] > self.properties["temperature"]):
                # Decrease the object's temperature, down to the container's temperature
                newTemperature = obj.properties["temperature"] - maxTempChangePerTick
                if (newTemperature < self.properties["temperature"]):
                    newTemperature = self.properties["temperature"]
                obj.properties["temperature"] = newTemperature

            # Case 2: The object's temperature is lower than the container's temperature
            elif (obj.properties["temperature"] < self.properties["temperature"]):
                # Increase the object's temperature, up to the container's temperature
                newTemperature = obj.properties["temperature"] + maxTempChangePerTick
                if (newTemperature > self.properties["temperature"]):
                    newTemperature = self.properties["temperature"]
                obj.properties["temperature"] = newTemperature


    # Make a human-readable string that describes this object
    def makeDescriptionStr(self, makeDetailed=False):
        return "the " + self.name + "."


# Abstract class for anything that can be considered a device that turns on or off (e.g. a light, a fan, a TV, etc.)
class Device(GameObject):
    def __init__(self, name):
        # Prevent this constructor from running if it's already been run during multiple inheritance
        if hasattr(self, "constructorsRun"):
            if "Device" in self.constructorsRun:
                return
        GameObject.__init__(self, name)
        # Otherwise, mark this constructor as having been run
        self.constructorsRun.append("Device")
        # Set critical properties
        self.properties["isDevice"] = True
        self.properties["isActivatable"] = True # Can this device be turned on or off?
        self.properties["isOn"] = False         # Is the device currently on or off?

    # Try to turn on the device.
    # Returns an observation string, and a success flag (boolean)
    def turnOn(self):
        # If the device isn't activatable, then return an error
        if (self.getProperty("isActivatable") == False):
            return ("It's not clear how the " + self.getReferents()[0] + " could be turned on.", False)

        # If the device is already on, then return an error
        if self.properties["isOn"]:
            return ("The " + self.getReferents()[0] + " is already on.", False)
        else:
            self.properties["isOn"] = True
            return ("The " + self.getReferents()[0] + " is now turned on.", True)

    # Try to turn off the device.
    # Returns an observation string, and a success flag (boolean)
    def turnOff(self):
        # If the device isn't activatable, then return an error
        if (self.getProperty("isActivatable") == False):
            return ("It's not clear how the " + self.getReferents()[0] + " could be turned off.", False)

        # If the device is already off, then return an error
        if not self.properties["isOn"]:
            return ("The " + self.getReferents()[0] + " is already off.", False)
        else:
            self.properties["isOn"] = False
            return ("The " + self.getReferents()[0] + " is now turned off.", True)

    # Try to use the device with a patient object (e.g. a light with a person, a fan with a person, etc.)
    # Returns an observation string, and a success flag (boolean)
    def useWithObject(self, patientObject):
        return ("You're not sure how to use the " + self.getReferents()[0] + " with the " + patientObject.name + ".", False)

    # Make a human-readable string that describes this object
    def makeDescriptionStr(self, makeDetailed=False):
        outStr = "The " + self.name + ", which is currently "
        if self.properties["isOn"]:
            outStr += "on."
        else:
            outStr += "off."
        return outStr


#
#   Specific Game Objects
#

# A fridge, which is a cooling device.  It contains things inside of it.  It's always on.  When things are inside it, it cools them down to some temperature.
class Fridge(Container, Device):
    def __init__(self):
        GameObject.__init__(self, "fridge")
        Container.__init__(self, "fridge")
        Device.__init__(self, "fridge")

        self.properties["containerPrefix"] = "in"

        # Set the properties of this object
        self.properties["isOpenable"] = True    # A fridge is openable
        self.properties["isOpen"] = False       # A fridge starts out closed
        self.properties["isMoveable"] = False   # A fridge is too heavy to move (and doesn't really need to be moved for this simulation)

        self.properties["isOn"] = True           # A frridge is always on
        self.properties["isActivatable"] = False # A fridge essentially never is turned off (unless it's unplugged, which is irelevant for this simulation)

        # Set critical properties
        self.properties["minTemperature"] = 4.0        # Minimum temperature of the fridge (in degrees Celsius)
        self.properties["tempDecreasePerTick"] = 5.0   # How much the temperature decreases per tick (in degrees Celsius)

    # Decrease the temperature of anything inside the fridge
    def tick(self):
        # If the fridge is on, then decrease the temperature of anything inside it
        if (self.properties["isOn"] == True):
            # Let's also add fidelity and say the temperature will only decrease if the fridge is closed
            if (self.properties["isOpen"] == False):

                # Get a list of all objects in the fridge
                objectsOnStove = self.getAllContainedObjectsRecursive()

                # Decrease the temperature of each object in the fridge
                for obj in objectsOnStove:
                    # Decrease the object's temperature, down to the maximum temperature
                    newTemperature = obj.properties["temperature"] - self.properties["tempDecreasePerTick"]
                    if (newTemperature < self.properties["minTemperature"]):
                        newTemperature = self.properties["minTemperature"]
                    # Set the object's new temperature
                    obj.properties["temperature"] = newTemperature

    # Make a human-readable string that describes this object
    def makeDescriptionStr(self, makeDetailed=False):
        outStr = f"a {self.name}"

        # A freezer is essentially always on, so we'll only mention it if it's off
        if not self.properties["isOn"]:
            outStr += " that is currently off, and"

        # Check if open
        if self.properties["isOpen"]:
            outStr += " that is currently open"
            # Check if empty
            effectiveContents = []
            for obj in self.contains:
                effectiveContents.append(obj.makeDescriptionStr())

            if (len(effectiveContents) > 0):
                outStr += " that looks to have "
                for i in range(len(effectiveContents)):
                    if (i == len(effectiveContents) - 1) and (len(effectiveContents) > 1):
                        outStr += "and "
                    outStr += effectiveContents[i] + ", "
                outStr = outStr[:-2] + " " + self.properties["containerPrefix"] + " it"
            else:
                outStr += " that is empty"

        else:
            outStr += " that is currently closed"

        return outStr

# A food item, which is a type of object that can be eaten.  The food has a certain amount of time before it spoils.
class FoodItem(GameObject):
    def __init__(self, foodPrefix, foodName, spoilTime=20):
        GameObject.__init__(self, foodName)
        self.properties["foodPrefix"] = foodPrefix  # The prefix to use when referring to the food item (e.g. "a", "some", "the", etc.)

        # Set critical properties
        self.properties["isFood"] = True
        self.properties["spoilTime"] = spoilTime    # How long the food item lasts before it spoils (in steps)
        self.properties["maxTemperature"] = 4.0     # Maximum temperature of the food item (in degrees Celsius).  If the food item is hotter than this, it will eventually spoil.
        self.properties["timeAboveMaxTemp"] = 0     # How long the food item has been above the maximum temperature (in steps)
        self.properties["isSpoiled"] = False        # Whether the food item is spoiled or not
        self.properties["isAboveMaxTemp"] = True    # Whether the food item is above the maximum temperature or not (helpful for scoring)

    # Tick the food item
    def tick(self):
        # Check to see if the food item is above the maximum temperature
        if (self.properties["temperature"] > self.properties["maxTemperature"]):
            self.properties["isAboveMaxTemp"] = True
        else:
            self.properties["isAboveMaxTemp"] = False

        # If the food item is above the maximum temperature, then increase the time it's been above the maximum temperature
        if (self.properties["isAboveMaxTemp"] == True):
            self.properties["timeAboveMaxTemp"] += 1

        # If the food item has been above the maximum temperature for too long, then it spoils
        if (self.properties["timeAboveMaxTemp"] > self.properties["spoilTime"]):
            self.properties["isSpoiled"] = True

    # Get a list of referents (i.e. names that this object can be called by)
    def getReferents(self):
        referents = []
        # Add the food item's potentially spoiled property as a prefix
        if (self.properties["isSpoiled"]):
            referents.append("spoiled " + self.name)
        referents.append(self.name)
        return referents

    # Make a human-readable string that describes this object
    def makeDescriptionStr(self, makeDetailed=False):
        outStr = self.properties["foodPrefix"] + " "
        if (self.properties["isSpoiled"]):
            outStr += "spoiled "
        outStr += self.name

        return outStr


# A counter, which is a type of container that can be used to put things on
class Counter(Container):
    # Constructor.
    def __init__(self):
        GameObject.__init__(self, "counter")
        Container.__init__(self, "counter")

        self.properties["containerPrefix"] = "on"
        # Set the properties of this object
        self.properties["isOpenable"] = False # A counter pit is a flat surface that can't be closed (i.e always open)
        self.properties["isMoveable"] = False # A counter is too heavy to move

    def makeDescriptionStr(self, makeDetailed=False):
        outStr = f"a {self.name}"

        effectiveContents = []
        for obj in self.contains:
            effectiveContents.append(obj.makeDescriptionStr())

        if (len(effectiveContents) > 0):
            outStr += " that looks to have "
            for i in range(len(effectiveContents)):
                if (i == len(effectiveContents) - 1) and (len(effectiveContents) > 1):
                    outStr += "and "
                outStr += effectiveContents[i] + ", "
            outStr = outStr[:-2] + " " + self.properties["containerPrefix"] + " it"
        else:
            outStr += " that is empty"

        return outStr


# TODO: Add any Distractor items



# The world is the root object of the game object tree.  In single room environments, it's where all the objects are located.
class World(Container):
    def __init__(self):
        Container.__init__(self, "kitchen")

    def makeDescriptionStr(self, makeDetailed=False):
        outStr = "You find yourself in a kitchen.  In the kitchen, you see: \n"
        for obj in self.contains:
            outStr += "\t" + obj.makeDescriptionStr() + "\n"

        return outStr


# The agent (just a placeholder for a container for the inventory)
class Agent(Container):
    def __init__(self):
        GameObject.__init__(self, "agent")
        Container.__init__(self, "agent")

    def getReferents(self):
        return ["yourself"]

    def makeDescriptionStr(self, makeDetailed=False):
        return "yourself"


class TextGame:

    def __init__(self, randomSeed):
        # Random number generator, initialized with a seed passed as an argument
        self.random = random.Random(randomSeed)
        # Reset global UUID
        global UUID
        UUID = 0
        # The agent/player
        self.agent = Agent()
        # Game Object Tree
        self.rootObject = self.initializeWorld()
        # Game score
        self.score = 0
        self.numSteps = 0
        # Game over flag
        self.gameOver = False
        self.gameWon = False
        # Last game observation
        self.observationStr = self.rootObject.makeDescriptionStr()
        # Do calculate initial scoring
        self.calculateScore()

    # Create/initialize the world/environment for this game
    def initializeWorld(self):
        world = World()

        # Add the agent
        world.addObject(self.agent)

        # Add a fridge
        fridge = Fridge()
        world.addObject(fridge)

        # Add a counter
        counter = Counter()
        world.addObject(counter)

        # Create foods
        possibleFoods = []
        possibleFoods.append(FoodItem("some", "apple sauce", spoilTime=20))
        possibleFoods.append(FoodItem("some", "yogurt", spoilTime=20))
        possibleFoods.append(FoodItem("a bottle of", "orange juice", spoilTime=20))
        possibleFoods.append(FoodItem("a bottle of", "pineapple juice", spoilTime=20))
        possibleFoods.append(FoodItem("a bottle of", "soy milk", spoilTime=20))
        possibleFoods.append(FoodItem("a jar of", "jam", spoilTime=20))

        # Randomly shuffle the foods
        self.random.shuffle(possibleFoods)

        # Add a few random foods
        numFoods = self.random.randint(1, 3)
        for i in range(numFoods):
            # Choose the next food
            food = possibleFoods[i % len(possibleFoods)]
            # Add the food to the fridge
            counter.addObject(food)

        # Store the number of foods that need to be put in the fridge, for scoring
        self.numFoodsToPutInFridge = numFoods

        # Return the world
        return world

    # Get the task description for this game
    def getTaskDescription(self):
        return "Your task is to prevent the foods from spoiling."

    # Make a dictionary whose keys are object names (strings), and whose values are lists of object references with those names.
    # This is useful for generating valid actions, and parsing user input.
    def makeNameToObjectDict(self):
        # Get a list of all game objects
        allObjects = self.rootObject.getAllContainedObjectsRecursive()

        # Make a dictionary whose keys are object names (strings), and whose values are lists of object references with those names.
        nameToObjectDict = {}
        for obj in allObjects:
            for name in obj.getReferents():
                #print("Object referent: " + name)
                if name in nameToObjectDict:
                    nameToObjectDict[name].append(obj)
                else:
                    nameToObjectDict[name] = [obj]

        return nameToObjectDict

    #
    #   Action generation
    #

    def addAction(self, actionStr, actionArgs):
        # Check whether the action string key already exists -- if not, add a blank list
        if not (actionStr in self.possibleActions):
            self.possibleActions[actionStr] = []
        # Add the action arguments to the list
        self.possibleActions[actionStr].append(actionArgs)

    # Returns a list of valid actions at the current time step
    def generatePossibleActions(self):
        # Get a list of all game objects that could serve as arguments to actions
        allObjects = self.makeNameToObjectDict()

        # Make a dictionary whose keys are possible action strings, and whose values are lists that contain the arguments.
        self.possibleActions = {}

        # Actions with zero arguments
        # (0-arg) Look around the environment
        self.addAction("look around", ["look around"])
        self.addAction("look", ["look around"])

        # (0-arg) Look at the agent's current inventory
        self.addAction("inventory", ["inventory"])

        # Actions with one object argument
        # (1-arg) Eat
        for objReferent, objs in allObjects.items():
            for obj in objs:
                self.addAction("eat " + objReferent, ["eat", obj])

        # (1-arg) Take
        for objReferent, objs in allObjects.items():
            for obj in objs:
                self.addAction("take " + objReferent, ["take", obj])
                self.addAction("take " + objReferent + " from " + obj.parentContainer.getReferents()[0], ["take", obj])

        # (1-arg) Open/Close
        for objReferent, objs in allObjects.items():
            for obj in objs:
                self.addAction("open " + objReferent, ["open", obj])
                self.addAction("close " + objReferent, ["close", obj])

        # (1-arg) Detailed look/examine
        for objReferent, objs in allObjects.items():
            for obj in objs:
                self.addAction("examine " + objReferent, ["examine", obj])

        # (1-arg) Turn on/Turn off device
        for objReferent, objs in allObjects.items():
            for obj in objs:
                self.addAction("turn on " + objReferent, ["turn on", obj])
                self.addAction("turn off " + objReferent, ["turn off", obj])

        # Actions with two object arguments
        # (2-arg) Put
        for objReferent1, objs1 in allObjects.items():
            for objReferent2, objs2 in allObjects.items():
                for obj1 in objs1:
                    for obj2 in objs2:
                        if (obj1 != obj2):
                            containerPrefix = "in"
                            if obj2.properties["isContainer"]:
                                containerPrefix = obj2.properties["containerPrefix"]
                            self.addAction("put " + objReferent1 + " " + containerPrefix + " " + objReferent2, ["put", obj1, obj2])

        # (2-arg) Use
        ## OMIT, UNUSED (make ice cubes)
        for objReferent1, objs1 in allObjects.items():
            for objReferent2, objs2 in allObjects.items():
                for obj1 in objs1:
                    for obj2 in objs2:
                        if (obj1 != obj2):
                            self.addAction("use " + objReferent1 + " on " + objReferent2, ["use", obj1, obj2])


        return self.possibleActions

    #
    #   Interpret actions
    #

    # Describe the room that the agent is currently in
    def actionLook(self):
        return self.agent.parentContainer.makeDescriptionStr()

    # Perform the "eat" action.  Returns an observation string.
    def actionEat(self, obj):
        # Enforce that the object must be in the inventory to do anything with it
        if (obj.parentContainer != self.agent):
            return "You don't currently have the " + obj.getReferents()[0] + " in your inventory."

        # Check if the object is food
        if (obj.getProperty("isFood") == True):
            # Try to pick up/take the food
            obsStr, objRef, success = obj.parentContainer.takeObjectFromContainer(obj)
            if (success == False):
                # If it failed, we were unable to take the food (e.g. it was in a closed container)
                return "You can't see that."

            # Update the game observation
            outStr = "You eat the " + obj.name + "."
            del obj
            return outStr
        else:
            return "You can't eat that."

    # Open a container
    def actionOpen(self, obj):
        # Check if the object is a container
        if (obj.getProperty("isContainer") == True):
            # This is handled by the object itself
            obsStr, success = obj.openContainer()
            return obsStr
        else:
            return "You can't open that."

    # Close a container
    def actionClose(self, obj):
        # Check if the object is a container
        if (obj.getProperty("isContainer") == True):
            # This is handled by the object itself
            obsStr, success = obj.closeContainer()
            return obsStr
        else:
            return "You can't close that."

    # Take an object from a container
    def actionTake(self, obj):
        # If the object doesn't have a parent container, then it's dangling and something has gone wrong
        if (obj.parentContainer == None):
            return "Something has gone wrong -- that object is dangling in the void.  You can't take that."

        # Cannot take the agent
        if type(obj) == Agent:
            return "You cannot take yourself."
        
        # Take the object from the parent container, and put it in the inventory
        obsStr, objRef, success = obj.parentContainer.takeObjectFromContainer(obj)
        if (success == False):
            return obsStr

        # Add the object to the inventory
        self.agent.addObject(obj)
        return obsStr + " You put the " + obj.getReferents()[0] + " in your inventory."

    # Put an object in a container
    def actionPut(self, objToMove, newContainer):
        # Check that the destination container is a container
        if (newContainer.getProperty("isContainer") == False):
            return "You can't put things in the " + newContainer.getReferents()[0] + "."

        # Enforce that the object must be in the inventory to do anything with it
        if (objToMove.parentContainer != self.agent):
            return "You don't currently have the " + objToMove.getReferents()[0] + " in your inventory."

        # Take the object from it's current container, and put it in the new container.
        # Deep copy the reference to the original parent container, because the object's parent container will be changed when it's taken from the original container
        originalContainer = objToMove.parentContainer
        obsStr1, objRef, success = objToMove.parentContainer.takeObjectFromContainer(objToMove)
        if (success == False):
            return obsStr1

        # Put the object in the new container
        obsStr2, success = newContainer.placeObjectInContainer(objToMove)
        if (success == False):
            # For whatever reason, the object can't be moved into the new container. Put the object back into the original container
            originalContainer.addObject(objToMove)
            return obsStr2

        # Success -- show both take and put observations
        return obsStr1 + "\n" + obsStr2


    # Display agent inventory
    def actionInventory(self):
        # Get the inventory
        inventory = self.agent.contains
        # If the inventory is empty, return a message
        if (len(inventory) == 0):
            return "Your inventory is empty."
        # Otherwise, return a list of the inventory items
        else:
            obsStr = "You have the following items in your inventory:\n"
            for obj in inventory:
                obsStr += "\t" + obj.makeDescriptionStr() + "\n"
            return obsStr

    ## OMIT, UNUSED (refridgerate food)
    def actionTurnOn(self, obj):
        # Check if the object is a device
        if (obj.getProperty("isDevice") == True):
            # This is handled by the object itself
            obsStr, success = obj.turnOn()
            return obsStr
        else:
            return "You can't turn on that."

    ## OMIT, UNUSED (refridgerate food)
    def actionTurnOff(self, obj):
        # Check if the object is a device
        if (obj.getProperty("isDevice") == True):
            # This is handled by the object itself
            obsStr, success = obj.turnOff()
            return obsStr
        else:
            return "You can't turn off that."

    ## OMIT, UNUSED (refridgerate food)
    def actionUse(self, deviceObj, patientObject):
        # Check if the object is a device
        if (deviceObj.getProperty("isDevice") == True):
            # This is handled by the object itself
            obsStr, success = deviceObj.useWithObject(patientObject)
            return obsStr
        else:
            return "You can't use that."



    # Performs an action in the environment, returns the result (a string observation, the reward, and whether the game is completed).
    def step_action(self, actionStr):
        self.observationStr = ""
        reward = 0

        # Check to make sure the action is in the possible actions dictionary
        if actionStr not in self.possibleActions:
            self.observationStr = "I don't understand that."
            return (self.observationStr, self.score, reward, self.gameOver, self.gameWon)

        self.numSteps += 1

        # Find the action in the possible actions dictionary
        actions = self.possibleActions[actionStr]
        action = None

        # Check for an ambiguous action (i.e. one that has multiple possible arguments)
        if (len(actions) > 1):
            # If there are multiple possible arguments, for now just choose the first one
            action = actions[0]
        else:
            # Otherwise, also just take the first action in the list of possible actions
            action = actions[0]

        # Interpret the action
        actionVerb = action[0]


        if (actionVerb == "look around"):
            # Look around the environment -- i.e. show the description of the world.
            self.observationStr = self.rootObject.makeDescriptionStr()
        elif (actionVerb == "inventory"):
            # Display the agent's inventory
            self.observationStr = self.actionInventory()

        elif (actionVerb == "examine"):
            # Examine an object
            thingToExamine = action[1]
            self.observationStr = thingToExamine.makeDescriptionStr(makeDetailed = True)
        elif (actionVerb == "eat"):
            # Eat a food
            thingToEat = action[1]
            self.observationStr = self.actionEat(thingToEat)
        elif (actionVerb == "open"):
            # Open a container
            thingToOpen = action[1]
            self.observationStr = self.actionOpen(thingToOpen)
        elif (actionVerb == "close"):
            # Close a container
            thingToClose = action[1]
            self.observationStr = self.actionClose(thingToClose)
        elif (actionVerb == "take"):
            # Take an object from a container
            thingToTake = action[1]
            self.observationStr = self.actionTake(thingToTake)
        elif (actionVerb == "turn on"):
            # Turn on a device
            thingToTurnOn = action[1]
            self.observationStr = self.actionTurnOn(thingToTurnOn)
        elif (actionVerb == "turn off"):
            # Turn off a device
            thingToTurnOff = action[1]
            self.observationStr = self.actionTurnOff(thingToTurnOff)

        elif (actionVerb == "put"):
            # Put an object in a container
            thingToMove = action[1]
            newContainer = action[2]
            self.observationStr = self.actionPut(thingToMove, newContainer)

        ## OMIT, UNUSED (make ice cubes)
        elif (actionVerb == "use"):
            # Use a device on an object
            deviceObj = action[1]
            patientObj = action[2]
            self.observationStr = self.actionUse(deviceObj, patientObj)


        # Catch-all
        else:
            self.observationStr = "ERROR: Unknown action."

    def step_tick(self):
        # Do one tick of the environment
        self.doWorldTick()

    def step_calculate_score(self):
        # Calculate the score
        lastScore = self.score
        self.calculateScore()
        reward = self.score - lastScore
        return reward

    def step(self, actionStr):
        self.step_action(actionStr)
        self.step_tick()
        reward = self.step_calculate_score()
        return (self.observationStr, self.score, reward, self.gameOver, self.gameWon)


    # Call the object update for each object in the environment
    def doWorldTick(self):
        # Get a list of all objects in the environment
        allObjects = self.rootObject.getAllContainedObjectsRecursive()
        # Loop through all objects, and call their tick()
        for obj in allObjects:
            obj.tick()

    # Calculate the game score
    def calculateScore(self):
        # Baseline score
        self.score = 0

        # Give a positive score for each food that's cooled, and a negative score for each food that's spoiled.
        # Also, give a negative score for each food that's missing (e.g. it's been eaten)
        numFoodsFound = 0
        numFoodsChanged = 0     # Foods modified (e.g. spoiled or cooled)
        allObjects = self.rootObject.getAllContainedObjectsRecursive()
        for obj in allObjects:
            # Check if the object is a food (i.e. an instance of the FoodItem class)
            if (isinstance(obj, FoodItem)):
                # Check if the food is spoiled
                if (obj.getProperty("isSpoiled") == True):
                    self.score -= 1
                    numFoodsChanged += 1
                # Otherwise, check if the food is cooled
                elif (obj.getProperty("isAboveMaxTemp") == False):
                    self.score += 1
                    numFoodsChanged += 1

                numFoodsFound += 1

        # Give a negative score for each food that's missing (e.g. it's been eaten)
        numFoodsMissing = self.numFoodsToPutInFridge - numFoodsFound
        self.score -= numFoodsMissing

        # Check if the game is over
        # Check for winning condition -- score is the same as the number of foods to put in the fridge
        if (self.score == self.numFoodsToPutInFridge):
            self.gameOver = True
            self.gameWon = True
        # Check for losing condition -- all foods changed, one or more foods are spoiled or missing
        elif ((numFoodsChanged + numFoodsMissing) >= self.numFoodsToPutInFridge):
            self.gameOver = True
            self.gameWon = False
        else:
            self.gameOver = False
            self.gameWon = False



# Main Program
def main():

    # Create a new game
    game = TextGame(randomSeed = randomSeed)

    # Get a list of valid actions
    possibleActions = game.generatePossibleActions()
    #print("Possible actions: " + str(possibleActions.keys()))
    print("Task Description: " + game.getTaskDescription())
    print("")
    print("Initial Observation: " + game.observationStr)
    print("")
    print("Type 'help' for a list of possible actions.")
    print("")


    # Main game loop
    #while not game.gameOver:
    while True:

        # Get the player's action
        actionStr = ""
        while ((len(actionStr) == 0) or (actionStr == "help")):
            actionStr = input("> ")
            if (actionStr == "help"):
                print("Possible actions: " + str(possibleActions.keys()))
                print("")
                actionStr = ""
            elif (actionStr == "exit") or (actionStr == "quit"):
                return

        # Perform the action
        observationStr, score, reward, gameOver, gameWon = game.step(actionStr)

        # Get a list of valid actions
        possibleActions = game.generatePossibleActions()

        # Print the current game state
        print("Observation: " + observationStr)
        print("")
        print("Current step: " + str(game.numSteps))
        print("Score: " + str(score))
        print("Reward: " + str(reward))
        print("Game Over: " + str(gameOver))
        print("Game Won: " + str(gameWon))
        print("")
        print("----------------------------------------")


# Run the main program
if __name__ == "__main__":
    main()

