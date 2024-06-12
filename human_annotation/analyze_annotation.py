import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scripts'))

import json
import argparse

from evaluate import get_state_diff_detail_v2, load_jsonl_as_dict


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_path", type=str, default="../data")
    parser.add_argument("--annotation_path", type=str, default="human_annotation_1")
    parser.add_argument("--paper", action="store_true", help="Use the same data to reproduce the human annotation results from the paper.")
    parser.add_argument("--verbose", action="store_true", help="Verbose mode.")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    data_path = args.data_path
    annotation_path = args.annotation_path

    if args.paper:
        data_path = "./data"

    gt_data = load_jsonl_as_dict(os.path.join(data_path, "test.jsonl"))

    # parse the diff return to a boolean of correct of not
    def parse_diff(diffs):
        is_same = True
        for key in ['added', 'removed']:
            if len(diffs[key]) > 0:
                is_same = False
        for prop in diffs['modified']:
            if prop[-1] != 1:
                is_same = False
        return is_same

    for game in sorted(os.listdir(annotation_path)):
        if game == "example":
            continue

        print(f"Evaluating {game}")
        total = 0
        correct = 0
        for file in os.listdir(os.path.join(annotation_path, game)):
            if not file.endswith('annotation.json'):
                continue

            try:
                with open(os.path.join(annotation_path, game, file)) as f:
                    annotation_data = json.load(f)
            except json.decoder.JSONDecodeError as e:
                print(e)
                total += 1
            else:

                if args.verbose:
                    print(f"File: {file}")

                predicted_state = annotation_data["action_state"]
                state_file = annotation_data["state_file"]
                state_id = int(state_file.split('.')[0].split('_')[-1])

                if args.paper:
                    gt_state = gt_data[game][state_id]["next_state"]["objects"]
                else:
                    gt_state = gt_data[game][state_id]["action_state"]["objects"]

                # compare annotation with ground truth
                diffs = get_state_diff_detail_v2({"game_state":gt_state}, {"game_state":predicted_state})
                is_correct = parse_diff(diffs)
                total += 1
                if is_correct:
                    correct += 1
                else:
                    diffs_out = {
                        "added": diffs["added"],
                        "removed": diffs["removed"],
                        "modified": [s for s in diffs["modified"] if s[-1] != 1]
                    }

                if args.verbose:
                    print(is_correct)
                    if not is_correct:
                        print(diffs_out)

        print(f"Game {game}, acc: {correct/total}")
