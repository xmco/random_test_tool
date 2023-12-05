"""
Module containing output generation functions.
"""
import itertools
import os
import time

import pandas as pd
from matplotlib import pyplot as plt
from tabulate import tabulate


def _generate_plots(group, group_name, dir_path, time_str):
    """
    Generate graphical representations of the output of the different statistical_tests.
    :param group: data to plot
    :param group_name: test name
    """
    plot_path = os.path.join(dir_path, f"{time_str}-plots")
    if not os.path.exists(plot_path):
        os.mkdir(plot_path)
    y = group["p_value"].to_numpy()
    x = range(1, len(y) + 1)
    # Scatter plot
    plt.plot(x, y, marker='.', linestyle='none')
    plt.xlabel("Sample nuber")
    plt.ylabel("P-value")
    plt.title(f"Test: {group_name}")
    plt.savefig(os.path.join(plot_path, f"{time_str}-{group_name.replace(' ', '_')}_scatter.png"))
    plt.clf()
    plt.boxplot(y)
    plt.title(f"Test: {group_name}")
    plt.ylabel("P-value")
    plt.savefig(os.path.join(plot_path, f"{time_str}-{group_name.replace(' ', '_')}_boxplot.png"))
    plt.clf()


def _generate_execution_summary(output_dir, time_str, test_summary, execution_data):
    with open(os.path.join(output_dir, f"{time_str}-summary.txt"), 'w') as file:
        file.write("RANDOM TEST TOOL REPORT SUMMARY\n\n")
        file.write(f"Execution Time: {execution_data['exec_time']}")
        file.write("\n\n")
        file.write("Processed files: \n")
        file.writelines([f"- {inputs[1]}\n" for inputs in execution_data["processed_files"]])
        file.write("\n\n")
        file.write("Tests summary: ")
        file.write("\n")
        file.write(tabulate(test_summary, tablefmt='fancy_grid', headers="keys"))


def generate_report(outputs, mode, execution_data):
    """
    Takes the outputs from different runs and generates an output report.
    :param execution_data: Summary of relevant executuion information
    :param outputs: list of dictionaries
    :param mode: terminal/file/graph or all output mode
    """
    time_str = time.strftime("%Y-%m-%d-%H-%M-%S")
    output_dir = f"rtt-{time_str}"
    terminal = (mode == "terminal" or mode == "all")
    graph = (mode == "graph" or mode == "all")
    file = (mode == "file" or mode == "all")

    # Generating output_directory
    os.mkdir(output_dir)

    if terminal:
        for test_result in outputs:
            table = tabulate(test_result, tablefmt='fancy_grid', headers="keys")
            print(table)

    if file or graph:
        df = pd.DataFrame(list(itertools.chain.from_iterable(outputs)))

        if file:
            df_formatted = pd.DataFrame(outputs).stack().apply(pd.Series)
            df_formatted.to_csv(f"{output_dir}/{time_str}-statistical_results.csv", index=False)

        groups = df.groupby("test_name")
        summary = []
        for name, group in groups:
            summary_for_test = {"test_name": name}
            if graph:
                _generate_plots(group, name, output_dir, time_str)
            try:
                summary_for_test["OK_count"] = group["status"].value_counts()["OK"]
            except KeyError:
                summary_for_test["OK_count"] = 0
            try:
                summary_for_test["SUSPECT_count"] = group["status"].value_counts()["SUSPECT"]
            except KeyError:
                summary_for_test["SUSPECT_count"] = 0
            try:
                summary_for_test["KO_count"] = group["status"].value_counts()["KO"]
            except KeyError:
                summary_for_test["KO_count"] = 0
            summary.append(summary_for_test)

        if terminal:
            # We add an additional summary table in this case
            print(tabulate(summary, tablefmt='fancy_grid', headers="keys"))

        # Generating execution summary
        _generate_execution_summary(output_dir, time_str, summary, execution_data)
