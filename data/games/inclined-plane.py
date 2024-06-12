# inclined-plane.py
# based on boil-water.py
# ruoyao wang (apr 27/2023)

# Task: Create a micro-simulation that models how to compare the friction of two inclined planes by measuring the time a block sliding down the plane.
# Environment: workshop
# Task-critical Objects: InclinedPlane, Stopwatch
# High-level object classes: Container (InclinedPlane)
# Critical properties: acceleration (InclinedPlane), length (InclinedPlane), objects (InclinedPlane), isActivated (Stopwatch), tick (Stopwatch)
# Actions: look, inventory, examine, take/put objects, activate/deactivate/reset stopwatch, focus on object
# Distractor Items: None
# Distractor Actions: None
# High-level solution procedure: take stopwatch, take the block, put the block on the first inclined plane, activate stopwatch, wait till the block slides down to the bottom, deactivate stopwatch, examine stopwatch, reset stopwatch, take the block, put the block on the second inclined plane, activate the stopwatch, wait till the block slides to the bottom, deactivate stopwatch, examiine stopwatch, focus on the answer inclined plane


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

# A stove, which is a heating device.  It holds things on its surface.  When turned on, it progressively heats things up to some temperature.

# Inclined plane
class InclinedPlane(Container):
    def __init__(self, name, acceleration, length):
        GameObject.__init__(self, name)
        Container.__init__(self, name)
        self.properties["containerPrefix"] = "on"
        self.properties["isMoveable"] = False

        # Set critical properties
        self.properties["acceleration"] = acceleration # acceleration a block can have when putting on the inclined plane, reflects the angle of the inclined plane
        self.properties["length"] = length # the length of the surface of the inclined plane
        self.properties["objects"] = {} # record the number of ticks that the object is on the inclined plane

    def addObject(self, obj):
        self.properties["objects"][obj.name] = 0
        super().addObject(obj)

    def removeObject(self, obj):
        self.properties["objects"].pop(obj.name)
        super().removeObject(obj)

    def tick(self):
        for obj in self.contains:
            self.properties["objects"][obj.name] += 1

    def makeDescriptionStr(self, makeDetailed=False):
        if len(self.contains) == 0:
            return f"an {self.name}"
        else:
            outStr = f"an {self.name}, with:"
            obj_desc = []
            for obj_name in self.properties["objects"]:
                distance = 0.5 * self.properties["acceleration"] * self.properties["objects"][obj_name] ** 2
                if distance > self.properties["length"]:
                    rate = 1
                else:
                    rate = round(distance/self.properties["length"], 3)
                obj_desc.append(f"a {obj_name} approximately {rate*100}% down the plane")
            outStr += ','.join(obj_desc)
            return outStr

