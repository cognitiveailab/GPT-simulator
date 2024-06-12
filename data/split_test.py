import argparse
import json
import random

num_states = 5
random.seed(0)

# arg parser
def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_distribution_file", type=str, default="data/dynamic_static_states_per_action.json")
    parser.add_argument("--games", type=str, default="experiments/games.json")
    parser.add_argument("--raw_data", type=str, default="data/data.jsonl")
    parser.add_argument("--output_train", type=str, default="data/train.jsonl")
    parser.add_argument("--output_test", type=str, default="data/test.jsonl")
    parser.add_argument("--num_samples", type=int, default=10)

    args = parser.parse_args()
    return args

args = parse_args()

with open(args.data_distribution_file) as f:
    data_distribution = json.load(f)

with open(args.games) as f:
    games = json.load(f)["games"]

test_states = {}
num_data = args.num_samples

# sample states
for game in games:
    data_states_positive = [] # states that changed by the action
    data_states_negative = [] # states that are not changed by the action

    for action in data_distribution[game]:
        if action not in ["tick", "score"]:
            positive_states = [s for s in data_distribution[game][action]['positive']]
            num_data_positive = min(num_states, len(positive_states))
            data_states_positive.extend(random.sample(positive_states, num_data_positive))

            negative_states = [s for s in data_distribution[game][action]['negative']]
            num_data_negative = min(num_states, len(negative_states))
            data_states_negative.extend(random.sample(negative_states, num_data_negative))
            num_data += num_data_positive
    print(f"Game: {game}, Positive: {len(data_states_positive)}, Negative: {len(data_states_negative)}")
    data_states = data_states_positive + data_states_negative
    test_states[game] = data_states

# get sampled stated from the data file
out_test = []
out_train = []
with open(args.raw_data) as f:
    lines = f.readlines()

for line in lines:
    line_data = json.loads(line)
    if line_data["game"] in test_states and line_data["state_id"] in test_states[line_data["game"]]:
        out_test.append(line)
    else:
        out_train.append(line)

with open(args.output_train, 'w') as f:
    for line in out_train:
        f.write(line)

with open(args.output_test, "w") as f:
    for line in out_test:
        f.write(line)
