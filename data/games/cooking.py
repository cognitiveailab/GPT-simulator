# cooking.py
# based on boil-water.py
# ruoyao wang (apr 26/2023)

# Task: Create a micro-simulation that models how to cook following instructions in a cooking book.
# Environment: kitchen
# Task-critical Objects: CookBook, Ingredient, Device, Knife
# High-level object classes: None
# Critical properties: cut (Ingredient, whether the ingredient is sliced, diced or chopped), cook (Ingredient, whether the ingredient is roasted or fried), cook_method (Device)
# Actions: look, inventory, take/put objects, slice/dice/chop ingredient with knife, cook ingredient with device, read cook book, prepare meal
# Distractor Items: Ingredient
# Distractor Actions: None
# High-level solution procedure: take cook book, read cook book, follow instructions in the cook book to prepare ingredients, take the action prepare meal to finish


import random

UUID = 0
randomSeed = 10
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
        return f"the {self.name}"


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

# A cook book
class CookBook(GameObject):
    def __init__(self, receipt):
        GameObject.__init__(self, "cook book")
        # Set critical properties
        # receipt = {ingredients:[(cut methods, cook methods)]}
        self.properties["receipt"] = {k.name: v for k, v in receipt.items()}

    def read(self):
        instruction = "Gather all following ingredients and follow the directions to prepare this tasty meal.\n\n"

        instruction += "Ingredients:\n"
        for ingredient in self.properties["receipt"]:
            instruction += f"\t{ingredient}\n"

        instruction += "\n"
        instruction += "Directions:\n"
        for ingredient in self.properties["receipt"]:
            for prepare_method in self.properties["receipt"][ingredient]:
                if prepare_method is not None:
                    instruction += f"\t{prepare_method} the {ingredient}\n"
        instruction += "\tprepare meal\n"

        return instruction

# Ingredient
class Ingredient(GameObject):
    def __init__(self, name):
        GameObject.__init__(self, name)
        # Set critical properties
        self.properties["cut"] = None # how the ingredient is cut
        self.properties["cook"] = None # how the ingredient is cooked

    def makeDescriptionStr(self, makeDetailed=False):
        cut = ''
        cook = ''
        if self.properties["cut"] is not None:
            cut = self.properties["cut"][1] + ' '
        if self.properties["cook"] is not None:
            cook = self.properties["cook"][1] + ' '

        return f"the {cut}{cook}{self.name}"

# A device to cook (stove/oven)
class Device(GameObject):
    def __init__(self, name, cook_method):
        GameObject.__init__(self, name)
        self.properties["isMoveable"] = False
        # Set critical properties
        self.properties["cook_method"] = cook_method # e.g. (roast, roasted)

    def cook(self, ingredient):
        if ingredient.properties["cook"] is not None:
            return f"The {ingredient.name} has already been cooked."
        else:
            ingredient.properties["cook"] = self.properties["cook_method"]
            return f"You {self.properties['cook_method'][0]} the {ingredient.name} in the {self.name}"

