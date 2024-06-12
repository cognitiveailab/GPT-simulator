# wash-clothes.py
# based on dishwasher.py
# ruoyao wang (feb 19/2023)

# Task: Create a micro-simulation that models how to wash clothes with a washing machine and dry clothes with a dryer.
# Environment: room
# Task-critical Objects: WashingMachine, Dryer, Clothes, DetergentBottle, Detergent, Container, Basket
# High-level object classes: Device (WashingMachine, Dryer, DetergentBottle), Container (WashingMachine, Dryer, Basket)
# Critical properties: isDirty (Clothes), isWet (Clothes), cycleStage(WashingMachine, Dryer)
# Actions: look, inventory, wait, examine, take/put objects, open/close containers, turn on/off devices, use X on Y
# Distractor Items: None
# Distractor Actions: None
# High-level solution procedure: put dirty clothes into the washing machine, add detergent, turn on washing machine, wait for cycle to finish, put wet clothes into the dryer, turn on dryer, wait for cycle to finish, put all clothes into the basket


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

# A washing machine, which is a device that can hold clothes.  When it's turned on, it washes the clothes (changes them from dirty to clean)
# as long as it has detergent in it.  If it doesn't have detergent in it, then it doesn't change them from dirty to clean.
class WashingMachine(Container, Device):
    def __init__(self):
        GameObject.__init__(self, "washing machine")
        Container.__init__(self, "washing machine")
        Device.__init__(self, "washing machine")

        # Set the properties of this object
        self.properties["isOpenable"] = True  # A washing machine is openable
        self.properties["isOpen"] = False     # A washing machine is closed by default
        self.properties["isMoveable"] = False # A washing machine is too heavy to move (and doesn't really need to be moved for this simulation)
        # Set critical properties
        self.properties["cycleStage"] = 0     # The current stage of the washing machine's cycle.  0 = not running, 1 = washing, 2 = finished
        self.properties["finishedCycle"] = False  # Set to True when the washing machine has finished washing the dishes.  Reset when it's open.

    # Try to turn on the washing machine.
    # Returns an observation string, and a success flag (boolean)
    def turnOn(self):
        # The washing machine can't be turned on if it's opened
        if self.properties["isOpen"]:
            return ("The " + self.name + " is opened, so it can't be turned on.", False)

        # Otherwise, turn on the dishwasher
        return Device.turnOn(self)


    def tick(self):
        # If the washing machine is opened, then it automatically turns off and resets
        if (self.properties["isOpen"] == True):
            self.properties["isOn"] = False
            self.properties["finishedCycle"] = False
            self.properties["cycleStage"] = 0

        # If the washing machine is on, then wash the dishes
        if (self.properties["isOn"] == True):
            # Increment the cycle stage
            if (self.properties["cycleStage"] < 3):
                self.properties["cycleStage"] += 1

            # Check for stage 1
            if self.properties["cycleStage"] == 2:
                # Check to see if there is detergent in the washing machine
                containsDetergent = False
                for obj in self.getAllContainedObjectsRecursive():
                    if type(obj) == Detergent:
                        containsDetergent = True
                        break

                # If there is detergent in the dishwasher, then wash the clothes
                if containsDetergent:
                    for obj in self.getAllContainedObjectsRecursive():
                        if (type(obj) == Clothes):
                            obj.properties['isDirty'] = False

                # Remove any detergent from the washing machine
                for obj in self.getAllContainedObjectsRecursive():
                    if type(obj) == Detergent:
                        obj.removeSelfFromContainer() # Disappears

                # Clothes become wet no matter there is detergent or not
                for obj in self.getAllContainedObjectsRecursive():
                    if type(obj) == Clothes:
                        obj.properties['isWet'] = True

            # Check for stage 2
            elif self.properties["cycleStage"] == 3:
                # Set the washer to finished
                self.properties["finishedCycle"] = True
                self.properties["cycleStage"] = 0
                # Turn off dishwasher
                self.turnOff()

        else:
            # If the washing machine is off, then don't wash the clothes
            pass

    def makeDescriptionStr(self, makeDetailed=False):
        outStr = f"a {self.name}"
        # Check if finished a cycle
        if self.properties["finishedCycle"]:
            outStr += " with a blinking green light"

        if self.properties["isOn"]:
            outStr += " that is currently on"
        else:
            # Check if open
            if self.properties["isOpen"]:
                outStr += " that is currently open"
                # Check if empty
                if len(self.contains) == 0:
                    outStr += " and empty"
                else:
                    if not makeDetailed:
                        outStr += " and contains one or more items."
                    else:
                        outStr += " and contains the following items: \n"
                        for obj in self.contains:
                            outStr += "\t" + obj.makeDescriptionStr() + "\n"
            else:
                outStr += " that is currently closed"

        return outStr

