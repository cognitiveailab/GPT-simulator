import pandas as pd
import plotly.express as px

import argparse

def parse_args():
    parser = argparse.ArgumentParser(description="Generate histograms for the paper")
    parser.add_argument("--full", help="Results CSV file for predicting the full pipeline (i.e., --data_type full).")
    parser.add_argument("--tick", help="Results CSV file for predicting tick state (i.e., --data_type tick).")
    parser.add_argument("--action", help="Results CSV file for predicting action state (i.e., --data_type action).")
    parser.add_argument("--output", help="Name of output PDF.")
    args = parser.parse_args()
    return args


def load_data(args):
    print(f"Processing {args.output}")

    df_full = pd.read_csv(args.full)
    df_tick = pd.read_csv(args.tick)
    df_action = pd.read_csv(args.action)

    # Merge the three dataframes and add a new column to differentiate them.
    df_tick["transition_type"] = "tick"
    df_action["transition_type"] = "action"
    df_full["transition_type"] = "full"
    df = pd.concat([df_full, df_tick, df_action]).reset_index()
    return df


def gen_histograms(df, output_path):
    print(f"Number of rows: {len(df)}")


    # Add a new values to prop column when is_modified is True/False and gold_prop is True/False
    df["is_modified"] = df["is_modified"].replace("na", '0')
    df.loc[(df["prop"] == '0') & (df['is_modified'] == '1') & (df['gold_prop'] == '1'), 'prop'] = '4'
    df.loc[(df["prop"] == '0') & (df['is_modified'] == '1') & (df['gold_prop'] == '0'), 'prop'] = '5'
    df.loc[(df["prop"] == '0') & (df['is_modified'] == '0') & (df['gold_prop'] == '1'), 'prop'] = '6'

    prop = {'0': "incorrect", '1': "correct value", '2': "missing property", '3': "incorrect property", '4': "incorrect value", '5': "incorrect change", '6': "unaltered value", "na": "na"}
    #PROP_COLORS = {'0': "#EF553B", '1': h"#00cc96", '2': "#636efa", '3': "#ab63fa", '4': "#ff7700", '5': "#ff0077", '6': "#770077", 'na': "#000000"}
    PROP_COLORS = {'0': "#EF553B", '1': "#00cc96", '2': "#C7C6C6", '3': "#ab63fa", '4': "#EF553B", '5': "#ff7700", '6': "#FACCCC", 'na': "#000000"}
    #PROP_COLORS = {'0': "#EF553B", '1': "#7AC944", '2': "#C7C6C6", '3': "#ab63fa", '4': "#FF1D25", '5': "#ED878B", '6': "#CCCCCC", 'na': "#000000"}
    #STATE_CHANGE_FACET_TITLES = {0: "Unchanged States", 1: "Changed States"} #{0: "No transitions", 1: "Transitions"}
    TRANSITION_TYPE_FACET_TITLES = {'tick': r"$\small\mathcal{F}_\text{env}$", 'action': r"$\small\mathcal{F}_\text{act}$", 'full': r"$\small\mathcal{F}$"} #{0: "No transitions", 1: "Transitions"}
    # Use latex font in plot for tick Facet \mathcal{F}


    # Plot histogram of prop grouped per property
    prop_per_property = df.groupby(["game", "state_id", "action", "name", "prop_key" ,"transition_type"])
    prop_per_property = prop_per_property.first().reset_index()

    # Plot histogram of prop grouped per action (only for the dynamic case, i.e. gold_prop == 1)
    data = prop_per_property[(prop_per_property.prop != "na") & (prop_per_property.gold_prop != "na") & (prop_per_property.gold_prop == '1')]  # Dynamic case
    PROPERTIES = sorted(data.prop_key[df.prop != "na"].unique())
    print(len(PROPERTIES))

    # data = prop_per_property[(prop_per_property.gold_prop == '1')]
    # fig3 = px.histogram(prop_per_property[(prop_per_property.prop != "na") & (prop_per_property.gold_prop != "na")], x="prop_key", color="prop", facet_row="gold_prop", barnorm="percent")

    # fig3 = px.histogram(data, x="prop_key", color="prop", barnorm="percent", histnorm="percent")

    #fig3 = px.histogram(data, x="prop_key", color="prop", facet_row="datatype", facet_col="gold_prop", barnorm="percent")
    fig3 = px.histogram(data, x="prop_key", color="prop", facet_row="transition_type", barnorm="percent",
                        category_orders={"transition_type": ["full", "action", "tick"]},
                        facet_row_spacing=0.07,)

    fig3.update_layout(xaxis_title="", yaxis_title="") #fig3.update_layout(xaxis_title="Property", yaxis_title="Proportion")
    fig3.update_yaxes(title="") #fig3.update_yaxes(title="Proportion")
    fig3.for_each_trace(lambda t: t.update(name=prop[t.name], marker={'color':PROP_COLORS[t.legendgroup]}))
    fig3.update_xaxes(categoryorder="array", categoryarray=PROPERTIES)
    # fig3.update_xaxes(showgrid=True, ticks="outside")
    fig3.update_xaxes(tickangle=45, tickfont=dict(size=9))
    for i in range(len(fig3.layout.annotations)):
        fig3.layout.annotations[i]["text"] = TRANSITION_TYPE_FACET_TITLES[fig3.layout.annotations[i]["text"].split("=")[1]]
    # fig3.layout.annotations[i]["text"] = STATE_CHANGE_FACET_TITLES[int(fig3.layout.annotations[i]["text"].split("=")[1])]


    # Sort traces by name
    fig3.data = sorted(fig3.data, key=lambda x: x.name)
    fig3.data = fig3.data[:-2] + (fig3.data[-1], fig3.data[-2])

    fig3.update_layout(legend=dict(
    orientation="h",
    entrywidth=96,
    yanchor="bottom",
    y=1.02,
    xanchor="left",
    x=0,
    title=""
    ))

    # Use 16:9 aspect ratio
    fig3.update_layout(
        autosize=False,
        width=800,
        height=320,
    )

    # Tight layout
    fig3.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor="white",
    )

    fig3.show()
    # Save plots as svg
    fig3.write_image(output_path, width=800, height=320)
    print(f"  {output_path}")
    #fig3.write_image(f"./images2/{results_name}_hist_property.pdf", width=800, height=320)
    #print(f"  ./images2/{results_name}_hist_property_state_changed.pdf")



# #models = ["gpt-3.5-turbo-0125", "gpt-4-0125-preview", ]
# models = ["gpt-4o"]
# # date = "apr24"
# date = "jun10"
# #output_types = ["diff", "full"] # partial state / full state
# output_types = ["diff"] # partial state / full state
# #rules = ["hwr", "lwr", "no_rule"] # human rules / llm rules / no rules
# rules = ["hwr"]
# # exp = ["action", "tick"] # action changes / tick changes

# # Dummy to avoid weird MathJax error
# first_generation = True

# for model in models:
#     for output_type in output_types:
#         for rule in rules:

#             results_name = f"{model}_{date}_{output_type}_{rule}_action-tick-full"
#             df = load_data(model, date, output_type, rule)
#             gen_histograms(df, results_name)

#             if first_generation:
#                 # Dummy to overwrite the image with the weird MathJax error
#                 first_generation = False
#                 gen_histograms(df, results_name)

if __name__ == "__main__":
    args = parse_args()
    df = load_data(args)
    if not args.output.endswith(".pdf"):
        args.output = args.output + ".pdf"

    gen_histograms(df, args.output)
