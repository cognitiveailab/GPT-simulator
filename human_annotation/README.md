# Human Annotation
This subfolder contains all the scripts and data for the human annotation of the state transitions. The annotation was done for 5 games. The games are:

  - bath-tub-water-temperature
  - clean-energy
  - metal-detector
  - mix-paint
  - take-photo

### Instructions to the annotators
The annotators were given the following instructions:

  1. Make a copy of the `template/` folder and rename it to a unique ID, e.g. `annotation_#`.
  2. For each game subfolder, there will be a `rules/` folder which contains the descriptions of the actions (in `rules/action_rules.txt`) and the objects (in `rules/obj_rule.txt`). Get familiar with the rules.
  3. For each game subfolder, there will be list of pair of JSON files:
    - `{game_name}_{state_id}.json` represents the current state and the action to be taken. **(DO NOT CHANGE)**.
    - `{game_name}_{state_id}_annotation.json` should be updated to represent the resulting action state after taking the aforementioned action. For convenience, the `*_annotation.json` file contains the same state as the original state file as a starting point. **(THIS SHOULD BE UPDATED)**.
  4. Once you have updated all `*_annotation.json` file for all games, please zip the whole folder and send it back to us.

**Note:** In the root of the `template/` folder, the `example/` subfolder shows a self-contained example of an annotated state transition from a game not being asked to annotate.


### Analyzing the annotations
The annotations were analyzed using the `results_analysis.py` script. The script computes the general accuracy per game state as well as detailed per object property accuracy. The script can be run by:

    python analyze_annotation.py --data_path DATA_FOLDER --annotation_path ANNOTATION_FOLDER

**Note:** Some of the underlying data representation as slightly changed since we performed the human study. To reproduce the human annotation results from the paper, use the `--paper` flag which will load a copy of the original data stored in `./data`. Here's an example:

    python analyze_annotation.py --paper --annotation_path human_annotation_1


### Generating the data for human annotation
The `template/` folder for the human annotator was generated using the `generate_human_annotator_data.py` script. The script can be run by:

    python generate_human_annotator_data.py

**Note:** TODO: this script needs to be update to reflect the new structure of the code repository.