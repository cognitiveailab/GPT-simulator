import os

import numpy as np
import pandas as pd
from glob import glob

import argparse


def parse_args():
    parser = argparse.ArgumentParser(description="Create a table with the results of the state analysis")
    parser.add_argument("filenames", nargs='*',
                        help="CSV files with the state analysis results. Defaut: ./analysis/*_state.csv")
    parser.add_argument("--latex", action="store_true", help="Output the table in LaTeX format")

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    if not args.filenames:
        filenames = sorted(glob("./analysis/*_state.csv"))

    print(f"Found {len(filenames)} files")

    all_data = pd.DataFrame()
    for filename in filenames:
        name = os.path.basename(filename).split("_state.csv")[0]
        keys = name.split("_")

        data = pd.read_csv(filename)
        print(f"Reading file: {filename} ({len(data)} datapoints)")
        # add the keys to the data
        data['model'] = keys[0]
        data['data'] = keys[1]
        data['partial'] = keys[2]
        data['rule'] = keys[3]
        data['transition'] = keys[4]

        # concatenate the data to the all_data dataframe
        all_data = pd.concat([all_data, data], ignore_index=True)

    # Clone the data
    static_data = all_data.copy()
    dynamic_data = all_data.copy()
    static_data["state_change"] = "static"
    dynamic_data["state_change"] = "dynamic"
    static_data["accuracy"] = all_data['correct_unchanged'] / all_data['total_unchanged_states']
    dynamic_data["accuracy"] = all_data['correct_changed'] / all_data['total_changed_states']

    # Concatenate the data
    all_data = pd.concat([static_data, dynamic_data], ignore_index=True)

    # Drop the columns that are not needed
    all_data.drop(columns=['correct_unchanged', 'total_unchanged_states', 'correct_changed', 'total_changed_states'], inplace=True)

    # drop model
    all_data.drop(columns=['model'], inplace=True)

    results = all_data.copy()

    # Use this orderining for the transition column: [full, action, tick]
    results['transition'] = pd.Categorical(results['transition'], categories=['full', 'action', 'tick'], ordered=True)
    results['transition'] = results['transition'].replace('full', r'$\mathcal{F}$')
    results['transition'] = results['transition'].replace('action', r'$\mathcal{F}_\text{act}$')
    results['transition'] = results['transition'].replace('tick', r'$\mathcal{F}_\text{env}$')

    # Rename partial value 'all' to 'full'
    results['partial'] = results['partial'].replace('all', 'Full')
    results['partial'] = results['partial'].replace('diff', 'Diff')
    results['partial'] = pd.Categorical(results['partial'], categories=['Full', 'Diff'], ordered=True)

    results = results.groupby(['rule', 'transition', 'state_change', 'partial'])["accuracy"].mean()

    # Rename columns to be more readable
    results.index = results.index.set_names(['Rule', '', 'Change', 'State'])

    # Multiply accuracy by 100
    results = results * 100

    print()
    print(results.unstack(level=1).unstack(level=2).to_string())

    print()
    if args.latex:
        latex = results.unstack(level=1).unstack(level=2).to_latex(float_format="{:02.1f}".format)
        latex = latex.replace(r"\multicolumn{2}{r}", "\multicolumn{2}{c}")
        print(latex)

    # If running in a ipython notebook, you can use this to display the table
    results.unstack(level=1).unstack(level=2)
