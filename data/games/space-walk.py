# space-walk.py
# based on sunburn.py
# ruoyao wang (apr 29/2023)

# Task Description: Create a micro-simulation that models conducting a space walk.
# Environment: world
# Task-critical Objects: Room, Door, SpaceSuit
# High-level object classes: Container (Room)
# Critical properties: isOuterSpace (Room), is_open(Door), wearSpaceSuit (Agent), die (Agent)
# Actions: look, inventory, take/put objects, move to a room, put on object, open/close door
# Distractor Items: None
# Distractor Actions: None
# High-level solution procedure: put on space suit, open door to airlock, move to airlock, close door to spaceship, open door to outer space, move to outer space

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
        return f"a {self.name}"


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
        return "a " + self.name


# A room
class Room(Container):
    def __init__(self, name, isOuterSpace=False):
        GameObject.__init__(self, name)
        Container.__init__(self, name)
        self.properties["isMoveable"] = False
        self.connects = {} # other rooms that this room connects to, {room: door}
        # Set critical properties
        self.properties["isOuterSpace"] = isOuterSpace



    def makeDescriptionStr(self, makeDetailed=False):
        outStr = f"You find yourself in a {self.name}.  In the {self.name}, you see: \n"
        for obj in self.contains:
            outStr += "\t" + obj.makeDescriptionStr() + "\n"

        # describe room connection information
        outStr += "You also see:\n"
        for _, door in self.connects.items():
            outStr += f"\t {door.makeDescriptionStr()}\n"
        return outStr

    # connect to another room
    def connect(self, room):
        if room not in self.connects:
            self.connects[room] = None
            room.connects[self] = None

    # check if there exists a path that connects to another room without any closed door on the path
    def connectsToOuterSpace(self, visited):
        visited.append(self)
        if self.properties["isOuterSpace"]:
            return True
        connected = False
        for r in self.connects:
            if r in visited:
                continue
            elif self.connects[r] is not None and not self.connects[r].getProperty("is_open"):
                continue
            elif r.getProperty("isOuterSpace"):
                connected = True
                break
            else:
                connected = r.connectsToOuterSpace(visited)
                if connected:
                    break
        return connected


# A door
class Door(GameObject):
    def __init__(self, name, room1, room2, is_open=False):
        GameObject.__init__(self, name)
        # connects to the door to two rooms
        self.connects = {room1: room2, room2: room1} # rooms connected by the door
        room1.connects[room2] = self
        room2.connects[room1] = self
        self.properties["isMoveable"] = False

        # Set critical properties
        self.properties["connects"] = (room1.name, room2.name)
        self.properties["is_open"] = is_open

    def get_curr_room(self):
        curr_room = None
        for room in self.connects:
            if room.containsItemWithName("agent"):
                curr_room = room
                break
        return curr_room

    def open(self, curr_room):
        # check if the curr_room is connected by this door
        if curr_room not in self.connects:
            return f"You can't open a door that is not in the current room."
        # The door is already opened
        elif self.properties["is_open"]:
            return f"The {self.name} to the {self.connects[curr_room].name} is already open."
        else:
            # If the door is closed, open it
            self.properties["is_open"] = True
            return f"You open the {self.name} to the {self.connects[curr_room].name}."

    def close(self, curr_room):
        # check if the curr_room is connected by this door
        if curr_room not in self.connects:
            return f"You can't close a door that is not in the current room."
        # The door is already closed
        elif not self.properties["is_open"]:
            return f"The {self.name} to the {self.connects[curr_room].name} is already closed."
        else:
            # If the door is closed, open it
            self.properties["is_open"] = False
            return f"You close the {self.name} to the {self.connects[curr_room].name}."

    def getReferents(self):
        curr_room = self.get_curr_room()
        if curr_room is not None:
            return [f"{self.name} to {self.connects[curr_room].name}"]
        else:
            return [f"{self.name}"]

    def makeDescriptionStr(self, makeDetailed=False):
        curr_room = self.get_curr_room()
        if curr_room is not None:
            if self.properties["is_open"]:
                outStr = f"a {self.name} to the {self.connects[curr_room].name} that is open"
            else:
                outStr = f"a {self.name} to the {self.connects[curr_room].name} that is closed"
        else:
            if self.properties["is_open"]:
                outStr = f"a {self.name} that is open"
            else:
                outStr = f"a {self.name} that is closed"
        return outStr

# Space suit
class SpaceSuit(GameObject):
    def __init__(self, name):
        GameObject.__init__(self, name)

# The world is the root object of the game object tree.
class World(Container):
    def __init__(self):
        Container.__init__(self, "world")

    # Describe the a room
    def makeDescriptionStr(self, room, makeDetailed=False):
        outStr = f"You find yourself in a {room.name}.  In the {room.name}, you see: \n"
        for obj in room.contains:
            outStr += "\t" + obj.makeDescriptionStr() + "\n"
        # describe room connection information
        outStr += "You also see:\n"
        for _, door in room.connects.items():
            outStr += f"\t {door.makeDescriptionStr(room)}\n"

        return outStr

