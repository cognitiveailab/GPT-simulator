import json
import os

data_folder = "data"

statistics = {}
for game in os.listdir(data_folder):
    if game == "wash-clothes":
        continue
    statistics[game] = {"states": 0, "action_verbs": set(), "object_types": set(), "object_instances": 0}
    for state_file in os.listdir(os.path.join(data_folder, game)):
        with open(os.path.join(data_folder, game, state_file)) as f:
            state_data = json.load(f)
        curr_state = state_data["current_state"]
        statistics[game]["states"] += 1
        statistics[game]["action_verbs"].add(state_data["action_state"]["lastAction"].split()[0])
        statistics[game]["object_instances"] += len(curr_state["objects"])
        for obj in curr_state["objects"]:
            statistics[game]["object_types"].add(obj["type"])

num_states = sum([statistics[game]["states"] for game in statistics])

print(num_states)
states = num_states/len(statistics)
action_verbs = sum([len(statistics[game]["action_verbs"]) for game in statistics])/len(statistics)
object_types = sum([len(statistics[game]["object_types"]) for game in statistics])/len(statistics)
object_instances = sum([statistics[game]["object_instances"] for game in statistics])/num_states

print(states, action_verbs, object_types, object_instances)