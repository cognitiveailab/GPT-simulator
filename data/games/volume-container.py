# volume-container.py
# based on plant-tree.py
# ruoyao wang (mar 6/2023)

# Task Description: Your task is to simulate an experiment that measures the volume of a container by measuring the water it can hold.
# Environment: room
# Task-critical Objects: Water, Sink, WaterContainer, GraduatedCylinder
# High-level object classes: Container (Sink, WaterContainer), WaterContainer (GraduatedCylinder)
# Critical properties: volume (WaterContainer), containedLiquidVolume (GraduatedCylinder)
# Actions: look, inventory, take/put objects, pour liquid, answer
# Distractor Items: WaterContainer
# Distractor Actions: None
# High-level solution procedure: put target water container into the sink, turn on sink, pour water in the target water container to the graduated cylinder, read graduated cylinder, answer

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

        # Check to see if the object is liquid
        if obj.getProperty("isLiquid"):
            return (f"The {obj.name} is liquid and cannot be taken directly.",None, False)

        # If this object is a container, then check to see if it is open
        if not (self.getProperty("isOpen") == True):
            # If not, then it can't be removed from a container
            return ("The " + self.name + " is closed, so things can't be removed from it.", None, False)

        # Check to make sure that the object is contained in this container
        if obj not in self.contains:
            return ("The " + obj.name + " is not contained in the " + self.name + ".", None, False)

        # If this object is a container and it is open, then remove the object from the container
        obj.removeSelfFromContainer()
        return ("", obj, True)

    # Make a human-readable string that describes this object
    def makeDescriptionStr(self, makeDetailed=False):
        return "the " + self.name + "."

#
#   Specific Game Objects
#

# water
class Water(GameObject):
    def __init__(self, volume):
        GameObject.__init__(self, "water")
        # Set critical properties
        self.properties["isLiquid"] = True
        self.properties["volume"] = volume

    def getReferents(self):
        return [f"water in {self.parentContainer.name}"]

    def makeDescriptionStr(self, makeDetailed=False):
        return f"{self.name}"


# A sink
class Sink(Container):
    def __init__(self, isOn = False):
        GameObject.__init__(self, "sink")
        Container.__init__(self, "sink")

        self.properties["containerPrefix"] = "in"
        self.properties["isActivatable"] = True # a sink can be activated
        self.properties["isMoveable"] = False
        self.properties["isOn"] = isOn

    # On each step that the sink is on, add water to any object in the sink that doesn't have water on it
    def tick(self):
        # Get the objects contained in the sink
        containedObjects = self.getAllContainedObjectsRecursive()
        # Check if the sink is on
        if self.properties["isOn"]:
            # Check each container to make sure it contains water
            for obj in containedObjects:
                # Check if the object is a container
                if isinstance(obj, WaterContainer):
                    # Check if the container contains water
                    foundObject = None
                    for o in obj.contains:
                        if type(o) == Water:
                            foundObject = o
                            break
                    # If it doesn't contain any water, add some
                    if foundObject is None:
                        water = Water(obj.getProperty("volume"))
                        obj.addObject(water)
                    # If it contains water, add water to the container's max volume
                    else:
                        foundObject.properties["volume"] = obj.getProperty("volume")

    def makeDescriptionStr(self, makeDetailed=True):
        outStr = f"a {self.name}"

        # Check if on
        if self.properties["isOn"]:
            outStr += " that is currently on"
        else:
            outStr += " that is currently off"

        # Check if open
        if len(self.contains) == 0:
            outStr += " and that is empty"
        else:
            if not makeDetailed:
                outStr += " and that contains one or more items."
            else:
                outStr += " and that contains the following items: \n"
                for obj in self.contains:
                    outStr += "\t" + obj.makeDescriptionStr() + "\n"

        return outStr

    # Try to turn on the sink.
    # Returns an observation string, and a success flag (boolean)
    def turnOn(self):
        # If the sink isn't activatable, then return an error
        if (self.getProperty("isActivatable") == False):
            return ("It's not clear how the " + self.getReferents()[0] + " could be turned on.", False)

        # If the sink is already on, then return an error
        if self.properties["isOn"]:
            return ("The " + self.getReferents()[0] + " is already on.", False)
        else:
            self.properties["isOn"] = True
            return ("The " + self.getReferents()[0] + " is now turned on.", True)

    # Try to turn off the sink.
    # Returns an observation string, and a success flag (boolean)
    def turnOff(self):
        # If the sink isn't activatable, then return an error
        if (self.getProperty("isActivatable") == False):
            return ("It's not clear how the " + self.getReferents()[0] + " could be turned off.", False)

        # If the sink is already off, then return an error
        if not self.properties["isOn"]:
            return ("The " + self.getReferents()[0] + " is already off.", False)
        else:
            self.properties["isOn"] = False
            return ("The " + self.getReferents()[0] + " is now turned off.", True)



