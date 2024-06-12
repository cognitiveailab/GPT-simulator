# bird-life-cycle.py
# based on make-ice-cubes.py
# ruoyao wang (feb 7/2023)

# Task: Create a micro-simulation that models a bird hatching its egg.
# Environment: nest
# Task-critical Objects: Bird
# High-level object classes: Container (Bird)
# Critical properties: stage (Bird, current life stage of the bird), warm (Bird, warmth that an egg gets), food (Bird, food that a young bird gets), hatch (Bird, number of ticks that the egg survives), grow (Bird, number of ticks that the young bird survives)
# Actions: look, inventory, sing, fly around, sit on object, feed object
# Distractor Items: None
# Distractor Actions: sing, fly around
# High-level solution procedure: sit on the egg till it is hatched, feed the young bird till it grows up

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


# A bird with three life stages: egg, young bird, adult bird
class Bird(Container):
    def __init__(self, name, stage, warm=3, food=3, hatch=0, grow=0):
        GameObject.__init__(self, name)
        Container.__init__(self, name)
        assert stage in ["egg", "young bird", "adult bird"]
        # Set critical properties
        self.properties["stage"] = stage # the life stage of a bird
        self.properties["warm"] = warm # the level of warm of the egg
        self.properties["food"] = food # the level of food of a young bird
        self.properties["hatch"] = hatch # the hatch stages
        self.properties["grow"] = grow # the grow stages


    def makeDescriptionStr(self, makeDetailed=False):
        if self.properties["stage"] == "egg":
            if self.properties["warm"] == 0:
                return "an egg (dead)"
            else:
                return "an egg"
        else:
            if self.properties["food"] <= 1:
                if self.properties["food"] == 1:
                    return f"a hungury {self.properties['stage']}"
                else:
                    return f"a {self.properties['stage']} (dead)"
            else:
                if self.properties["stage"] == "young bird":
                    return "a young bird"
                else:
                    return "an adult bird"

    def getReferents(self):
        return [self.getProperty("stage")]

    def tick(self):
        output_str = None
        # lose 1 point of warm for the egg at each step
        if self.properties["stage"] == "egg":
            self.properties["warm"] -= 1
        # lose 1 point of food for the young bird at each step
        if self.properties["stage"] == "young bird":
            self.properties["food"] -= 1
        # an egg gain 1 point of hatch at each step, and becomes a young bird when hatch reaches 5
        if self.properties["stage"] == "egg":
            self.properties["hatch"] += 1
            if self.properties["hatch"] == 5 and self.properties["warm"] > 0:
                self.properties["stage"] = "young bird"
                self.properties["food"] = 3
                output_str = "The egg is hatched!"
        # a young bird gain 1 point of grow at each step, and becomes an adult when grow reaches 5
        elif self.properties["stage"] == "young bird":
            self.properties["grow"] += 1
            if self.properties["grow"] == 5 and self.properties["food"] > 0:
                self.properties["stage"] = "adult bird"
                output_str = "The young bird grows up."
        return output_str

# The world is the root object of the game object tree.  In single room environments, it's where all the objects are located.
class World(Container):
    def __init__(self):
        Container.__init__(self, "nest")

    def makeDescriptionStr(self, makeDetailed=False):
        outStr = "You are a mother bird in your nest.  In the nest, you see: \n"
        for obj in self.contains:
            outStr += "\t" + obj.makeDescriptionStr() + "\n"

        return outStr


# The agent (just a placeholder for a container for the inventory)
class Agent(Bird):
    def __init__(self):
        GameObject.__init__(self, "agent")
        Bird.__init__(self, "agent", "adult bird")

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

        # Add the agent (the mother bird) into the world (nest)
        world.addObject(self.agent)
        # Add an egg into the nest
        egg = Bird("baby", "egg")
        world.addObject(egg)

        # Return the world
        return world

    # Get the task description for this game
    def getTaskDescription(self):
        return "Your task is to hatch the egg and raise the baby bird."

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

        # (0-arg) Sing. A distractor action, nothing happens
        self.addAction("sing", ["sing"])

        # (0-arg) Fly around. A distractor action, nothing happens
        self.addAction("fly around", ["fly around"])

        # Actions with one object argument
        # (1-arg) Eat
        # for objReferent, objs in allObjects.items():
        #     for obj in objs:
        #         self.addAction("eat " + objReferent, ["eat", obj])


        # (1-arg) Hatch an egg
        for objReferent, objs in allObjects.items():
            for obj in objs:
                self.addAction("sit on " + objReferent, ["sit", obj])

        # (1-arg) Feed a young bird
        for objReferent, objs in allObjects.items():
            for obj in objs:
                self.addAction("feed " + objReferent, ["feed", obj])


        return self.possibleActions

    #
    #   Interpret actions
    #

    # Describe the room that the agent is currently in
    def actionLook(self):
        return self.agent.parentContainer.makeDescriptionStr()


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

    # Sit on an egg
    def actionSit(self, obj):
        # if the target is not an egg
        if obj.getProperty("stage") != "egg":
            return f"You can't sit on that."
        else:
            # sit on the egg will keep the egg warm
            obj.properties["warm"] = 3
            return "You sit on the egg and keep it warm."

    # Feed a young bird
    def actionFeed(self, obj):
        # if the target is not a young bird
        if obj.getProperty("stage") != 'young bird':
            return "You can't feed that."
        else:
            # reset the food the maximum. At young bird stage it's 3
            obj.properties["food"] = 3
            return "You feed the young bird."


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
        # elif (actionVerb == "eat"):
        #     # Eat a food
        #     thingToEat = action[1]
        #     self.observationStr = self.actionEat(thingToEat)
        elif (actionVerb == "fly around"):
            self.observationStr = "You fly around."
        elif (actionVerb == "sing"):
            self.observationStr = "You sing."
        elif (actionVerb == "sit"):
            eggToHatch = action[1]
            self.observationStr = self.actionSit(eggToHatch)
        elif (actionVerb == "feed"):
            babyToFeed = action[1]
            self.observationStr = self.actionFeed(babyToFeed)


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

        allObjects = self.rootObject.getAllContainedObjectsRecursive()
        for obj in allObjects:
            # If there is an adult bird other than the agent, the player wins.
            if (type(obj) != Agent and obj.getProperty("stage") == "adult bird"):
                self.score += 1
                self.gameOver = True
                self.gameWon = True
            # The player loses the game if the egg is not hatched in time or the young bird is too hungry.
            if (obj.getProperty("food")==0):
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

