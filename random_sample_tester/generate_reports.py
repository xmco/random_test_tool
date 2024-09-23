"""
Module containing output generation functions.
"""
import itertools
import logging
import math
import os
import time

import pandas as pd
import plotly.express as px
from scipy.stats import binomtest
from tabulate import tabulate
from jinja2 import Environment, FileSystemLoader

from utils.exceptions import RTTException


def _generate_plots(df, dir_path, time_str):
    """
    Generate graphical representations of the output of the different statistical_tests.
    :param groups: data to plot
    """
    # Creating output directory for the graphs
    plot_path = os.path.join(dir_path, f"{time_str}-plots")
    if not os.path.exists(plot_path):
        os.mkdir(plot_path)

    fig = px.scatter(df, x="sample number", y="p_value", color='test_name', symbol='test_name')
    fig.update_traces(marker=dict(size=10))
    fig.add_hrect(y0=0.95, y1=1.0, line_width=0, fillcolor="red", opacity=0.1)
    fig.add_hrect(y0=0.0, y1=0.05, line_width=0, fillcolor="red", opacity=0.1)
    fig.write_html(os.path.join(plot_path, f"{time_str}_scatter.html"))

    fig_2 = px.box(df, x='test_name', y='p_value')
    fig_2.add_hrect(y0=0.95, y1=1.0, line_width=0, fillcolor="red", opacity=0.1)
    fig_2.add_hrect(y0=0.0, y1=0.05, line_width=0, fillcolor="red", opacity=0.1)
    fig.write_html(os.path.join(plot_path, f"{time_str}_boxplot.html"))

    return fig, fig_2


def _create_pandas_objects(outputs):
    for i, chunk_output in enumerate(outputs):
        for test_result in chunk_output:
            test_result["sample number"] = str(i + 1)
    df = pd.DataFrame(list(itertools.chain.from_iterable(outputs)))
    groups = df.groupby("test_name")
    return df, groups


def _write_csv(outputs, output_dir, time_str):
    """
    Write a csv report of the tests.
    """
    df_formatted = pd.DataFrame(outputs).stack().apply(pd.Series)
    df_formatted.to_csv(f"{output_dir}/{time_str}-statistical_results.csv", index=False)


def _get_confidence_interval(p_value, n_samples):
    if p_value * n_samples < 5:
        # Sample too small to compute confidence interval
        return None
    interval = binomtest(math.floor(p_value * n_samples * 2), n_samples, p=p_value, alternative='two-sided'). \
        proportion_ci(confidence_level=0.95)
    return interval


def _generate_run_summary(groups):
    """
    Generate a summary of the run as a list of dictionaries
    """
    summary = []
    for name, group in groups:
        summary_for_test = {"test_name": name}
        n_values = group["status"].count()
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

        # Add KO interval
        interval = _get_confidence_interval(group["p_value_limits"].iloc[0][0], n_values)
        if interval is None:
            summary_for_test["KO_interval"] = "Sample too Small"
        else:
            summary_for_test["KO_interval"] = [math.floor(interval.low * n_values),
                                               math.floor(interval.high * n_values)]

        # Add SUSPECT Interval
        interval = _get_confidence_interval(group["p_value_limits"].iloc[0][1], n_values)
        if interval is None:
            summary_for_test["SUSPECT_interval"] = "Sample too Small"
        else:
            summary_for_test["SUSPECT_interval"] = [math.floor(interval.low * n_values),
                                                    math.floor(interval.high * n_values)]

        # Add colors
        # BY default we use p_value * n_values or confidence interval
        result_class = "ok"
        if summary_for_test["SUSPECT_interval"] != "Sample too Small":
            if summary_for_test["SUSPECT_count"] < summary_for_test["SUSPECT_interval"][0] or \
                    summary_for_test["SUSPECT_count"] > summary_for_test["SUSPECT_interval"][1]:
                result_class = "suspect"
        else:
            if summary_for_test["SUSPECT_count"] > group["p_value_limits"].iloc[0][1] * n_values * 3:
                result_class = "suspect"
        if summary_for_test["KO_interval"] != "Sample too Small":
            if summary_for_test["KO_count"] < summary_for_test["KO_interval"][0] or \
                    summary_for_test["KO_count"] > summary_for_test["KO_interval"][1]:
                result_class = "ko"
        else:
            if summary_for_test["KO_count"] > group["p_value_limits"].iloc[0][1] * n_values * 3:
                result_class = "ko"
        summary_for_test["result_class"] = result_class

        summary.append(summary_for_test)
    return summary


def _write_terminal(outputs, summary):
    for test_result in outputs:
        # We had the results for each individual file
        table = tabulate(test_result, tablefmt='fancy_grid', headers="keys")
        print(table)
    # We add an additional run summary table
    print(tabulate([{k: v for k, v in d.items() if k != 'result_class'} for d in summary],
                   tablefmt='fancy_grid', headers="keys"))


def _write_html_report(outputs, summary, execution_data, output_dir, time_str, scatter_plot, box_plot):
    """
    Write a html report summarizing the run.
    """
    report_path = os.path.join(output_dir, f"{time_str}_report.html")
    environment = Environment(loader=FileSystemLoader("templates/"))
    report_template = environment.get_template("report.html")

    template_info = {
        "outputs": outputs,
        "ScatterPlot": scatter_plot.to_html(full_html=False),
        "BoxPlot": box_plot.to_html(full_html=False),
        "summary": summary,
        "exec_time": execution_data["exec_time"],
        "processed_files": sorted(execution_data["processed_files"])
    }

    with open(report_path, mode="w", encoding="utf-8") as report:
        report.write(report_template.render(template_info))


def generate_report(out_dir, outputs, mode, execution_data):
    """
    Takes the outputs from different runs and generates an output report.
    :param out_dir: Output directory.
    :param execution_data: Summary of relevant executuion information
    :param outputs: list of dictionaries
    :param mode: terminal/file/graph or all output mode
    """
    time_str = time.strftime("%Y-%m-%d-%H-%M-%S")
    output_dir = os.path.join(out_dir, f"rtt-{time_str}")
    terminal = (mode == "terminal" or mode == "all")
    graph = (mode == "graph" or mode == "all")
    csv = (mode == "csv" or mode == "all")
    html = (mode == "html" or mode == "all")

    # Generating output_directory
    try:
        os.mkdir(output_dir)
    except OSError:
        raise RTTException(f"Incorrect output directory: {output_dir}.")

    # Create the pandas objects
    try:
        df, groups = _create_pandas_objects(outputs)
    except KeyError:
        # Could happen if no valid test is provided
        raise RTTException("No valid test name provided.")

    # Generate run summary
    summary = _generate_run_summary(groups)

    if csv:
        _write_csv(outputs, output_dir, time_str)

    if terminal:
        _write_terminal(outputs, summary)

    if graph:
        _generate_plots(df, output_dir, time_str)

    if html:
        scatter_plot, box_plot = _generate_plots(df, output_dir, time_str)
        _write_html_report(outputs, summary, execution_data, output_dir, time_str, scatter_plot, box_plot)