# Water Container
class WaterContainer(Container):
    def __init__(self, name, volume):
        GameObject.__init__(self, name)
        # Set critical properties
        self.properties["isWaterContainer"] = True
        self.properties["volume"] = volume

    def makeDescriptionStr(self, makeDetailed=False):
        outStr = f"a {self.name}"

        effectiveContents = []
        for obj in self.contains:
            effectiveContents.append(obj.makeDescriptionStr())

        if (len(effectiveContents) > 0):
            outStr += " containing "
            for i in range(len(effectiveContents)):
                if (i == len(effectiveContents) - 1) and (len(effectiveContents) > 1):
                    outStr += "and "
                outStr += effectiveContents[i] + ", "
            outStr = outStr[:-2]
        else:
            outStr += " that is empty"

        return outStr

# A Graduated Cylinder that can measure the volume of water
class GraduatedCylinder(WaterContainer):
    def __init__(self, volume):
        WaterContainer.__init__(self, "graduated cylinder", volume)

    def makeDescriptionStr(self, makeDetailed=False):
        outStr = f"a {self.name}"

        containedLiquidVolume = 0
        for obj in self.contains:
            containedLiquidVolume += obj.properties['volume']

        if containedLiquidVolume > 0:
            outStr += f" containing {containedLiquidVolume} mL {self.contains[0].name}"
        else:
            outStr += " that is empty"

        return outStr