# A dryer, which is a device that can hold clothes.  When it's turned on, it dries the clothes (changes them from wet to dry)
class Dryer(Container, Device):
    def __init__(self):
        GameObject.__init__(self, "dryer")
        Container.__init__(self, "dryer")
        Device.__init__(self, "dryer")

        # Set the properties of this object
        self.properties["isOpenable"] = True  # A dryer is openable
        self.properties["isOpen"] = False     # A dryer is closed by default
        self.properties["isMoveable"] = False # A dryer is too heavy to move (and doesn't really need to be moved for this simulation)
        # Set critical properties
        self.properties["cycleStage"] = 0     # The current stage of the dryer's cycle.  0 = not running, 1 = drying, 2 = finished
        self.properties["finishedCycle"] = False  # Set to True when the dryer has finished drying the clothes.  Reset when it's open.

    # Try to turn on the dryer.
    # Returns an observation string, and a success flag (boolean)
    def turnOn(self):
        # The dryer can't be turned on if it's opened
        if self.properties["isOpen"]:
            return ("The " + self.name + " is opened, so it can't be turned on.", False)

        # Otherwise, turn on the dishwasher
        return Device.turnOn(self)


    def tick(self):
        # If the dryer is opened, then it automatically turns off and resets
        if (self.properties["isOpen"] == True):
            self.properties["isOn"] = False
            self.properties["finishedCycle"] = False
            self.properties["cycleStage"] = 0

        # If the dryer is on, then dry the clothes
        if (self.properties["isOn"] == True):
            # Increment the cycle stage
            if (self.properties["cycleStage"] < 3):
                self.properties["cycleStage"] += 1

            # Check for stage 1
            if self.properties["cycleStage"] == 2:
                # Clothes become dry
                for obj in self.getAllContainedObjectsRecursive():
                    if (type(obj) == Clothes):
                        obj.properties['isWet'] = False

            # Check for stage 2
            elif self.properties["cycleStage"] == 3:
                # Set the dryer to finished
                self.properties["finishedCycle"] = True
                self.properties["cycleStage"] = 0
                # Turn off the dryer
                self.turnOff()

        else:
            # If the dryer is off, then don't dry the clothes
            pass

    def makeDescriptionStr(self, makeDetailed=False):
        outStr = f"a {self.name}"
        # Check if finished a cycle
        if self.properties["finishedCycle"]:
            outStr += " with a blinking green light"

        if self.properties["isOn"]:
            outStr += " that is currently on"
        else:
            # Check if open
            if self.properties["isOpen"]:
                outStr += " that is currently open"
                # Check if empty
                if len(self.contains) == 0:
                    outStr += " and empty"
                else:
                    if not makeDetailed:
                        outStr += " and contains one or more items."
                    else:
                        outStr += " and contains the following items: \n"
                        for obj in self.contains:
                            outStr += "\t" + obj.makeDescriptionStr() + "\n"
            else:
                outStr += " that is currently closed"

        return outStr


class Clothes(GameObject):
    # Constructor.
    # isClean is a boolean that indicates whether the dish is initialized as clean or dirty
    def __init__(self, name, isDirty=True, isWet=False):
        GameObject.__init__(self, name)
        # Set critical properties
        self.properties["isDirty"] = isDirty
        self.properties["isWet"] = isWet

    # Get a list of referents (i.e. names that this object can be called by)
    def getReferents(self):
        is_dirty = ""
        if self.properties["isDirty"]:
            is_dirty += "dirty "
        else:
            is_dirty += "clean "

        is_wet = ""
        if self.properties["isWet"]:
            is_wet += "wet "
        else:
            is_wet += "dry "

        # Allow reference by either the clothes name, or optionally saying its dirty/clean or wet/dry
        return [self.name, f"{is_dirty}{self.name}", f"{is_wet}{self.name}", f"{is_dirty}{is_wet}{self.name}"]

    def makeDescriptionStr(self, makeDetailed=False):
        is_dirty = ""
        if self.properties["isDirty"]:
            is_dirty += "dirty "
        else:
            is_dirty += "clean "

        is_wet = ""
        if self.properties["isWet"]:
            is_wet += "wet "
        else:
            is_wet += "dry "
        outStr = f"a {is_dirty}{is_wet}{self.name}"

        return outStr


