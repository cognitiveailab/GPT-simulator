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
    parser.add_argument("--input_folder", type=str, default="data/games")
    parser.add_argument("--output_folder", type=str, default="rules/llm_generated_rules")
    parser.add_argument("--model", type=str, default="gpt-4-0125-preview")

    args = parser.parse_args()
    return args

def main():
    args = parse_args()

    out = {}
    for game_file in os.listdir(args.input_folder)[:2]:
        if not game_file.endswith(".py"):
            continue

        with open(os.path.join(args.input_folder, game_file)) as f:
            game_code = f.read()

        prompt = "You will be given a Python program which defines an a text game. Describe how the game can be won or lose, and how game scores can be earned based on your understanding of the calculateScore function in the TextGame class. \n"

        prompt += "Here is the code of the game. Do not describe the main function.\n"
        prompt += game_code

        print(prompt)
        response = stream_llm_gpt(prompt, model=args.model)
        print(response)

        numTokens = getTokenLength(response)
        print("")
        print("Responded with " + str(numTokens) + " tokens.")
        print("")
        out[game_file[:-3]] = response

    if not os.path.exists(args.output_folder):
        os.mkdir(args.output_folder)
    with open(os.path.join(args.output_folder, "score_rules.json"), "w") as f:
        json.dump(out, f)

if __name__ == "__main__":
    main()