# A knife
class Knife(GameObject):
    def __init__(self, name):
        GameObject.__init__(self, name)

    def cut(self, ingredient, cut_method):
        if ingredient.properties["cut"] is not None:
            return f"The {ingredient.name} has already been {ingredient.properties['cut'][1]}."
        else:
            ingredient.properties["cut"] = cut_method
            return f"You {cut_method[0]} the {ingredient.name}."


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
        # Number of actions that can earn a reward
        self.full_mark = 0
        # Game Object Tree
        self.rootObject = self.initializeWorld()
        # Game score
        self.score = 0
        self.numSteps = 0
        self.prepare_meal = False

        # Game over flag
        self.gameOver = False
        self.gameWon = False
        # Last game observation
        self.observationStr = self.rootObject.makeDescriptionStr()
        # Do calculate initial scoring
        self.calculateScore()
        # Generate possible actions
        self.generatePossibleActions()

    # Create/initialize the world/environment for this game
    def initializeWorld(self):
        world = World()

        # Add the agent
        world.addObject(self.agent)

        # cutting and cooking methods
        possible_cutting = ["slice", "dice", "chop", None]
        possible_cooking = ["fry", "roast", None]

        # randomly add some ingredients
        possible_ingredients = ["green hot pepper", "onion", "patato", "cucumber", "carrot"]
        num_ingredients = self.random.randint(2, 4)
        self.random.shuffle(possible_ingredients)

        # random generate the receipt
        self.receipt = {}
        for i in range(len(possible_ingredients)):
            ingredient = Ingredient(possible_ingredients[i])
            world.addObject(ingredient)
            if i < num_ingredients:
                # earn a reward when an ingredient on the receipt is taken
                self.full_mark += 1
                cut = self.random.choice(possible_cutting)
                cook = self.random.choice(possible_cooking)
                # earn a reward each time an ingredient is correctly prepared
                if cut is not None:
                    self.full_mark += 1
                if cook is not None:
                    self.full_mark += 1
                self.receipt[ingredient] = (cut, cook)

        # Add a cook book
        cook_book = CookBook(self.receipt)
        world.addObject(cook_book)

        # Add a knife
        knife = Knife("knife")
        world.addObject(knife)

        # Add a stove
        stove = Device("stove", ("fry", "fried"))
        oven = Device("oven", ("roast", "roasted"))
        world.addObject(stove)
        world.addObject(oven)

        # Return the world
        return world

    # Get the task description for this game
    def getTaskDescription(self):
        return "Your task is to prepare a meal following the instructions of the cook book."

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

        # (0-arg) Prepare the meal
        self.addAction("prepare meal", ["prepare meal"])

        # Actions with one object argument

        # (1-arg) Take
        for objReferent, objs in allObjects.items():
            for obj in objs:
                self.addAction("take " + objReferent, ["take", obj])
                self.addAction("take " + objReferent + " from " + obj.parentContainer.getReferents()[0], ["take", obj])

        # (1-arg) read
        for objReferent, objs in allObjects.items():
            for obj in objs:
                self.addAction("read " + objReferent, ["read", obj])


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

        # (2-arg) slice/dice/chop/cook
        for objReferent1, objs1 in allObjects.items():
            for objReferent2, objs2 in allObjects.items():
                for obj1 in objs1:
                    for obj2 in objs2:
                        if (obj1 != obj2):
                            self.addAction("slice " + objReferent1 + " with " + objReferent2, ["slice", obj1, obj2])
                            self.addAction("dice " + objReferent1 + " with " + objReferent2, ["dice", obj1, obj2])
                            self.addAction("chop " + objReferent1 + " with " + objReferent2, ["chop", obj1, obj2])
                            self.addAction("cook " + objReferent1 + " in " + objReferent2, ["cook", obj1, obj2])


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

    # slice/dice/chop
    def actionCut(self, cut_method, ingredient, knife):
        # Check if the object is an ingredient
        if type(ingredient) != Ingredient:
            return f"You can't {cut_method} the {ingredient.name}."
        # Check if the tool is a knife
        if type(knife) != Knife:
            return f"You can't {cut_method} with {knife.name}."

        # The agent must have the ingredient in inventory
        if type(ingredient.parentContainer) != Agent:
            return f"You should take the {ingredient.name} first."

        # The agent must have the knife in inventory
        if type(knife.parentContainer) != Agent:
            return f"You should take the {knife.name} first."

        if cut_method == "slice":
            cut = ("slice", "sliced")
        elif cut_method == "dice":
            cut = ("dice", "diced")
        elif cut_method == "chop":
            cut = ("chop", "chopped")
        else:
            return f"I don't know how to {cut_method}."

        return knife.cut(ingredient, cut)

    # cook
    def actionCook(self, ingredient, device):
        # Check if the object is an ingredient
        if type(ingredient) != Ingredient:
            return f"You can't cook the {ingredient.name}."
        # Check if the tool is a knife
        if type(device) != Device:
            return f"You can't cook in {device.name}."

        # The agent must have the ingredient in inventory
        if type(ingredient.parentContainer) != Agent:
            return f"You should take the {ingredient.name} first."

        return device.cook(ingredient)

    # read the cook book
    def actionRead(self, cook_book):
        # Check the type of the cook book
        if type(cook_book) != CookBook:
            return f"You can't read the {cook_book.name}."

        # Check if the agent has the cook book
        if type(cook_book.parentContainer) != Agent:
            return f"You should take the {cook_book.name} first."

        return cook_book.read()

    # prepare meal
    def actionPrepareMeal(self):
        self.prepare_meal = True
        return "You prepare the meal."



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


        if actionVerb == "look around":
            # Look around the environment -- i.e. show the description of the world.
            self.observationStr = self.rootObject.makeDescriptionStr()
        elif actionVerb == "inventory":
            # Display the agent's inventory
            self.observationStr = self.actionInventory()

        elif actionVerb == "take":
            # Take an object from a container
            thingToTake = action[1]
            self.observationStr = self.actionTake(thingToTake)

        elif actionVerb == "put":
            # Put an object in a container
            thingToMove = action[1]
            newContainer = action[2]
            self.observationStr = self.actionPut(thingToMove, newContainer)

        elif actionVerb in ["slice", "dice", "chop"]:
            # cut an ingredient
            cut_method = action[0]
            ingredient = action[1]
            knife = action[2]
            self.observationStr = self.actionCut(cut_method, ingredient, knife)

        elif actionVerb == "cook":
            # cook
            ingredient = action[1]
            device = action[2]
            self.observationStr = self.actionCook(ingredient, device)

        elif actionVerb == "read":
            # read
            cook_book = action[1]
            self.observationStr = self.actionRead(cook_book)

        elif actionVerb == "prepare meal":
            self.observationStr = self.actionPrepareMeal()


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

        for ingredient in self.receipt:
            # check if the agent has all ingredients in inventory
            if type(ingredient.parentContainer) == Agent:
                self.score += 1

            # check if all ingredients are prepared properly
            # The player loses the game if they wrongly prepare any ingredients
            if ingredient.properties['cut'] is not None:
                if ingredient.properties['cut'][0] == self.receipt[ingredient][0]:
                    self.score += 1
                else:
                    self.gameOver = True
                    self.gameWon = False
            if ingredient.properties['cook'] is not None:
                if ingredient.properties['cook'][0] == self.receipt[ingredient][1]:
                    self.score += 1
                else:
                    self.gameOver = True
                    self.gameWon = False


        if self.prepare_meal and self.score == self.full_mark:
            self.gameOver = True
            self.gameWon = True
            self.score += 1

        self.score /= self.full_mark + 1
        self.score = round(self.score, 2)





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

