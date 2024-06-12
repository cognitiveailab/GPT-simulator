import os
import json
import random

random.seed(7)

# We read the data from the results to keep them consistant with data of other experimend
data_folder = "results"
data_prefix = "gpt-4-0125-preview_mar08_diff_hwr_action"
total_num_shards = 4

target_games = ["clean-energy", "take-photo", "metal-detector", "mix-paint", "bath-tub-water-temperature"]

data_for_human = {}
for i in range(total_num_shards):
    with open(f"{data_folder}/results_{data_prefix}_shard_{total_num_shards}_{i}.json") as f:
        data = json.load(f)
        for game in data:
            if game in target_games:
                data_for_human[game] = data[game]

# stores whether GPT-4 predicts each dynamic/static state correct
distribution = {}
for game in data_for_human:
    distribution[game] = {"dynamic": {"correct":[], "wrong":[]},
                              "static": {"correct":[], "wrong":[]}}
    for state_id in data_for_human[game]:
        if state_id in ['total_states','total_errors', "time"]:
            continue
        state = data_for_human[game][state_id]


        if state["state_change"]:
            if state["objprop_errors"] == 0:
                distribution[game]["dynamic"]["correct"].append(state_id)
            else:
                distribution[game]["dynamic"]["wrong"].append(state_id)
        else:
            if state["objprop_errors"] == 0:
                distribution[game]["static"]["correct"].append(state_id)
            else:
                distribution[game]["static"]["wrong"].append(state_id)

# sample data
sample_size = 10 # in our data correct + wrong >= 10
output_dir = "human_annotation"
data_for_human_sampled = {}
for game in distribution:
    data_for_human_sampled[game] = []
    # dynamic games
    if len(distribution[game]["dynamic"]["correct"]) < 5:
        data_for_human_sampled[game] += distribution[game]["dynamic"]["correct"] +\
                                    random.sample(distribution[game]["dynamic"]["wrong"], sample_size - len(distribution[game]["dynamic"]["correct"]))
    elif len(distribution[game]["dynamic"]["wrong"]) < 5:
        data_for_human_sampled[game] += distribution[game]["dynamic"]["wrong"] +\
                                    random.sample(distribution[game]["dynamic"]["correct"], sample_size - len(distribution[game]["dynamic"]["wrong"]))
    else:
        data_for_human_sampled[game] += random.sample(distribution[game]["dynamic"]["wrong"], 5) +\
                                    random.sample(distribution[game]["dynamic"]["correct"], 5)

    # static games
    if len(distribution[game]["static"]["correct"]) < 5:
        data_for_human_sampled[game] += distribution[game]["static"]["correct"] +\
                                    random.sample(distribution[game]["static"]["wrong"], sample_size - len(distribution[game]["static"]["correct"]))
    elif len(distribution[game]["static"]["wrong"]) < 5:
        data_for_human_sampled[game] += distribution[game]["static"]["wrong"] +\
                                    random.sample(distribution[game]["static"]["correct"], sample_size - len(distribution[game]["static"]["wrong"]))
    else:
        data_for_human_sampled[game] += random.sample(distribution[game]["static"]["wrong"], 5) +\
                                    random.sample(distribution[game]["static"]["correct"], 5)

# output
for game in data_for_human_sampled:
    if not os.path.exists(os.path.join(output_dir, game)):
        os.mkdir(os.path.join(output_dir, game))
    for state_id in data_for_human_sampled[game]:
        path = os.path.join("data_v2", game, f"{state_id}.json")
        with open(path) as f:
            state_info = json.load(f)

        state_info_output = {}
        state_info_output["game_name"] = state_id.split("_")[0]
        state_info_output["state_file"] = f"{state_id}.json"
        state_info_output["task_desc"] = state_info["current_state"]["taskDesc"]
        state_info_output["action_to_take"] = state_info["action_state"]["lastAction"]
        state_info_output["current_state"] = state_info["current_state"]["objects"]

        with open(os.path.join(output_dir, game, f"{state_id}.json"), "w") as f:
            json.dump(state_info_output, f, indent=4)

        state_info_output_annotation = {}
        state_info_output_annotation["game_name"] = state_id.split("_")[0]
        state_info_output_annotation["state_file"] = f"{state_id}.json"
        state_info_output_annotation["task_desc"] = state_info["current_state"]["taskDesc"]
        state_info_output_annotation["action_to_take"] = state_info["action_state"]["lastAction"]
        state_info_output_annotation["action_state"] = state_info["current_state"]["objects"]

        with open(os.path.join(output_dir, game, f"{state_id}_annotation.json"), "w") as f:
            json.dump(state_info_output_annotation, f, indent=4)

