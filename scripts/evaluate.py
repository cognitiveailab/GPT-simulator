from collections import defaultdict
import json


def load_jsonl_as_dict(jsonl_path):
    """ Load the jsonl and convert it to a nested dictionary first indexed by game, then by state_id. """
    out = defaultdict(dict)
    with open(jsonl_path) as f:
        for line in f:
            line_data = json.loads(line)
            game = line_data["game"]
            out[game][line_data["state_id"]] = line_data

    return dict(out)


def compare(pred, target):
    if pred["properties"] != target["properties"]:
        return False
    if sorted(pred["contains"]) != sorted(target["contains"]):
        return False
    return True


def make_game_state(raw_json):
    return {"game_state": raw_json["objects"]}


def make_game_state_partial(current_state, next_state):
    '''
    raw_json: json read directly from json data files
    '''
    state_diffs, score_diff = get_state_diff(current_state, next_state)

    diffs = {"modified": [], "removed":[], "score":{}}

    for uuid in state_diffs:
        _, state_2 = state_diffs[uuid]
        if state_2 is not None:
            diffs["modified"].append(state_2)
        else:
            diffs["removed"].append(uuid)

    if score_diff is not None:
        diffs["score"] = score_diff[1]
    return diffs


def make_state_for_comprison(states):
    obj_dict = {}
    score = {}
    for state in states:
        if 'uuid' in state:
            obj_dict[state['uuid']] = state
        elif 'score' in state:
            score = state
    return obj_dict, score


def compare_dict(dict_1, dict_2):
    """ compare if two dictionary are the same """
    if len(dict_1) != len(dict_2):
        return False
    for key in dict_1:
        if key not in dict_2:
            return False
        # We don't care it is a list/tuple
        if type(dict_1[key]) in [list, tuple] and type(dict_2[key]) in [list, tuple]:
            if list(dict_1[key]) != list(dict_2[key]):
                return False
        elif type(dict_1[key]) == dict and type(dict_2[key]) == dict:
            if not compare_dict(dict_1[key], dict_2[key]):
                return False
        elif dict_1[key] != dict_2[key]:
            return False
    return True


def compare_score_state(score_state_1, score_state_2):
    return compare_dict(score_state_1, score_state_2)


def evaluate_score(pred, target):
    try:
        if len(pred) != len(target):
            return 1, "Wrong number of keys"
        num_errors = 0
        out_str = []
        for key in target:
            if key not in pred:
                num_errors += 1
                out_str.append(f"Missing key {key}")
            else:
                if pred[key] != target[key]:
                    num_errors += 1
                    out_str.append(f"Wrong value for the key {key}. Prediction: {pred[key]}, Target: {target[key]}")
        if num_errors == 0:
            return num_errors, "Same."
        else:
            return num_errors, '\n'.join(out_str)
    except:
        return -1, "Wrong format"


def evaluate(prediction, target, last_action, evaluate_score=False):
    num_errors = 0
    num_errors_score = 0

    out_str = ''
    try:
        target, score_t = make_state_for_comprison(target["game_state"])

        prediction, score_p = make_state_for_comprison(prediction["game_state"])

        out_str += f"last_action: {last_action}\n\n"

        # compare objects
        for uuid in target:
            if uuid not in prediction:
                out_str += f"Missing object: {target[uuid]['name']}\n\n"
                num_errors += 1
            else:
                if "properties" not in prediction[uuid]:
                    out_str += f'No prediction of properties: {target[uuid]["name"]}\n\n'
                    num_errors += 1
                else:
                    t = target[uuid]["properties"]
                    p = prediction[uuid]["properties"]

                    for key in t:
                        if key not in p:
                            out_str += f'Missing key: {key} for {target[uuid]["name"]}\n\n'
                            num_errors += 1
                        else:
                            if type(t[key]) in [list, tuple] and type(p[key]) in [list, tuple]:
                                # We don't care it is a list/tuple
                                if list(t[key]) != list(p[key]):
                                    out_str += f"Difference in {key} of {target[uuid]['name']}:\n"
                                    out_str += f"Prediction: {p[key]}\n"
                                    out_str += f"Target: {t[key]}\n\n"
                                    num_errors += 1
                            elif type(t[key]) == dict and type(p[key]) == dict:
                                if not compare_dict(t[key], p[key]):
                                    out_str += f"Difference in {key} of {target[uuid]['name']}:\n"
                                    out_str += f"Prediction: {p[key]}\n"
                                    out_str += f"Target: {t[key]}\n\n"
                                    num_errors += 1
                            else:
                                if t[key] != p[key]:
                                    out_str += f"Difference in {key} of {target[uuid]['name']}:\n"
                                    out_str += f"Prediction: {p[key]}\n"
                                    out_str += f"Target: {t[key]}\n\n"
                                    num_errors += 1

                if "contains" not in prediction[uuid]:
                    out_str += f'No prediction of contains: {target[uuid]["name"]}\n\n'
                    num_errors += 1
                else:
                    # We don't care the order of contains
                    if sorted(target[uuid]["contains"]) != sorted(prediction[uuid]["contains"]):
                        out_str += f"Difference in contains of {target[uuid]['name']}:\n"
                        out_str += f"Prediction: {prediction[uuid]['contains']}\n"
                        out_str += f"Target: {target[uuid]['contains']}\n\n"
                        num_errors += 1


        # compare scores
        if evaluate_score:
            for key in score_t:
                if key not in score_p:
                    out_str += f'Missing key: {key} for scoring\n\n'
                    num_errors_score += 1
                else:
                    if score_t[key] != score_p[key]:
                        out_str += f"Difference in {key} for scoring:\n"
                        out_str += f"Prediction: {score_p[key]}\n"
                        out_str += f"Target: {score_t[key]}\n\n"
                        num_errors_score += 1

    except:
        out_str = "Wrong prediction format"
        if evaluate_score:
            return -1, -1, out_str
        else:
            return -1, out_str
    if evaluate_score:
        out_str += f"Total errors: {num_errors}, Total score errors: {num_errors_score}\n"
    else:
        out_str += f"Total errors: {num_errors}\n"
    out_str += "-------------------------------------------------------------------\n"

    if evaluate_score:
        return num_errors, num_errors_score, out_str
    else:
        return num_errors, out_str


