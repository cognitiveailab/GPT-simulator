# take-photo.py
# based on dishwasher.py
# eric yuan (apr 26/2023)

# Task: take a photo of an object, using specified shutter speed, aperture, and iso.
# Environment: kitchen
# Task-critical Objects: Camera, Food
# High-level object classes: Device (Camera)
# Critical properties: shutter speed, aperture, iso
# Actions: look, inventory, examine, take/put objects, open/close containers, turn on/off devices, focus, rotate dials, press shutter
# Distractor Items: None
# Distractor Actions: None
# High-level solution procedure: take camera, focus on required object (food), rotate dials to adjust shutter speed/iso/aperture, press shutter.

import copy
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
        self.properties["isContainer"] = False # By default, objects are not containers
        self.properties["isMoveable"] = True   # By default, objects are moveable
        self.properties["temperature"] = 20.0  # Initialize everything to have a starting temperature of 20 degrees C

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
        # Can the container be opened (e.g. a drawer, a door, a box, etc.), or is it always 'open' (e.g. a table, a shelf, etc.)
        self.properties["isOpenable"] = False
        # Is the container open or closed (if it is openable)
        self.properties["isOpen"] = True
        # The prefix to use when referring to the container (e.g. "in the drawer", "on the table", etc.)
        self.properties["containerPrefix"] = "in"

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
        # Can this device be turned on or off?
        self.properties["isActivatable"] = True
        # Is the device currently on or off?
        self.properties["isOn"] = False

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

# A manual camera, which is a device for taking photos. To make the photo more appealing, one needs to set the appropriate aperture-iso-shutter speed combination.
class Camera(Device):
    def __init__(self, random_seed):
        GameObject.__init__(self, "camera")
        Device.__init__(self, "camera")
        self.random = random.Random(random_seed)

        # Set the properties of this object
        self.properties["isOn"] = True  # always on
        # Sure, it's manual, but not that old.
        self.properties["isMoveable"] = True
        self.current_focus = None
        # Set critical properties
        self.properties["shutter_speed_dial"] = ["1/4000", "1/2000", "1/1000", "1/500", "1/250",
                                   "1/125", "1/60", "1/30", "1/15", "1/8", "1/4", "1/2", "1", "2", "4", "8"]
        self.properties["iso_dial"] = ["64", "200", "400", "800", "1600", "3200", "6400"]
        self.properties["aperture_dial"] = ["1.4", "2", "2.8", "4", "5.6", "8", "11", "16"]
        self.properties["current_shutter_speed"] = self.random.randint(0, len(self.properties["shutter_speed_dial"]) - 1)
        self.properties["current_iso"] = self.random.randint(0, len(self.properties["iso_dial"]) - 1)
        self.properties["current_aperture"] = self.random.randint(0, len(self.properties["aperture_dial"]) - 1)
        self.properties["current_focus"] = None
        self.properties["photo"] = None

    def rotate_dial(self, which_dial="aperture", clockwise=True):
        diff = 1 if clockwise else -1
        if which_dial == "aperture":
            self.properties["current_aperture"] = (
                self.properties["current_aperture"] + len(self.properties["aperture_dial"]) + diff) % len(self.properties["aperture_dial"])
            outStr = "You rotated the aperture dial to %s" % (
                self.properties["aperture_dial"][self.properties["current_aperture"]])
        elif which_dial == "iso":
            self.properties["current_iso"] = (self.properties["current_iso"] +
                                len(self.properties["iso_dial"]) + diff) % len(self.properties["iso_dial"])
            outStr = "You rotated the iso dial to %s" % (
                self.properties["iso_dial"][self.properties["current_iso"]])
        elif which_dial == "shutter speed":
            self.properties["current_shutter_speed"] = (self.properties["current_shutter_speed"] + len(
                self.properties["shutter_speed_dial"]) + diff) % len(self.properties["shutter_speed_dial"])
            outStr = "You rotated the shutter speed dial to %s" % (
                self.properties["shutter_speed_dial"][self.properties["current_shutter_speed"]])
        return outStr

    def shutter(self):
        current_focus_ = "nothing" if self.current_focus is None else self.current_focus.name
        self.properties["photo"] = [current_focus_, copy.copy(
            self.properties["current_shutter_speed"]), copy.copy(self.properties["current_aperture"]), copy.copy(self.properties["current_iso"])]
        outStr = "You took a photo of %s, with shutter speed of %s, aperture of %s, and iso of %s." % (
            self.properties["photo"][0], self.properties["shutter_speed_dial"][self.properties["photo"][1]], self.properties["aperture_dial"][self.properties["photo"][2]], self.properties["iso_dial"][self.properties["photo"][3]])
        return outStr

    def focus(self, something):
        if something == self:
            return "You cannot focus on the camera itself."
        else:
            self.current_focus = something
            self.properties["current_focus"] = something.name
            return f"The camera is now focusing on {something.name}."

    def makeDescriptionStr(self, makeDetailed=False):
        current_focus_ = "nothing" if self.current_focus is None else self.current_focus.name
        outStr = []
        outStr.append("A loaded %s, the current shutter speed, aperture, and iso are %s, %s, and %s, it is currently focusing on %s." % (   self.name,
            self.properties["shutter_speed_dial"][self.properties["current_shutter_speed"]],
            self.properties["aperture_dial"][self.properties["current_aperture"]],
            self.properties["iso_dial"][self.properties["current_iso"]],
            current_focus_))

        outStr.append(
            "To change the shutter speed, aperture, or iso settings, one can rotate the corresponding dials either clockwise or the opposite direction.")
        outStr.append("The min/max available shutter speed is %s and %s." %
                      (self.properties["shutter_speed_dial"][0], self.properties["shutter_speed_dial"][-1]))
        outStr.append("The min/max available aperture is %s and %s." %
                      (self.properties["aperture_dial"][0], self.properties["aperture_dial"][-1]))
        outStr.append("The min/max available iso is %s and %s." %
                      (self.properties["iso_dial"][0], self.properties["iso_dial"][-1]))

        return "\n".join(outStr)