# generate an example
example_state_id = "dishwasher_8872"
example_info_output = {}
example_info_output["game_name"] = "dishwasher"
example_info_output["state_file"] = f"{example_state_id}.json"
example_info_output["task_desc"] = 'Your task is to wash the dirty dishes.'
example_info_output["action_to_take"] = 'put plate (ID: 5) in dirty cup (ID: 4)'
example_info_output["current_state"] = [{'name': 'agent (ID: 0)', 'uuid': 0, 'type': 'Agent', 'properties': {'isContainer': True, 'isMoveable': True, 'isOpenable': False, 'isOpen': True, 'containerPrefix': 'in'}, 'contains': ['plate (ID: 5)', 'mug (ID: 6)', 'knife (ID: 7)']}, {'name': 'plate (ID: 5)', 'uuid': 5, 'type': 'Dish', 'properties': {'isContainer': True, 'isMoveable': True, 'isOpenable': False, 'isOpen': True, 'containerPrefix': 'on', 'dishType': 'plate', 'isDirty': True, 'foodMessName': 'orange'}, 'contains': []}, {'name': 'mug (ID: 6)', 'uuid': 6, 'type': 'Dish', 'properties': {'isContainer': True, 'isMoveable': True, 'isOpenable': False, 'isOpen': True, 'containerPrefix': 'in', 'dishType': 'mug', 'isDirty': True, 'foodMessName': 'sandwhich'}, 'contains': []}, {'name': 'knife (ID: 7)', 'uuid': 7, 'type': 'Dish', 'properties': {'isContainer': True, 'isMoveable': True, 'isOpenable': False, 'isOpen': True, 'containerPrefix': 'in', 'dishType': 'knife', 'isDirty': True, 'foodMessName': 'apple (ID: 11)'}, 'contains': []}, {'name': 'dishwasher (ID: 2)', 'uuid': 2, 'type': 'DishWasher', 'properties': {'isContainer': True, 'isMoveable': False, 'isOpenable': True, 'isOpen': True, 'containerPrefix': 'in', 'isDevice': True, 'isActivatable': True, 'isOn': False, 'cycleStage': 0, 'finishedCycle': False}, 'contains': ['cup (ID: 4)']}, {'name': 'cup (ID: 4)', 'uuid': 4, 'type': 'Dish', 'properties': {'isContainer': True, 'isMoveable': True, 'isOpenable': False, 'isOpen': True, 'containerPrefix': 'in', 'dishType': 'cup', 'isDirty': True, 'foodMessName': 'peanut butter'}, 'contains': []}, {'name': 'bottle of dish soap (ID: 3)', 'uuid': 3, 'type': 'DishSoapBottle', 'properties': {'isContainer': False, 'isMoveable': True, 'isDevice': True, 'isActivatable': True, 'isOn': False}, 'contains': []}, {'name': 'glass (ID: 8)', 'uuid': 8, 'type': 'Dish', 'properties': {'isContainer': True, 'isMoveable': True, 'isOpenable': False, 'isOpen': True, 'containerPrefix': 'in', 'dishType': 'glass', 'isDirty': False}, 'contains': []}, {'name': 'bowl (ID: 9)', 'uuid': 9, 'type': 'Dish', 'properties': {'isContainer': True, 'isMoveable': True, 'isOpenable': False, 'isOpen': True, 'containerPrefix': 'in', 'dishType': 'bowl', 'isDirty': False}, 'contains': []}, {'name': 'banana (ID: 10)', 'uuid': 10, 'type': 'Food', 'properties': {'isContainer': False, 'isMoveable': True, 'isFood': True}, 'contains': []}]