# The agent
class Agent(Container):
    def __init__(self):
        GameObject.__init__(self, "agent")
        Container.__init__(self, "agent")
        # Set critical properties
        self.properties["wearSpaceSuit"] = False
        self.properties["die"] = False

    def getReferents(self):
        return ["yourself"]

    def makeDescriptionStr(self, makeDetailed=False):
        return "yourself"

    def tick(self):
        if self.parentContainer.connectsToOuterSpace([]) and not self.getProperty("wearSpaceSuit"):
            self.properties["die"] = True


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
        self.observationStr = self.rootObject.makeDescriptionStr(self.current_room)
        # Do calculate initial scoring
        self.calculateScore()

    # Create/initialize the world/environment for this game
    def initializeWorld(self):
        world = World()

        # Add three "rooms": spaceship, airlock, outer space
        spaceship = Room("spaceship")
        airlock = Room("airlock")
        outer_space = Room("outer space", isOuterSpace=True)
        world.addObject(spaceship)
        world.addObject(airlock)
        world.addObject(outer_space)
        # Connects the rooms
        spaceship.connect(airlock)
        airlock.connect(outer_space)

        # Add doors
        inner_door = Door("inner door", spaceship, airlock)
        world.addObject(inner_door)
        outer_door = Door("outer door", airlock, outer_space)
        world.addObject(outer_door)

        # Add the agent
        spaceship.addObject(self.agent)
        self.current_room = spaceship

        # Add a space suit
        space_suit = SpaceSuit("space suit")
        spaceship.addObject(space_suit)

        # Return the world
        return world

    # Get the task description for this game
    def getTaskDescription(self):
        return "Your task is to conduct a space walk."

    # Make a dictionary whose keys are object names (strings), and whose values are lists of object references with those names.
    # This is useful for generating valid actions, and parsing user input.
    def makeNameToObjectDict(self):
        # Get a list of all game objects
        allObjects = self.current_room.getAllContainedObjectsRecursive()

        # Make a dictionary whose keys are object names (strings), and whose values are lists of object references with those names.
        nameToObjectDict = {}
        for obj in allObjects:
            for name in obj.getReferents():
                #print("Object referent: " + name)
                if name in nameToObjectDict:
                    nameToObjectDict[name].append(obj)
                else:
                    nameToObjectDict[name] = [obj]

        # add doors to other rooms
        for _, door in self.current_room.connects.items():
            for referent in door.getReferents():
                if referent in nameToObjectDict:
                    nameToObjectDict[referent].append(door)
                else:
                    nameToObjectDict[referent] = [door]

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

        # (1-arg) open/close
        for objReferent, objs in allObjects.items():
            for obj in objs:
                self.addAction("open " + objReferent, ["open", obj])
                self.addAction("close " + objReferent, ["close", obj])

        # (1-arg) Move
        for room in self.current_room.connects:
            for room_ref in room.getReferents():
                self.addAction("move to " + room_ref, ["move", room])

        # (1-arg) Put on
        for objReferent, objs in allObjects.items():
            for obj in objs:
                self.addAction("put on " + objReferent, ["wear", obj])

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
        if not newContainer.getProperty("isContainer"):
            obj_ref = newContainer.getReferents()[0]
            return "You can't put things in the " + obj_ref + "."

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

    # Open a door
    def actionOpen(self, obj):
        if type(obj) == Door:
            return obj.open(self.current_room)
        else:
            return "You can't open that."


    # Close a door
    def actionClose(self, obj):
        if type(obj) == Door:
            return obj.close(self.current_room)
        else:
            return "You can't close that."

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


    ## Put on the space suit
    def actionPutOn(self, obj):
        # Check if the object is a space suit
        if type(obj) != SpaceSuit:
            return f"You can't put on {obj.name}"

        # wear the space suit
        self.agent.properties["wearSpaceSuit"] = True
        obsStr, objRef, success = obj.parentContainer.takeObjectFromContainer(obj)
        if not success:
            return obsStr
        # Add the object to the inventory
        self.agent.addObject(obj)
        return obsStr + f" You put on the {obj.name}."

    def actionMove(self, room):
        # Check if the target is a room
        if type(room) != Room:
            return f"Cannot move to the {room.name}"
        # Check if two rooms are connected
        elif room not in self.agent.parentContainer.connects:
            return f"There is no way from {self.agent.parentContainer.name} to {room.name}."
        # Check if the door to the target room is open
        elif not self.agent.parentContainer.connects[room].getProperty("is_open"):
            return f"The door to the {room.name} is closed."
        else:
            current_location = self.agent.parentContainer.name
            self.agent.removeSelfFromContainer()
            room.addObject(self.agent)
            self.current_room = room
            return f"You move from {current_location} to {room.name}."



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
            self.observationStr = self.actionLook()
        elif (actionVerb == "inventory"):
            # Display the agent's inventory
            self.observationStr = self.actionInventory()
        elif (actionVerb == "take"):
            # Take an object from a container
            thingToTake = action[1]
            self.observationStr = self.actionTake(thingToTake)
        elif (actionVerb == "put"):
            # Put an object in a container
            thingToMove = action[1]
            newContainer = action[2]
            self.observationStr = self.actionPut(thingToMove, newContainer)
        elif (actionVerb == "open"):
            # Open a door
            door = action[1]
            self.observationStr = self.actionOpen(door)
        elif (actionVerb == "close"):
            # Close a door
            door = action[1]
            self.observationStr = self.actionClose(door)
        elif (actionVerb == "wear"):
            # Put on the space suit
            space_suit = action[1]
            self.observationStr = self.actionPutOn(space_suit)
        elif (actionVerb == "move"):
            # move to a new location
            target_location = action[1]
            self.observationStr = self.actionMove(target_location)
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
        # Lose if the agent dies
        if self.agent.properties["die"]:
            self.score = 0
            self.gameOver = True
            self.gameWon = False
            return
        # Lose if the spaceship directly connects to the outerspace
        else:
            allObjects = self.rootObject.getAllContainedObjectsRecursive()
            for obj in allObjects:
                if "spaceship" in obj.name:
                    if obj.connectsToOuterSpace([]):
                        self.score = 0
                        self.gameOver = True
                        self.gameWon = False
                        return

        # Win when the agent moves to the outer space
        if "outer space" in self.agent.parentContainer.name:
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

