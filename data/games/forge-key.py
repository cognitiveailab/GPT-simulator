# forge-key.py
# based on boil-water.py
# ruoyao wang (apr 29/2023)

# Task: Create a micro-simulation that models how to use a mold to forge a key and open a door.
# Environment: workshop
# Task-critical Objects: HeatSource, Substance, Mold, Door
# High-level object classes: Container (HeatSource, Mold)
# Critical properties: maxTemperature (HeatSource), tempIncreasePerTick (HeatSource, Mold), temperature (Substance, Mold), stateOfMatter (Substance), solidName/liquidName/gasName (Substance), meltingPoint/boilingPoint (Substance), isLiquidContainer (HeatSource, Mold), mold_shape (mold), solidShapeName (Substance), is_locked (Door), is_open (Door)
# Actions: look, inventory, take/put objects, open/close containers/doors, turn on/off devices, pour liquid into container
# Distractor Items: HeatSource, Mold
# Distractor Actions: None
# High-level solution procedure: take copper ingot, put copper ingot in foundry, turn on foundry, wait till copper melts, pour copper into a key mold, wait till copper cools down, take the copper key, open the door with the copper key

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
        self.properties["temperature"] = 20.0 # Initialize everything to have a starting temperature of 20 degrees C

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

    # Make a human-readable string that describes this object
    def makeDescriptionStr(self, makeDetailed=False):
        return "the " + self.name + "."


#
#   Specific Game Objects
#

# A heat source, which is a heating device.  It holds things on its surface.  When turned on, it progressively heats things up to some temperature.
class HeatSource(Container):
    def __init__(self, name, maxTemperature, tempIncreasePerTick, containerPrefix, isLiquidContainer=False):
        GameObject.__init__(self, name)
        Container.__init__(self, name)

        self.properties["containerPrefix"] = containerPrefix

        # Set the properties of this object
        self.properties["isMoveable"] = False
        self.properties["isOn"] = False         # Is the device currently on or off?

        # Set critical properties
        self.properties["isLiquidContainer"] = isLiquidContainer
        self.properties["maxTemperature"] = maxTemperature # Maximum temperature of the heat source (in degrees Celsius)
        self.properties["tempIncreasePerTick"] = tempIncreasePerTick # How much the temperature increases per tick (in degrees Celsius)

    # If the heat source is on, increase the temperature of anything on the heat source, up to the maximum temperature.
    def tick(self):
        # If the heat source is on, then increase the temperature of anything on the heat source
        if (self.properties["isOn"] == True):
            # Get a list of all objects on the heat source
            containedObjects = self.getAllContainedObjectsRecursive()

            # Change the temperature of each object on/in the heatsource
            for obj in containedObjects:
                if obj.properties["temperature"] > self.properties["maxTemperature"]:
                    newTemperature = max(obj.properties["temperature"] - self.properties["tempIncreasePerTick"], self.properties["maxTemperature"])
                else:
                    newTemperature = min(obj.properties["temperature"] + self.properties["tempIncreasePerTick"], self.properties["maxTemperature"])
                # Set the object's new temperature
                obj.properties["temperature"] = newTemperature

    # Try to turn on the device.
    # Returns an observation string, and a success flag (boolean)
    def turnOn(self):
        # If the device is already on, then return an error
        if self.properties["isOn"]:
            return ("The " + self.getReferents()[0] + " is already on.", False)
        else:
            self.properties["isOn"] = True
            return ("The " + self.getReferents()[0] + " is now turned on.", True)

    # Try to turn off the device.
    # Returns an observation string, and a success flag (boolean)
    def turnOff(self):
        # If the device is already off, then return an error
        if not self.properties["isOn"]:
            return ("The " + self.getReferents()[0] + " is already off.", False)
        else:
            self.properties["isOn"] = False
            return ("The " + self.getReferents()[0] + " is now turned off.", True)

    def makeDescriptionStr(self, makeDetailed=False):
        outStr = f"a {self.name}"

        # Check if on/off
        if self.properties["isOn"]:
            outStr += " that is currently on"
        else:
            outStr += " that is currently off"

        # Check if empty
        if len(self.contains) == 0:
            outStr += " and has nothing " + self.properties["containerPrefix"] + " it."
        else:
            outStr += " and has the following items " + self.properties["containerPrefix"] + " it: "
            outStr += ', '.join([obj.makeDescriptionStr() for obj in self.contains])

        return outStr


