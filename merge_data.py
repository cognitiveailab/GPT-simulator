import os
import json

with open("experiments/sampled_states.json") as f:
    test_states = json.load(f)

test_out = []
train_out = []

for game in os.listdir("data"):
    if game in ["games", "playthroughs"]:
        continue

    for file in os.listdir(os.path.join("data",game)):
        with open(os.path.join("data", game, file)) as f:
            data = json.load(f)
        data["game"] = game
        state_id = int(file.split('.')[0].split('_')[-1])
        data["state_id"] = state_id
        if game in test_states and state_id in test_states[game]:
            test_out.append(data)
        else:
            train_out.append(data)

with open("data/train.jsonl", 'w') as f:
    for line in train_out:
        f.write(json.dumps(line) + "\n")

with open("data/test.jsonl", "w") as f:
    for line in test_out:
        f.write(json.dumps(line) + "\n")