def get_state_diff(state_1, state_2):
    state_1, score_1 = make_state_for_comprison(state_1["game_state"])

    state_2, score_2 = make_state_for_comprison(state_2["game_state"])

    diffs = {}

    # compare objects
    for uuid in state_1:
        if uuid not in state_2:
            diffs[uuid] = (state_1, None) # an object is removed
            continue
        # compare properties
        property_1 = state_1[uuid]["properties"]
        property_2 = state_2[uuid]["properties"]

        for key in property_1:
            if key not in property_2:
                diffs[uuid] = (state_1[uuid], state_2[uuid])
                break
            else:
                if type(property_1[key]) in [list, tuple] and type(property_2[key]) in [list, tuple]:
                    # We don't care it is a list/tuple
                    if list(property_1[key]) != list(property_2[key]):
                        diffs[uuid] = (state_1[uuid], state_2[uuid])
                        break
                elif type(property_1[key]) == dict and type(property_2[key]) == dict:
                    if not compare_dict(property_1[key], property_2[key]):
                        diffs[uuid] = (state_1[uuid], state_2[uuid])
                        break
                else:
                    if property_1[key] != property_2[key]:
                        diffs[uuid] = (state_1[uuid], state_2[uuid])
                        break

        # compare contained objects
        # We don't care the order of contains
        if uuid not in diffs and sorted(state_1[uuid]["contains"]) != sorted(state_2[uuid]["contains"]):
            diffs[uuid] = (state_1[uuid], state_2[uuid])

    # find new objects created
    for uuid in state_2:
        if uuid not in state_1:
            diffs[uuid] = (None, state_2)

    score_diff = None
    # compare scores
    for key in score_1:
        if key not in score_1:
            score_diff = (score_1, score_2)
            break
        else:
            if score_1[key] != score_2[key]:
                score_diff = (score_1, score_2)
                break

    return diffs, score_diff