# The world is the root object of the game object tree.  In single room environments, it's where all the objects are located.
class World(Container):
    def __init__(self):
        Container.__init__(self, "room")

    def makeDescriptionStr(self, makeDetailed=False):
        outStr = "You are in a room.  In the room, you see: \n"
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
        # Player answer volume
        self.answer_volume = None
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

        # Add the agent (the mother bird) into the world (nest)
        world.addObject(self.agent)

        # Add a sink
        sink = Sink()
        world.addObject(sink)

        # Add 2-5 water containers, one of them is the target
        possible_water_containers = ["cup", "glass", "mug", "bottle", "bowl"]
        self.random.shuffle(possible_water_containers)
        num_water_containers = self.random.randint(2,5)
        water_containers = possible_water_containers[:num_water_containers]
        # select volumes for the containers randomly from 50 mL to 200 mL
        water_containers_volume = self.random.choices(range(50, 200), k=num_water_containers)
        target_id = self.random.randint(0,num_water_containers-1)

        for i in range(num_water_containers):
            water_container = WaterContainer(water_containers[i], water_containers_volume[i])
            world.addObject(water_container)
            if i==target_id:
                self.target_water_container = water_containers[i]
                self.target_water_container_volume = water_containers_volume[i]

        # Add a 200 mL graduated cylinder
        graduated_cylinder = GraduatedCylinder(200)
        world.addObject(graduated_cylinder)

        # Return the world
        return world

    # Get the task description for this game
    def getTaskDescription(self):
        return f"Your task is to figure out the volume of the {self.target_water_container}."

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

        # (1-arg) Turn on/Turn off device
        for objReferent, objs in allObjects.items():
            for obj in objs:
                self.addAction("turn on " + objReferent, ["turn on", obj])
                self.addAction("turn off " + objReferent, ["turn off", obj])

        # (1-arg) Answer
        for i in range(50, 200):
            self.addAction(f"answer {i} mL", ["answer", i])

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

        # (2-arg) Pour
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

        # Putting solid objects into liquid containers is not allowed in this game
        if newContainer.getProperty("isWaterContainer"):
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

    # Pour water
    def actionPour(self, water, target):
        if type(water) != Water:
            return f"Cannot pour {water.name}."
        # if the target cannot hold water, remove the water
        elif not target.getProperty("isWaterContainer"):
            referent = water.getReferents()[0]
            water.removeSelfFromContainer()
            del water
            return f"{referent} is poured."
        else:
            # if current container is bigger than the target, the target is filled and there are some water left in the current container
            if water.getProperty("volume") > target.getProperty("volume"):
                water.properties["volume"] = water.getProperty("volume") - target.getProperty("volume")
                extra_water = Water(target.getProperty("volume"))
                target.addObject(extra_water)
            # otherwise, the target container will take all water
            else:
                water.removeSelfFromContainer()
                target.addObject(water)

            return f"You pour {water.getReferents()[0]} into {target.name}"

    def actionTurnOn(self, obj):
        # Check if the object is a device
        if (obj.getProperty("isActivatable") == True):
            # This is handled by the object itself
            obsStr, success = obj.turnOn()
            return obsStr
        else:
            return "You can't turn on that."

    def actionTurnOff(self, obj):
        # Check if the object is a device
        if (obj.getProperty("isActivatable") == True):
            # This is handled by the object itself
            obsStr, success = obj.turnOff()
            return obsStr
        else:
            return "You can't turn off that."

    # Answer
    def actionAnswer(self, volume):
        self.answer_volume = volume
        return f"You believe the volume of the {self.target_water_container} is {volume} mL."



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
        elif (actionVerb == "take"):
            # Take an object from a container
            thingToTake = action[1]
            self.observationStr = self.actionTake(thingToTake)
        elif (actionVerb == "turn on"):
            # turn on a sink
            thingToTurnOn = action[1]
            self.observationStr = self.actionTurnOn(thingToTurnOn)
        elif (actionVerb == "turn off"):
            # Turn off a sink
            thingToTurnOff = action[1]
            self.observationStr = self.actionTurnOff(thingToTurnOff)

        elif (actionVerb == "put"):
            # Put an object in a container
            thingToMove = action[1]
            newContainer = action[2]
            self.observationStr = self.actionPut(thingToMove, newContainer)
        elif (actionVerb == "pour"):
            # pour water
            water = action[1]
            target = action[2]
            self.observationStr = self.actionPour(water, target)
        elif (actionVerb == "answer"):
            # answer
            answer = action[1]
            self.observationStr = self.actionAnswer(answer)

        # Catch-all
        else:
            self.observationStr = "ERROR: Unknown action."


    def step_tick(self):
        # Do one tick of the environment
        tick_output_strs = self.doWorldTick()
        # if any tick output some information, add it to the output string
        if len(tick_output_strs) > 0:
            self.observationStr = '\n'.join([self.observationStr] + tick_output_strs)

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
        output_strs = []
        for obj in allObjects:
            tick_output_str = obj.tick()
            if tick_output_str is not None:
                output_strs.append(tick_output_str)
        return output_strs

    # Calculate the game score
    def calculateScore(self):
        # Baseline score
        self.score = 0

        if self.answer_volume is not None:
            if self.target_water_container_volume == self.answer_volume:
                self.score += 1
                self.gameOver = True
                self.gameWon = True
            else:
                self.score = 0
                self.gameOver = True
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