# (Distractor item) a food item
class Food(GameObject):
    def __init__(self, foodName):
        GameObject.__init__(self, foodName)
        self.foodName = foodName
        # Set critical properties
        self.properties["isFood"] = True

    def makeDescriptionStr(self, makeDetailed=False):
        return "a " + self.name


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
        self.randomSeed = randomSeed
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

        # Add a camera
        self.camera = Camera(self.randomSeed)
        world.addObject(self.camera)

        # Distractor items
        # Food names
        foodNames = ["apple", "orange", "banana", "pizza",
                     "peanut butter", "sandwhich", "pasta", "bell pepper"]
        # Shuffle the food names
        self.random.shuffle(foodNames)
        # Add a few random foods
        exist_foods = []
        numFoods = self.random.randint(1, 3)
        for i in range(numFoods):
            # Choose the next food name
            foodName = foodNames[i % len(foodNames)]
            # Create a new food item
            food = Food(foodName=foodName)
            exist_foods.append(food)
            # Add the food to the environment
            world.addObject(food)

        self.sample_task(exist_foods)

        # Return the world
        return world

    def sample_task(self, exist_foods):
        assert len(exist_foods) > 0
        self.target_food = self.random.choice(exist_foods)
        self.target_aperture = self.random.choice(self.camera.properties["aperture_dial"])
        self.target_shutter_speed = self.random.choice(
            self.camera.properties["shutter_speed_dial"])
        self.target_iso = self.random.choice(self.camera.properties["iso_dial"])

    # Get the task description for this game
    def getTaskDescription(self):
        return "Your task is to take a nice picture of %s, using a camera with shutter speed of %s, aperture of %s, and iso of %s." % (self.target_food.name, self.target_shutter_speed, self.target_aperture, self.target_iso)

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
        self.addAction("press shutter", ["press shutter"])
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
                self.addAction("take " + objReferent + " from " +
                               obj.parentContainer.getReferents()[0], ["take", obj])

        # (1-arg) Open/Close
        for objReferent, objs in allObjects.items():
            for obj in objs:
                self.addAction("open " + objReferent, ["open", obj])
                self.addAction("close " + objReferent, ["close", obj])

        # (1-arg) Detailed look/examine
        for objReferent, objs in allObjects.items():
            for obj in objs:
                self.addAction("examine " + objReferent, ["examine", obj])

        # (1-arg) Detailed focus
        for objReferent, objs in allObjects.items():
            for obj in objs:
                self.addAction("focus " + objReferent, ["focus", obj])

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
                            self.addAction(
                                "put " + objReferent1 + " " + containerPrefix + " " + objReferent2, ["put", obj1, obj2])

        # (2-arg) Use
        # OMIT, UNUSED (boiling water)
        for objReferent1, objs1 in allObjects.items():
            for objReferent2, objs2 in allObjects.items():
                for obj1 in objs1:
                    for obj2 in objs2:
                        if (obj1 != obj2):
                            self.addAction(
                                "use " + objReferent1 + " on " + objReferent2, ["use", obj1, obj2])

        # (2-arg) rotate
        for dial in ["aperture", "iso", "shutter speed"]:
            for direction in ["clockwise", "anticlockwise"]:
                self.addAction(
                    "rotate " + dial + " " + direction, ["rotate", dial, direction])

        return self.possibleActions

    #
    #   Interpret actions
    #

    # Describe the room that the agent is currently in
    def actionLook(self):
        return self.agent.parentContainer.makeDescriptionStr()

    # Perform the "press shutter" action.
    def actionPressShutter(self):
        # Enforce that the object must be in the inventory to do anything with it
        if (self.camera.parentContainer != self.agent):
            return "You don't currently have the camera in your inventory."
        else:
            outStr = self.camera.shutter()
            return outStr

    # Perform the "focus" action.  Returns an observation string.
    def actionFocus(self, obj):
        # Enforce that the object must be in the inventory to do anything with it
        if (self.camera.parentContainer != self.agent):
            return "You don't currently have the camera in your inventory."
        else:
            return self.camera.focus(obj)

    # Perform the "eat" action.  Returns an observation string.
    def actionEat(self, obj):
        # Enforce that the object must be in the inventory to do anything with it
        if (obj.parentContainer != self.agent):
            return "You don't currently have the " + obj.getReferents()[0] + " in your inventory."

        # Check if the object is food
        if (obj.getProperty("isFood") == True):
            # Try to pick up/take the food
            obsStr, objRef, success = obj.parentContainer.takeObjectFromContainer(
                obj)
            if (success == False):
                # If it failed, we were unable to take the food (e.g. it was in a closed container)
                return "You can't see that."

            # Update the game observation
            return "You eat the " + obj.foodName + "."
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
        obsStr, objRef, success = obj.parentContainer.takeObjectFromContainer(
            obj)
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
        obsStr1, objRef, success = objToMove.parentContainer.takeObjectFromContainer(
            objToMove)
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

    # rotate a dial
    def actionRotate(self, which_dial, direction):
        # Enforce that the camera must be in the inventory to do anything with it
        if (self.camera.parentContainer != self.agent):
            return "You don't currently have the camera in your inventory."

        obsStr = self.camera.rotate_dial(
            which_dial=which_dial, clockwise=(direction == "clockwise"))

        # Success observations
        return obsStr

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

    # OMIT, UNUSED (boiling water)
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
        elif (actionVerb == "press shutter"):
            # take a picture
            self.observationStr = self.actionPressShutter()

        elif (actionVerb == "examine"):
            # Examine an object
            thingToExamine = action[1]
            self.observationStr = thingToExamine.makeDescriptionStr(
                makeDetailed=True)
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

        # OMIT, UNUSED (boiling water)
        elif (actionVerb == "use"):
            # Use a device on an object
            deviceObj = action[1]
            patientObj = action[2]
            self.observationStr = self.actionUse(deviceObj, patientObj)
        elif (actionVerb == "focus"):
            # focus the camera on an object
            focusObj = action[1]
            self.observationStr = self.actionFocus(focusObj)
        elif (actionVerb == "rotate"):
            # rotate a dial on the camera
            which_dial = action[1]
            direction = action[2]
            self.observationStr = self.actionRotate(which_dial, direction)

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
        if self.camera.properties["photo"] is not None and \
                self.camera.properties["photo"][0] == self.target_food.name and \
                self.camera.properties["shutter_speed_dial"][self.camera.properties["photo"][1]] == self.target_shutter_speed and \
                self.camera.properties["aperture_dial"][self.camera.properties["photo"][2]] == self.target_aperture and \
                self.camera.properties["iso_dial"][self.camera.properties["photo"][3]] == self.target_iso:
            self.score = 1
            self.gameOver = True
            self.gameWon = True
        else:
            allObjects = self.makeNameToObjectDict()
            if self.target_food.name not in allObjects:
                # consumed
                self.score = 0
                self.gameOver = True
                self.gameWon = False

# Main Program
def main():

    # Create a new game
    game = TextGame(randomSeed=randomSeed)

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
    # while not game.gameOver:
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
