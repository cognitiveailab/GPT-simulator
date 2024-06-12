import argparse
import os
import json
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from experiments.quest_gpt import getTokenLength
from bytes32.utils import stream_llm_gpt

# arg parser
def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--game_code_folder", type=str, default="data/games")
    parser.add_argument("--output_folder", type=str, default="rules/llm_generated_rules")
    parser.add_argument("--model", type=str, default="gpt-4-0125-preview")

    args = parser.parse_args()
    return args

def get_classes(filename):
    # find the code of each class from the given Python code file
    # This function does not consider nested classes
    with open(filename) as f:
        lines = f.readlines()

    out = []

    class_indent = 0
    find_class = False
    class_code = ''
    for i, line in enumerate(lines):
        # remove all empty lines
        if len(line.strip()) == 0:
            continue
        if line.lstrip().startswith("class"):
            if find_class:
                out.append(class_code)
                class_code = ''
            find_class = True
            class_indent = len(line) - len(line.lstrip())
            class_code += line
        elif find_class:
            curr_indent = len(line) - len(line.lstrip())
            if curr_indent <= class_indent:
                out.append(class_code)
                find_class = False
                class_indent = 0
                class_code = ''
            else:
                class_code += line
    return out[:-1] # The last class of all games is the TextGame class

def main():
    args = parse_args()
    # for test
    sorted_file_names = [filename for filename in sorted(os.listdir(args.game_code_folder)) if filename.endswith('.py')]

    out_rules = {}
    for filename in sorted_file_names:
        if not filename.endswith('.py'):
            continue
        classes = get_classes(os.path.join(args.game_code_folder, filename))
        out = ""
        for i, cls in enumerate(classes):

            prompt = "You will be given a Python class which defines an object in a text game. List the classes inherited by this class and explain the properties of the object based on your understanding of the code. The properties you need to explain are commented as critical properties in the init function. If the class contains a tick method function, you should also decribe how the object properties will be changed at each game tick. Otherwise, do not explain any property. Your response should follow the format of the example below:\n"
            prompt += "Here is the code for the example:\n"
            prompt += '''class Stove(Container, Device):
        def __init__(self):
            GameObject.__init__(self, "stove")
            Container.__init__(self, "stove")
            Device.__init__(self, "stove")

            self.properties["containerPrefix"] = "on"
            self.properties["isOpenable"] = False # A stove is not openable
            self.properties["isMoveable"] = False # A stove is too heavy to move (and doesn't really need to be moved for this simulation)

            # Set critical properties
            self.properties["maxTemperature"] = 500.0 # Maximum temperature of the stove (in degrees Celsius)
            self.properties["tempIncreasePerTick"] = 25.0 # How much the temperature increases per tick (in degrees Celsius)

        # If the stove is on, increase the temperature of anything on the stove, up to the maximum temperature.
        def tick(self):
            # If the stove is on, then increase the temperature of anything on the stove
            if (self.properties["isOn"] == True):
                # Get a list of all objects on the stove
                objectsOnStove = self.getAllContainedObjectsRecursive()

                # Increase the temperature of each object on the stove
                for obj in objectsOnStove:
                    # Increase the object's temperature, up to the maximum temperature
                    newTemperature = obj.properties["temperature"] + self.properties["tempIncreasePerTick"]
                    if (newTemperature > self.properties["maxTemperature"]):
                        newTemperature = self.properties["maxTemperature"]
                    # Set the object's new temperature
                    obj.properties["temperature"] = newTemperature

        def makeDescriptionStr(self, makeDetailed=False):
            outStr = "a stove"

            # Check if on/off
            if self.properties["isOn"]:
                outStr += " that is currently on"
            else:
                outStr += " that is currently off"

            # Check if empty
            if len(self.contains) == 0:
                outStr += " and has nothing " + self.properties["containerPrefix"] + " it."
            else:
                if not makeDetailed:
                    outStr += " and has one or more items " + self.properties["containerPrefix"] + " it."
                else:
                    outStr += " and has the following items " + self.properties["containerPrefix"] + " it:\\n"
                    for obj in self.contains:
                        outStr += "\\t" + obj.makeDescriptionStr() + "\\n"

            return outStr'''
            prompt += "The expected output is:\n"
            prompt += "Object: Stove\n"
            prompt += "Inherits: Container, Device\n"
            prompt += "Properties:\n"
            prompt += "maxTemperature: the maximum temperature of the stove in degrees Celsius\n"
            prompt += "tempIncreasePerTick: the temperature increases per tick for objects on the stove if the stove is on.\n"
            prompt += "\n"
            prompt += "Now here is another object class that needs you to explain:\n"
            prompt += cls

            print(prompt)

            response = stream_llm_gpt(prompt, model=args.model)
            print(response)

            numTokens = getTokenLength(response)
            print("")
            print("Responded with " + str(numTokens) + " tokens.")
            print("")

            out += response
            out += '==========\n'
        out_rules[filename[:-3]] = out

    if not os.path.exists(args.output_folder):
        os.mkdir(args.output_folder)
    with open(os.path.join(args.output_folder, "object_rules.json"), "w") as f:
        json.dump(out_rules, f)

if __name__ == "__main__":
    main()