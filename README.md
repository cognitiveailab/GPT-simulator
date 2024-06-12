# Can Language Models Serve as Text-Based World Simulators?
This is the code base for the paper [Can Language Models Serve as Text-Based World Simulators?](https://arxiv.org/abs/2406.06485)

## Installation
```bash
pip install -r requirements.txt
```

## OpenAI API key
You need an OpenAI API key to run the code. The OpenAI API key should be saved as an environment variable. See the [OpenAI website](https://platform.openai.com/docs/quickstart?context=python) for detailed instructions.

## Data Generation
**In this section and all sections following, we always assume that you run the code from the root of this repository.**

We offer our data in the `data` folder. Unzip the `train.zip` and `test.zip` files to get the data `train.jsonl` and `test.jsonl`. `test.jsonl` contains all states transitions we used for our experiments and `train.jsonl` contains all remaining crawled transitions.

If you want to crawl the data your own, run
```bash
python data/get_game_states.py\
    --game_code_folder GAME_CODE_FOLDER\
    --game_playthrough_folder GAME_PLAYTHROUGH_FOLDER\
    --output_file OUTPUT_FILE\
    --data_split_output_path DATA_SPLIT_PATH\
    --changed_state_output_path CHANGED_STATE_PATH\
    --max_actions_crawl MAX_ACTIONS_CRAWL\
    --random_seed SEED\
    --overwrite
```
**GAME_CODE_FOLDER:** Folder that saves the game code. Default: `games`

**GAME_PLAYTHROUGH_FOLDER:** Folder that saves the game gold playthroughs. Default: `playthroughs`

**OUTPUT_FILE:** A JSONL file that stores all states crawled. Default: `data/data.jsonl`

**DATA_SPLIT_PATH:** The script will generate a json file that saves the state ids of dynamic and static states for each action. This is the output path of the json file.

**CHANGED_STATE_PATH:** The script will generate a json file that saves the ids all states that are changed by actions or over the time. This is the output path of the json file.

**MAX_ACTIONS_CRAWL:** The maximum number of actions to crawl per action verb per game.

**SEED:** Random seed. Default: 0.

**--overwrite:** overwrite existing data

This will generate a JSONL data file, a JSON file that stores the dynamic states of each action of each game, and a JSON file that stores all dynamic states of each game. You can further sample a test set from the dataset as we did in our experiments by running

```bash
python data/split_test.py\
    --data_distribution_file GAME_DISTRIBUTION_FILE\
    --games GAMES\
    --raw_data DATA\
    --output_train OUTPUT_TRAIN\
    --output_test OUTPUT_TEST\
    --num_samples NUM_SAMPLES
```
**GAME_DISTRIBUTION_FILE:** The JSON file that stores the dynamic and static states for each action of each game generated in the previous step. Default: data/dynamic_static_states_per_action.json

**GAMES**: Path of the JSON file that stores the names of all games and examples.

**RAW_DATA**: Path of the data JSONL generated in the previous step.

**OUTPUT_TRAIN:** Path to save the output train file.

**OUTPUT_TEST:** Path to save the output test file.

**NUM_SAMPLES:** Each game will sample NUM_SAMPLES dynamic states and NUM_SAMPLES static states.

## Rule generation
We offer our generated rules in `rules/`. We also provide the scripts to run them:
```bash
python [action|object|score]_desc_generation.py\
    --input_folder INPUT_FOLDER\
    --output_folder OUPUT_FOLDER\
    --model MODEL
```
**INPUT_FOLDER:** Folder of the game codel files. Default: data/games

**OUTPUT_FOLDER:** Output saving path

**MODEL:** Model used to generate the rules. We used `gpt-4-0125-preview` in our experiments.

## LLM as Simulator Experiments
Here is the command to run the simulation task. Arguments wrapped in square brackets are optional for some experiments.
```bash
python quest_gpt.py\
    --model MODEL\
    --output_prefix OUTPUT_PREFIX\
    --output_suffix OUTPUT_SUFFIX\
    --game_file_names GAME_FILE_NAMES\
    --total_shards NUM_SHARDS\
    --shard_idx SHARD\
    --state_data_folder DATA_FOLDER\
    --example_data EXAMPLE_DATA\
    --data_type DATA_TYPE\
    --output_folder OUTPUT_FOLDER\
    --rule_folder RULE_FOLDER\
    [--partial]\
    [--no-rule]
```

**MODEL:** OpenAI model to use. In our experiments we used `gpt-4-0125-preview` and `gpt-3.5-turbo-0125`.

**OUTPUT_PREFIX/SUFFIX:** The script will saves prediction results into one JSON file which store general statistics and one JSONL which stores all predicted states. The JSON file name will be `results_{OUTPUT_PREFIX}_{SHARD}{OUTPUT_SUFFIX}.json` and the name of the JSONL file will be `{OUTPUT_PREFIX}_{SHARD}{OUTPUT_SUFFIX}.jsonl`.

**GAME_FILE_NAMES:** By default, this is set to `games.json` which saves all game names. If you want to run some of the games or run on your own games, please edit this file or change to a new file.

**NUM_SHARDS:** total number of data shards

**SHARD:** the index of the shard to run. Zero base.

**DATA_FOLDER:**: Folder that saves all transition files. By default it is `data`.

**EXAMPLE_DATA**: Path to the JSON file that stores all example states.

**DATA_TYPE:** Types of input data. The value can be "action", "tick", "score", or "full", which corresponds to action-driven transitions, environment-driven transitions, game progress transitions, and the whole state transitions.

**OUTPUT_FOLDER:** Folder to save the result files.

**RULE_FOLDER:** Folders that saves the all game rules.

**--partial:** Include this flag for state difference prediction.

**--no-rule:** Include this flag for the no-rule experiments.

Here's an example to run on all games with the GPT-4o model, human-written rules (`--rule_folder ./rules/human_written_rules`), state difference prediction (`--partial`), and either whole state transitions (`--data_type full`), action-driven transitions (`--data_type action`), or environment-driven transitions (`--data_type tick`):

    python ./experiments/quest_gpt.py --model gpt-4o --output_prefix gpt4o_hwr_diff_full --rule_folder ./rules/human_written_rules --output_folder results --data_type full --partial
    python ./experiments/quest_gpt.py --model gpt-4o --output_prefix gpt4o_hwr_diff_action --rule_folder ./rules/human_written_rules --output_folder results --data_type action --partial
    python ./experiments/quest_gpt.py --model gpt-4o --output_prefix gpt4o_hwr_diff_tick --rule_folder ./rules/human_written_rules --output_folder results --data_type tick --partial

where `hwr` stands for human-written rules, `diff` stands for state difference prediction, and `full`, `action`, `tick`  stand for whole state transitions, action-driven transitions and environment-driven transitions.

## Results Analysis
We offer scripts to do analysis on model predictions.

The `results_analysis.py` will compute the general accuracy per game state as well as detailed per object property accuracy. Run the script by
```bash
python ./scripts/results_analysis.py\
    --prefix PREFIX\
    --suffix SUFFIX\
    --n_shards SHARDS\
    --output_folder OUTPUT_FOLDER\
    --exp_type EXP_TYPE\
    --results_folder RESULTS_FOLDER\
    --state_change_file STATE_CHANGE_FILE
```
**PREFIX/SUFFIX**, and **SHARDS** should correspond the arguments you used to run your experiments in previous steps.

**EXP_TYPE:** can be "action", "tick", "score", or "full". It is the same as the **DATA_TYPE** argument of `quest_gpt.py` script.

**RESULTS_FOLDER:** Folder where to save the results.

**STATE_CHANGE_FILE:** A JSON that saves all dynamic states. Default: dynamic_states.json

Here is an example to run the analysis on the results obtained at the previous step:

    python ./scripts/results_analysis.py --prefix gpt4o_hwr_diff_full --exp_type full --output_folder analysis
    python ./scripts/results_analysis.py --prefix gpt4o_hwr_diff_action --exp_type action --output_folder analysis
    python ./scripts/results_analysis.py --prefix gpt4o_hwr_diff_tick --exp_type tick --output_folder analysis

## Tables
To generate similar tables as shown in the paper, we provide the following script.

    python paper/gen_table.py analysis/*_state.csv --latex

## Histograms
To generate the stacked histograms as shown in the paper, we provide the following script.

    python paper/gen_figure.py --full analysis/gpt4o_hwr_diff_full_detail.csv --tick analysis/gpt4o_hwr_diff_tick_detail.csv --action analysis/gpt4o_hwr_diff_action_detail.csv --output gpt4o_hwr_diff.pdf

where `--full`, `--tick`, and `--action` are the detailed results files generated by the `results_analysis.py`. The `--output` argument specifies the output file name.