# stopwatch
class Stopwatch(GameObject):
    def __init__(self, name):
        GameObject.__init__(self, name)
        # Set critical properties
        self.properties["isActivated"] = False
        self.properties["tick"] = 0

    def tick(self):
        if self.properties["isActivated"]:
            self.properties["tick"] += 1

    def reset(self):
        self.properties["isActivated"] = False
        self.properties["tick"] = 0

    def makeDescriptionStr(self, makeDetailed=False):
        activated = "activated" if self.properties["isActivated"] else "deactivated"
        if makeDetailed:
            outStr = f"a {self.name}, which is {activated}. The time reads {self.properties['tick']} ticks."
        else:
            outStr = f"a {self.name}, which is {activated}"
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
        self.agent_answer = None
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

        # Add two inclined planes
        self.a1, self.a2 = self.random.sample([0.5,1,1.5,2], 2)

        inclined_plane_1 = InclinedPlane("inclined plane 1", self.a1, 100)
        inclined_plane_2 = InclinedPlane("inclined plane 2", self.a2, 100)
        world.addObject(inclined_plane_1)
        world.addObject(inclined_plane_2)

        if self.a1 < self.a2:
            self.answer = inclined_plane_1
        else:
            self.answer = inclined_plane_2

        # Add a block
        block = GameObject("block")
        world.addObject(block)

        # Add a stopwatch
        stopwatch = Stopwatch("stopwatch")
        world.addObject(stopwatch)

        # Return the world
        return world

    # Get the task description for this game
    def getTaskDescription(self):
        return "Here are two inclined planes with the same angle. Your task is figure out which of the two inclined planes has the most friction. Focus on the inclined plane with the most friction after your experiment."

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

        # (1-arg) Detailed look/examine
        for objReferent, objs in allObjects.items():
            for obj in objs:
                self.addAction("examine " + objReferent, ["examine", obj])

        # (1-arg) activate/deactivate/reset stopwatch
        for objReferent, objs in allObjects.items():
            for obj in objs:
                self.addAction("activate " + objReferent, ["activate", obj])
                self.addAction("deactivate " + objReferent, ["deactivate", obj])
                self.addAction("reset " + objReferent, ["reset", obj])

        # (1-arg) focus
        for objReferent, objs in allObjects.items():
            for obj in objs:
                self.addAction("focus on " + objReferent, ["focus", obj])

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

    # Activate a stopwatch
    def actionActivate(self, stopwatch):
        # type checking
        if type(stopwatch) != Stopwatch:
            return f"You can't activate the {stopwatch.name}."

        # check if the agent has the stopwatch
        if type(stopwatch.parentContainer) != Agent:
            return f"You should take the {stopwatch.name} first."

        if not stopwatch.properties["isActivated"]:
            stopwatch.properties["isActivated"] = True
            return f"You activate the {stopwatch.name}."
        else:
            return f"The {stopwatch.name} has already been activated."

    # Deactivate a stopwatch
    def actionDeactivate(self, stopwatch):
        # type checking
        if type(stopwatch) != Stopwatch:
            return f"You can't deactivate the {stopwatch.name}."

        # check if the agent has the stopwatch
        if type(stopwatch.parentContainer) != Agent:
            return f"You should take the {stopwatch.name} first."

        if stopwatch.properties["isActivated"]:
            stopwatch.properties["isActivated"] = False
            return f"You deactivate the {stopwatch.name}."
        else:
            return f"The {stopwatch.name} has already been deactivated."

    # reset a stopwatch
    def actionReset(self, stopwatch):
        # type checking
        if type(stopwatch) != Stopwatch:
            return f"You can't reset the {stopwatch.name}."

        # check if the agent has the stopwatch
        if type(stopwatch.parentContainer) != Agent:
            return f"You should take the {stopwatch.name} first."

        # reset
        stopwatch.reset()
        return f"You reset the {stopwatch.name}."

    # focus on one of the inclined planes
    def actionFocus(self, inclined_plane):
        # type checking
        if type(inclined_plane) != InclinedPlane:
            return f"You can't focus on the {inclined_plane.name}."

        self.agent_answer = inclined_plane
        return f"You focus on the {inclined_plane.name}."



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

        elif (actionVerb == "take"):
            # Take an object from a container
            thingToTake = action[1]
            self.observationStr = self.actionTake(thingToTake)

        elif (actionVerb == "put"):
            # Put an object in a container
            thingToMove = action[1]
            newContainer = action[2]
            self.observationStr = self.actionPut(thingToMove, newContainer)

        elif (actionVerb == "activate"):
            # activate a stopwatch
            stopwatch = action[1]
            self.observationStr = self.actionActivate(stopwatch)

        elif (actionVerb == "deactivate"):
            # deactivate a stopwatch
            stopwatch = action[1]
            self.observationStr = self.actionDeactivate(stopwatch)

        elif (actionVerb == "reset"):
            # reset a stopwatch
            stopwatch = action[1]
            self.observationStr = self.actionReset(stopwatch)

        elif (actionVerb == "focus"):
            inclined_plane = action[1]
            self.observationStr = self.actionFocus(inclined_plane)

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
        if self.agent_answer is not None:
            if self.answer == self.agent_answer:
                self.gameOver = True
                self.gameWon = True
                self.score = 1
            else:
                self.gameOver = True
                self.gameWon = False
                self.score = 1



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