with open(os.path.join(output_dir, "example", f"{example_state_id}.json"), "w") as f:
    json.dump(example_info_output, f, indent=4)

example_info_output_annotation = {}
example_info_output_annotation["game_name"] = "dishwasher"
example_info_output_annotation["state_file"] = f"{example_state_id}.json"
example_info_output_annotation["task_desc"] = 'Your task is to wash the dirty dishes.'
example_info_output_annotation["action_to_take"] = 'put plate (ID: 5) in dirty cup (ID: 4)'
example_info_output_annotation["action_state"] = [{'name': 'agent (ID: 0)', 'uuid': 0, 'type': 'Agent', 'properties': {'isContainer': True, 'isMoveable': True, 'isOpenable': False, 'isOpen': True, 'containerPrefix': 'in'}, 'contains': ['mug (ID: 6)', 'knife (ID: 7)']}, {'name': 'mug (ID: 6)', 'uuid': 6, 'type': 'Dish', 'properties': {'isContainer': True, 'isMoveable': True, 'isOpenable': False, 'isOpen': True, 'containerPrefix': 'in', 'dishType': 'mug', 'isDirty': True, 'foodMessName': 'sandwhich'}, 'contains': []}, {'name': 'knife (ID: 7)', 'uuid': 7, 'type': 'Dish', 'properties': {'isContainer': True, 'isMoveable': True, 'isOpenable': False, 'isOpen': True, 'containerPrefix': 'in', 'dishType': 'knife', 'isDirty': True, 'foodMessName': 'apple (ID: 11)'}, 'contains': []}, {'name': 'dishwasher (ID: 2)', 'uuid': 2, 'type': 'DishWasher', 'properties': {'isContainer': True, 'isMoveable': False, 'isOpenable': True, 'isOpen': True, 'containerPrefix': 'in', 'isDevice': True, 'isActivatable': True, 'isOn': False, 'cycleStage': 0, 'finishedCycle': False}, 'contains': ['cup (ID: 4)']}, {'name': 'cup (ID: 4)', 'uuid': 4, 'type': 'Dish', 'properties': {'isContainer': True, 'isMoveable': True, 'isOpenable': False, 'isOpen': True, 'containerPrefix': 'in', 'dishType': 'cup', 'isDirty': True, 'foodMessName': 'peanut butter'}, 'contains': ['plate (ID: 5)']}, {'name': 'plate (ID: 5)', 'uuid': 5, 'type': 'Dish', 'properties': {'isContainer': True, 'isMoveable': True, 'isOpenable': False, 'isOpen': True, 'containerPrefix': 'on', 'dishType': 'plate', 'isDirty': True, 'foodMessName': 'orange'}, 'contains': []}, {'name': 'bottle of dish soap (ID: 3)', 'uuid': 3, 'type': 'DishSoapBottle', 'properties': {'isContainer': False, 'isMoveable': True, 'isDevice': True, 'isActivatable': True, 'isOn': False}, 'contains': []}, {'name': 'glass (ID: 8)', 'uuid': 8, 'type': 'Dish', 'properties': {'isContainer': True, 'isMoveable': True, 'isOpenable': False, 'isOpen': True, 'containerPrefix': 'in', 'dishType': 'glass', 'isDirty': False}, 'contains': []}, {'name': 'bowl (ID: 9)', 'uuid': 9, 'type': 'Dish', 'properties': {'isContainer': True, 'isMoveable': True, 'isOpenable': False, 'isOpen': True, 'containerPrefix': 'in', 'dishType': 'bowl', 'isDirty': False}, 'contains': []}, {'name': 'banana (ID: 10)', 'uuid': 10, 'type': 'Food', 'properties': {'isContainer': False, 'isMoveable': True, 'isFood': True}, 'contains': []}]

with open(os.path.join(output_dir, "example", f"{example_state_id}_annotation.json"), "w") as f:
    json.dump(example_info_output_annotation, f, indent=4)