# A bottle of dish soap
class DetergentBottle(Device):
    def __init__(self):
        Device.__init__(self, "bottle of detergent")

    # Try to use the device with a patient object (e.g. a light with a person, a fan with a person, etc.)
    # Returns an observation string, and a success flag (boolean)
    def useWithObject(self, patientObject):
        # If the patient object is a washing machine, then add detergent in it
        if type(patientObject)==WashingMachine:
            # Add a squirt of soap to the dishwasher
            patientObject.addObject(Detergent())
            return ("You add some detergent into the washing machine.", True)

        else:
            return ("You're not sure how to use the " + self.name + " with the " + patientObject.name + ".", False)

    def makeDescriptionStr(self, makeDetailed=False):
        return f"a {self.name}"

# Detergent
class Detergent(GameObject):
    def __init__(self):
        GameObject.__init__(self, "detergent")

# A basket used as an answer box
class Basket(Container):
    def __init__(self):
        GameObject.__init__(self, "basket")
        Container.__init__(self, "basket")
        self.properties["isMoveable"] = False # we don't want the basket to be moved
        self.properties["isOpenable"] = False # no need to open a basket

    def makeDescriptionStr(self, makeDetailed=False):
        return f"a {self.name}"

# The world is the root object of the game object tree.  In single room environments, it's where all the objects are located.
class World(Container):
    def __init__(self):
        Container.__init__(self, "room")

    def makeDescriptionStr(self, makeDetailed=False):
        outStr = "You find yourself in a room.  In the room, you see: \n"
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

        # Add a washing machine
        washing_machine = WashingMachine()
        world.addObject(washing_machine)

        # Add a dryer
        dryer = Dryer()
        world.addObject(dryer)

        # Add dish soap
        detergent_bottle = DetergentBottle()
        world.addObject(detergent_bottle)

        # Add some clothes names and shuffle them
        clothes_names = ["shirt", "coat", "jacket", "dress", "skirt", "vest", "sweater"]
        self.random.shuffle(clothes_names)

        # Add some random number of dirty clothes to the world (minimum 3, maximum 5)
        self.num_dirty_clothes = self.random.randint(3, 5)

        for i in range(self.num_dirty_clothes):
            # create a Clothes object
            clothes = Clothes(clothes_names[i])
            # Add the clothes to the environment
            world.addObject(clothes)

        # Also add a few clean dishes
        for i in range(self.num_dirty_clothes, len(clothes_names)):
            # create a Clothes object
            clothes = Clothes(clothes_names[i], isDirty=False)
            # Add the clothes to the environment
            world.addObject(clothes)

        # Add a basket as an answer box
        basket = Basket()
        world.addObject(basket)
        self.answer_box = basket

        # Return the world
        return world

    # Get the task description for this game
    def getTaskDescription(self):
        return "Your task is to wash the dirty clothes and dry them."

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

        # (0-arg) Wait. Do nothing, just wait 1 tick
        self.addAction("wait", ["wait"])

        # Actions with one object argument
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

    def actionTurnOn(self, obj):
        # Check if the object is a device
        if (obj.getProperty("isDevice") == True):
            # This is handled by the object itself
            obsStr, success = obj.turnOn()
            return obsStr
        else:
            return "You can't turn on that."

    def actionTurnOff(self, obj):
        # Check if the object is a device
        if (obj.getProperty("isDevice") == True):
            # This is handled by the object itself
            obsStr, success = obj.turnOff()
            return obsStr
        else:
            return "You can't turn off that."

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
        elif (actionVerb == "wait"):
            # wait one tick
            self.observationStr = "You wait."
        elif (actionVerb == "examine"):
            # Examine an object
            thingToExamine = action[1]
            self.observationStr = thingToExamine.makeDescriptionStr(makeDetailed = True)
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

        #Check if all clothes are clean and dry
        allObjects = self.rootObject.getAllContainedObjectsRecursive()
        all_complete = True
        for obj in allObjects:
            if (type(obj)==Clothes):
                if (obj.getProperty("isDirty") == True or obj.getProperty("isWet")==True or obj.parentContainer != self.answer_box):
                    all_complete = False
                    break

        # Check if the game is complete
        if all_complete:
            self.score = 1
            self.gameOver = True
            self.gameWon = True




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
    while not game.gameOver:

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

