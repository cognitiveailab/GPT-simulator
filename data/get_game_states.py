import argparse
import os
import copy
import sys
import json
import importlib
import random

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from scripts.evaluate import evaluate, make_game_state, compare_score_state

def get_state(text_game, last_action, max_UUID, game_name):
    # For single room games we should also add the rootObject (the room)
    if game_name not in ["metal-detector", "space-walk", "sunburn"]:
        allObjects = [text_game.rootObject]
    else:
        allObjects = []

    allObjects.extend(text_game.rootObject.getAllContainedObjectsRecursive())

    global_state = {"observation": text_game.observationStr,
                "look": text_game.actionLook(),
                "inventory": text_game.actionInventory() if hasattr(text_game.__class__, "actionInventory") else "No inventory available.",
                "taskDesc": text_game.getTaskDescription(),
                "lastAction": last_action,
                }
    state = []
    for obj in allObjects:
        state.append({"name": obj.name,
                      "uuid": obj.uuid,
                      "type": obj.__class__.__name__,
                      "properties": copy.deepcopy(obj.properties),
                      "contains": [o.name for o in obj.contains]})
    global_state["objects"] = state
    global_state["max_UUID"] = max_UUID
    return global_state

def output_state(state, state_out_folder, gameName, state_id):
    if not os.path.exists(os.path.join(state_out_folder, gameName)):
        os.mkdir(os.path.join(state_out_folder, gameName))

    with open(os.path.join(state_out_folder, gameName, f"{gameName}_{state_id}.json"), 'w') as f:
        json.dump(state, f)

def parse_playthrough(playthrough):
    '''
    input:
    playthrough: a list of lines of the playthrough file
    output:
    actions: a list of actions in the playthrough
    '''
    actions = []
    for line in playthrough:
        if line.startswith(">"):
            action = line[1:].strip()
            if action not in ["help", ""]:
                actions.append(action)

    return actions

def select_actions(valid_actions, max_actions_crawl, seed):
    action_dict = {}
    for action in valid_actions:
        action_verb = action.split()[0]
        if action_verb in action_dict:
            action_dict[action_verb].append(action)
        else:
            action_dict[action_verb] = [action]

    selected_actions = []
    random.seed(seed)
    for action_verb in action_dict:
        if max_actions_crawl <= 0 or len(action_dict[action_verb]) <= max_actions_crawl:
            selected_actions.extend(action_dict[action_verb])
        else:
            selected_actions.extend(random.sample(action_dict[action_verb], max_actions_crawl))

    return selected_actions

# compare two games states to see if the state changes
def state_change(curr_state, next_state):
    # we reuse the evaluate function for state comparison
    # the action argument is only used in the output_str, so we use an arbitrary 'look' as a placeholder
    num_errors,  _ = evaluate(make_game_state(curr_state), make_game_state(next_state), 'look')

    return num_errors != 0