# A mold of the key
class Mold(Container):
    # Constructor.
    def __init__(self, mold_shape, temperature=20, temperature_change_per_tick=200):
        GameObject.__init__(self, f"{mold_shape} mold")
        Container.__init__(self, f"{mold_shape} mold")

        self.properties["containerPrefix"] = "in"
        # Set critical properties
        self.properties["mold_shape"] = mold_shape
        self.properties["temperature"] = temperature
        self.properties["tempIncreasePerTick"] = temperature_change_per_tick
        self.properties["isLiquidContainer"] = True

    def addObject(self, obj):
        super().addObject(obj)
        if obj.getProperty("stateOfMatter") == "liquid":
            obj.properties["solidShapeName"] = self.properties["mold_shape"]

    # Everything in the mold will gradually cools down (heated up) to the room temperature
    def tick(self):
        # Get a list of all objects on the mold
        containedObjects = self.getAllContainedObjectsRecursive()

        # Change the temperature of each object in the mold
        for obj in containedObjects:
            if obj.properties["temperature"] > self.properties["temperature"]:
                newTemperature = max(obj.properties["temperature"] - self.properties["tempIncreasePerTick"], self.properties["temperature"])
            else:
                newTemperature = min(obj.properties["temperature"] + self.properties["tempIncreasePerTick"], self.properties["temperature"])
            # Set the object's new temperature
            obj.properties["temperature"] = newTemperature

    def makeDescriptionStr(self, makeDetailed=False):
        outStr = f"the {self.name}"

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

# A substance with specific physical properties
class Substance(GameObject):
    def __init__(self, solidName, liquidName, gasName, solid_shape_name, boilingPoint, meltingPoint, currentTemperatureCelsius):
        GameObject.__init__(self, "substance")
        # Set critical properties
        self.properties["solidName"] = solidName
        self.properties["liquidName"] = liquidName
        self.properties["gasName"] = gasName
        self.properties["solidShapeName"] = solid_shape_name
        self.properties["boilingPoint"] = boilingPoint
        self.properties["meltingPoint"] = meltingPoint
        self.properties["temperature"] = currentTemperatureCelsius

        self.tick()

    # Change the state of matter of the substance (and it's name) based on the current temperature
    def tick(self):
        # Check if the substance is a solid
        if self.properties["temperature"] <= self.properties["meltingPoint"]:
            self.properties["stateOfMatter"] = "solid"
            self.name = f'{self.properties["solidName"]} {self.properties["solidShapeName"]} (ID: {self.uuid})'
        # Check if the substance is a liquid
        elif self.properties["temperature"] <= self.properties["boilingPoint"]:
            self.properties["stateOfMatter"] = "liquid"
            self.name = f"{self.properties["liquidName"]} (ID: {self.uuid})"
        # Check if the substance is a gas
        else:
            self.properties["stateOfMatter"] = "gas"
            self.name = f"{self.properties["gasName"]} (ID: {self.uuid})"

    def makeDescriptionStr(self, makeDetailed=False):
        if self.properties["stateOfMatter"] == "solid":
            return f"a {self.name}"
        else:
            return f"some {self.name}"


# A door
class Door(GameObject):
    def __init__(self, name, is_locked=True, is_open=False):
        GameObject.__init__(self, name)
        # Set critical properties
        self.properties["is_locked"] = is_locked
        self.properties["is_open"] = is_open

    def open(self, key=None):
        # The door is already opened
        if self.properties["is_open"]:
            return f"The {self.name} is already opened."
        else:
            # The door is closed, but not locked
            if not self.properties["is_locked"]:
                self.properties["is_open"] = True
                return f"You open the {self.name}."
            else:
                # The door is locked but a key is not available
                if key is None:
                    return f"The {self.name} is locked."
                # Unlock the door and open it
                else:
                    self.properties["is_open"] = True
                    self.properties["is_locked"] = False
                    return f"You unlock the {self.name} and open it."

    def close(self):
        # The door is already closed
        if not self.properties["is_open"]:
            return f"The {self.name} is already closed."
        # close the door
        else:
            return f"You close the {self.name}."

    def makeDescriptionStr(self, makeDetailed=False):
        if self.properties["is_open"]:
            outStr = f"a {self.name} that is open"
        elif self.properties["is_locked"]:
            outStr = f"a locked {self.name}"
        else:
            outStr = f"a {self.name} that is closed"
        return outStr