def get_state_diff_detail(state_1, state_2):
    """ list the diffs in each object property """
    state_1, score_1 = make_state_for_comprison(state_1["game_state"])

    state_2, score_2 = make_state_for_comprison(state_2["game_state"])

    diffs = {"added":[], "removed":[], "modified":[], "same":[]}

    # compare objects
    for uuid in state_1:
        is_same = True
        if uuid not in state_2:
            diffs["removed"].append((state_1[uuid], None)) # an object is removed
            is_same = False
            continue
        # compare properties
        property_1 = state_1[uuid]["properties"]
        property_2 = state_2[uuid]["properties"]

        for key in property_1:
            if key not in property_2:
                diffs["modified"].append((key, state_1[uuid], None, 2))
                is_same = False
            else:
                if type(property_1[key]) in [list, tuple] and type(property_2[key]) in [list, tuple]:
                    # We don't care it is a list/tuple
                    if list(property_1[key]) != list(property_2[key]):
                        diffs["modified"].append((key, state_1[uuid], state_2[uuid], 0))
                        is_same = False
                    else:
                        diffs["modified"].append((key, state_1[uuid], state_2[uuid], 1))
                elif type(property_1[key]) == dict and type(property_2[key]) == dict:
                    if not compare_dict(property_1[key], property_2[key]):
                        diffs["modified"].append((key, state_1[uuid], state_2[uuid], 0))
                        is_same = False
                    else:
                        diffs["modified"].append((key, state_1[uuid], state_2[uuid], 1))
                else:
                    if property_1[key] != property_2[key]:
                        diffs["modified"].append((key, state_1[uuid], state_2[uuid], 0))
                        is_same = False
                    else:
                        diffs["modified"].append((key, state_1[uuid], state_2[uuid], 1))

        for key in property_2:
            if key not in property_1:
                diffs["modified"].append((key, state_1[uuid], state_2[uuid], 3))
                is_same = False

        # compare contained objects
        # We don't care the order of contains
        if sorted(state_1[uuid]["contains"]) != sorted(state_2[uuid]["contains"]):
            diffs["modified"].append(('contains', state_1[uuid], state_2[uuid], 0))
            is_same = False
        else:
            diffs["modified"].append(('contains', state_1[uuid], state_2[uuid], 1))

        if is_same:
            diffs["same"].append(uuid)

    # find new objects created
    for uuid in state_2:
        if uuid not in state_1:
            diffs["added"].append((None, state_2[uuid]))

    score_diff = []
    # compare scores
    # score_code: 0: not the same, 1: same, 2: missing, 3: should not have the key
    for key in score_1:
        if key not in score_2:
            score_diff.append((key, score_1[key], None, 2))
        else:
            if score_1[key] != score_2[key]:
                score_diff.append((key, score_1, score_2, 0))
            else:
                score_diff.append((key, score_1, score_2, 1))

    for key in score_2:
        if key not in score_1:
            score_diff.append((key, None, score_2[key], 3))

    return diffs, score_diff


def get_state_diff_detail_v2(state_1, state_2):
    """ list the diffs in each object property

    This version is used for the experiments that split action and tick apart
    """
    state_1, _ = make_state_for_comprison(state_1["game_state"])

    state_2, _ = make_state_for_comprison(state_2["game_state"])

    diffs = {"added":[], "removed":[], "modified":[], "same":[]}

    # compare objects
    for uuid in state_1:
        is_same = True
        if uuid not in state_2:
            diffs["removed"].append((state_1[uuid], None)) # an object is removed
            is_same = False
            continue
        # compare properties
        property_1 = state_1[uuid]["properties"]
        property_2 = state_2[uuid]["properties"]

        for key in property_1:
            if key not in property_2:
                diffs["modified"].append((key, state_1[uuid], None, 2))
                is_same = False
            else:
                if type(property_1[key]) in [list, tuple] and type(property_2[key]) in [list, tuple]:
                    # We don't care it is a list/tuple
                    if list(property_1[key]) != list(property_2[key]):
                        diffs["modified"].append((key, state_1[uuid], state_2[uuid], 0))
                        is_same = False
                    else:
                        diffs["modified"].append((key, state_1[uuid], state_2[uuid], 1))
                elif type(property_1[key]) == dict and type(property_2[key]) == dict:
                    if not compare_dict(property_1[key], property_2[key]):
                        diffs["modified"].append((key, state_1[uuid], state_2[uuid], 0))
                        is_same = False
                    else:
                        diffs["modified"].append((key, state_1[uuid], state_2[uuid], 1))
                else:
                    if property_1[key] != property_2[key]:
                        diffs["modified"].append((key, state_1[uuid], state_2[uuid], 0))
                        is_same = False
                    else:
                        diffs["modified"].append((key, state_1[uuid], state_2[uuid], 1))

        for key in property_2:
            if key not in property_1:
                diffs["modified"].append((key, state_1[uuid], state_2[uuid], 3))
                is_same = False

        # compare contained objects
        # We don't care the order of contains
        #if sorted(state_1[uuid]["contains"]) != sorted(state_2[uuid]["contains"]):
        if sorted(state_1[uuid].get("contains", [])) != sorted(state_2[uuid].get("contains", [])):
            diffs["modified"].append(('contains', state_1[uuid], state_2[uuid], 0))
            is_same = False
        else:
            diffs["modified"].append(('contains', state_1[uuid], state_2[uuid], 1))

        if is_same:
            diffs["same"].append(uuid)

    # find new objects created
    for uuid in state_2:
        if uuid not in state_1:
            diffs["added"].append((None, state_2[uuid]))

    # score_diff = []
    # # compare scores
    # # score_code: 0: not the same, 1: same, 2: missing, 3: should not have the key
    # for key in score_1:
    #     if key not in score_2:
    #         score_diff.append((key, score_1[key], None, 2))
    #     else:
    #         if score_1[key] != score_2[key]:
    #             score_diff.append((key, score_1, score_2, 0))
    #         else:
    #             score_diff.append((key, score_1, score_2, 1))

    # for key in score_2:
    #     if key not in score_1:
    #         score_diff.append((key, None, score_2[key], 3))

    return diffs