def generate_game_state_data(args, game_name, gold_actions):
    # import the game
    if os.path.dirname(args.game_code_folder) not in sys.path:
        sys.path.append(args.game_code_folder)
    TextGame = importlib.import_module(game_name).TextGame
    game_random_seed = importlib.import_module(game_name).randomSeed

    crawled_states = []

    data_split = {"tick":{"positive": [], "negative": []}, "score":{"positive": [], "negative": []}}
    changed_state = {"action_change": [], "time_change":[]}
    state_id = 0

    for i in range(1,len(gold_actions)+1):
        # initialize the game
        game = TextGame(randomSeed=game_random_seed)
        game.generatePossibleActions()
        # step to the current action
        for action in gold_actions[:i-1]:
            game.step(action)
            game.generatePossibleActions()

        # crawl possible actions
        last_action = "" if i == 1 else gold_actions[i-2]
        max_UUID = importlib.import_module(game_name).UUID
        current_state = get_state(game, last_action, max_UUID, game_name)
        current_score_state = {"score": game.score, "gameOver": game.gameOver, "gameWon": game.gameWon}
        print(current_state)
        possible_actions = list(game.generatePossibleActions().keys())
        # it is possible that there are some invalid actions in the playthrough for testing corner cases
        if gold_actions[i-1] in possible_actions:
            possible_actions.remove(gold_actions[i-1])
        else:
            print(game_name)
            print(gold_actions[:i])
        # both look and look around are in the possible_actions, remove look around
        if gold_actions[i-1] != "look around":
            possible_actions.remove("look around")
        actions_to_take = select_actions(possible_actions, args.max_actions_crawl, args.random_seed+i)
        actions_to_take.append(gold_actions[i-1])


        # get game state changes for each action
        for action in actions_to_take:
            new_game = TextGame(randomSeed=game_random_seed)
            new_game.generatePossibleActions()
            for a in gold_actions[:i-1]:
                new_game.step(a)
                new_game.generatePossibleActions()

            print(gold_actions[:i-1])
            print(action)

            new_game.step_action(action)
            max_UUID = importlib.import_module(game_name).UUID
            action_state = get_state(new_game, action, max_UUID, game_name)
            new_game.step_tick()
            max_UUID = importlib.import_module(game_name).UUID
            tick_state = get_state(new_game, action, max_UUID, game_name)
            new_game.step_calculate_score()
            next_score_state = {"score": new_game.score, "gameOver": new_game.gameOver, "gameWon": new_game.gameWon}

            state_data = {"game": game_name, "state_id": state_id, "current_state": current_state, "action_state": action_state, "tick_state": tick_state, "current_score_state": current_score_state, "next_score_state": next_score_state}

            crawled_states.append(state_data)

            action_change = state_change(current_state, action_state)
            tick_change = state_change(action_state, tick_state)

            score_change = not compare_score_state(current_score_state, next_score_state)

            if tick_change:
                changed_state["time_change"].append(state_id)
            if action_change:
                changed_state["action_change"].append(state_id)


            action_verb = action.split(' ')[0]
            if action_verb not in data_split:
                data_split[action_verb] = {"positive": [], "negative": []}

            if action_change:
                data_split[action_verb]['positive'].append(state_id)
            else:
                data_split[action_verb]['negative'].append(state_id)

            if tick_change:
                data_split["tick"]["positive"].append(state_id)
            else:
                data_split["tick"]["negative"].append(state_id)

            if score_change:
                data_split["score"]["positive"].append(state_id)
            else:
                data_split["score"]["negative"].append(state_id)

            state_id += 1


    return crawled_states, data_split, changed_state


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--game_code_folder", type=str, default="data/games")
    parser.add_argument("--game_playthrough_folder", type=str, default="data/playthroughs")
    parser.add_argument("--output_file", type=str, default="data/data.jsonl")
    parser.add_argument("--data_split_output_path", type=str, default="dynamic_static_states_per_action.json")
    parser.add_argument("--changed_state_output_path", type=str, default="dynamic_states.json")
    parser.add_argument("--overwrite", action="store_true")

    parser.add_argument("--max_actions_crawl", type=int, default=-1, help="max number of actions to crawl per action verb")
    parser.add_argument("--random_seed", type=int, default=0)
    args = parser.parse_args()
    return args

def main():
    args = parse_args()

    data_split = {}
    changed_state = {}
    crawled_states = []

    if not args.overwrite:
        if os.path.exists(args.data_split_output_path):
            with open(args.data_split_output_path) as f:
                data_split = json.load(f)

        if os.path.exists(args.changed_state_output_path):
            with open(args.changed_state_output_path) as f:
                changed_state = json.load(f)

    game_files = os.listdir(args.game_code_folder)
    for game_filename in game_files:
        # There may be __pycache__ in the folder
        if not game_filename.endswith(".py"):
            continue
        game_name = os.path.basename(game_filename)[:-3]

        # parse game playthrough
        with open(os.path.join(args.game_playthrough_folder, f"{game_name}-playthrough.txt")) as f:
            playthrough = f.readlines()

        gold_actions = parse_playthrough(playthrough)

        crawled_states_game, data_split_game, changed_state_game = generate_game_state_data(args, game_name, gold_actions)
        crawled_states.extend(crawled_states_game)
        data_split[game_name] = data_split_game
        changed_state[game_name] = changed_state_game

    with open(args.output_file, "w") as f:
        for line in crawled_states:
            f.write(json.dumps(line) + "\n")

    with open(args.data_split_output_path, 'w') as f:
        json.dump(data_split, f)

    with open(args.changed_state_output_path, 'w') as f:
        json.dump(changed_state, f)

if __name__ == "__main__":
    main()