# The world is the root object of the game object tree.  In single room environments, it's where all the objects are located.
class World(Container):
    def __init__(self):
        Container.__init__(self, "workshop")

    def makeDescriptionStr(self, makeDetailed=False):
        outStr = "You find yourself in a workshop.  In the workshop, you see: \n"
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

        # Add a stove as a distractor
        stove = HeatSource("stove", 500, 50, "on")
        world.addObject(stove)

        # Add a foundry
        foundry = HeatSource("foundry", 1500, 200, "in", isLiquidContainer=True)
        world.addObject(foundry)

        # Add a copper ingot
        copper = Substance("copper", "copper (liquid)", "copper (steam)", "ingot", 2562, 1085, 20)
        world.addObject(copper)

        # Add a door
        door = Door("door")
        world.addObject(door)

        # Add a mold
        mold_key = Mold("key")
        world.addObject(mold_key)

        # Add a distractor mold
        mold_ingot = Mold("ingot")
        world.addObject(mold_ingot)

        # Return the world
        return world

    # Get the task description for this game
    def getTaskDescription(self):
        return "Your task is to forge a key to open the door."

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

        # (2-arg) Open with key
        for objReferent1, objs1 in allObjects.items():
            for objReferent2, objs2 in allObjects.items():
                for obj1 in objs1:
                    for obj2 in objs2:
                        if (obj1 != obj2):
                            self.addAction("open " + objReferent1 + " with " + objReferent2, ["open", obj1, obj2])

        # (2-arg) pour
        for objReferent1, objs1 in allObjects.items():
            for objReferent2, objs2 in allObjects.items():
                for obj1 in objs1:
                    for obj2 in objs2:
                        if (obj1 != obj2):
                            self.addAction("pour " + objReferent1 + " into " + objReferent2, ["pour", obj1, obj2])


        return self.possibleActions

    #
    #   Interpret actions
    #

    # Describe the room that the agent is currently in
    def actionLook(self):
        return self.agent.parentContainer.makeDescriptionStr()

    # Open a container/door
    def actionOpen(self, obj):
        # Check if the object is a container
        if (obj.getProperty("isContainer") == True):
            # This is handled by the object itself
            obsStr, success = obj.openContainer()
            return obsStr
        # Check if the object is a door
        elif type(obj) == Door:
            return obj.open()
        else:
            return "You can't open that."

    # Open a door with a key
    def actionOpenWith(self, door, key):
        # Check the type of the door
        if type(door) != Door:
            return f"You can't open the {door.name} with the {key.name}."

        # Check the key
        if type(key) != Substance or key.getProperty("solidShapeName") != "key" or key.getProperty("stateOfMatter") != "solid":
            return f"The {key.name} is not a valid key."

        # open the door with the key
        return door.open(key)

    # Close a container
    def actionClose(self, obj):
        # Check if the object is a container
        if (obj.getProperty("isContainer") == True):
            # This is handled by the object itself
            obsStr, success = obj.closeContainer()
            return obsStr
        elif type(obj) == Door:
            return obj.close()
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
        
        # If the object is a Subtance, it can only be taken when in the solid state
        if type(obj) == Substance and obj.getProperty("stateOfMatter") != "solid":
            return f"You can't take the {obj.name}."

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
        if type(obj) == HeatSource:
            # This is handled by the object itself
            obsStr, success = obj.turnOn()
            return obsStr
        else:
            return "You can't turn on that."

    def actionTurnOff(self, obj):
        # Check if the object is a device
        if type(obj) == HeatSource:
            # This is handled by the object itself
            obsStr, success = obj.turnOff()
            return obsStr
        else:
            return "You can't turn off that."

    def actionPour(self, liquid, container):
        # Check the type and state of liquid
        if type(liquid) != Substance or liquid.getProperty("stateOfMatter") != "liquid":
            return f"You can't pour the {liquid.name}."

        # Check if the container can hold liquid
        if not container.getProperty("isLiquidContainer"):
            return f"You can't pour the {liquid.name} into the {container.name}."

        # move the liquid to the new container
        container.addObject(liquid)
        return f"You pour the {liquid.name} into the {container.name}."



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

        elif (actionVerb == "open"):
            # Open a container/door
            if len(action) == 2:
                thingToOpen = action[1]
                self.observationStr = self.actionOpen(thingToOpen)
            # open with a key
            else:
                thingToOpen = action[1]
                key = action[2]
                self.observationStr = self.actionOpenWith(thingToOpen, key)
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

        elif (actionVerb == "pour"):
            # pour liquid
            liquid = action[1]
            container = action[2]
            self.observationStr = self.actionPour(liquid, container)


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

        # If the door is open, then add a point.
        allObjects = self.rootObject.getAllContainedObjectsRecursive()
        for obj in allObjects:
            if type(obj) == Door and obj.getProperty("is_open"):
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

