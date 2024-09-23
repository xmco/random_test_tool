import logging
import math
import os
import sys
import numpy as np
import yaml

from yaml import safe_load
from dataclasses import dataclass

from yaml.parser import ParserError

from random_sample_tester.random_sample_tester import RandomSample, DataSample
from statistical_tests.statistical_test import TestRegistry, StatisticalTest
from utils.data_type import DataType
from utils.exceptions import RTTException


@dataclass
class TestConfiguration:
    """
    Class used to store configuration for a specific test
    """
    display_name: str
    test_name: str
    test_class: StatisticalTest
    params: dict  # Dictionary containing parameters override


@dataclass
class RunConfiguration:
    """
    Class used to store run configuration information.
    """
    statistical_tests: list  # List of TestConfiguration objects
    output: str
    data_type: str
    separator: str
    input_files: list = None
    input_dir: str = None
    chunks: int = None
    n_cores: int = 1
    output_dir: str = "."


def _validate_test(test_name, data_type):
    if TestRegistry.get_test(test_name):
        test_class, test_data_type = TestRegistry.get_test(test_name)
    else:
        return None
    if DataType.get_data_type(data_type) in test_data_type:
        logging.info(f"Adding {test_name} to the run.")
        return test_class
    return None


def get_conf_from_args(args):
    """
    Create a RunConfiguration object from options given by command line.
    :param args: ArgumentParser object
    :return: RunConfiguration object
    """
    statistical_tests = []
    test_list = TestRegistry.get_available_tests().keys() if args.statistical_tests == "all" else args.statistical_tests
    for test_name in test_list:
        test_class = _validate_test(test_name, args.data_type)
        if test_class:
            statistical_tests.append(TestConfiguration(test_name, test_name, test_class, {}))

    return RunConfiguration(statistical_tests,
                            args.output,
                            args.data_type,
                            args.separator,
                            args.input_files,
                            args.input_dir,
                            args.chunks,
                            args.n_cores,
                            args.output_dir)


def get_conf_from_file(file_path):
    """
    Create a RunConfiguration object from a yaml config file
    :param file_path: path to yaml file
    :return: RunConfiguration object
    """
    if not os.path.exists(file_path):
        raise RTTException(f"The {file_path} file given as configuration does not exist.")
    with open(file_path, 'r') as file:
        try:
            conf = safe_load(file)
        except ParserError:
            raise RTTException(f"Impossible to parse file '{file_path}'. it must be a valid yaml file.")

    try:
        test_plan = conf["test_plan"]
    except KeyError:
        raise RTTException("No test plan defined")
    except ValueError:
        raise RTTException("No test defined in test_plan")

    statistical_tests = []
    for name, test_conf in test_plan.items():
        test_class = _validate_test(test_conf["test_name"], conf.get("data_type", "int"))
        if test_class:
            statistical_tests.append(TestConfiguration(test_conf["display_name"], test_conf["test_name"], test_class,
                                                       test_conf.get("params", {})))

    return RunConfiguration(statistical_tests,
                            conf.get("output", "terminal"),
                            conf.get("data_type", "int"),
                            conf.get("separator", "\\n"),
                            conf.get("input_files", None),
                            conf.get("input_dir", None),
                            conf.get("chunks", None),
                            conf.get("n_cores", 1),
                            conf.get("output_dir", "."))


def get_chunks_from_files(files, run_conf):
    """
    From a list of path files, load the files a separate the data in n chunks.
    """
    rs = RandomSample()
    data_list = []

    for file in files:
        rs.get_data(file, run_conf.data_type, run_conf.separator, None)
        data_list += rs.data.data

    chunk_size = math.floor(len(data_list) / run_conf.chunks)
    chunks = []
    for i in range(0, len(data_list[:chunk_size*run_conf.chunks]), chunk_size):
        data = ''.join(data_list[i:i + chunk_size]) if rs.data.data_type == DataType.BITSTRING else data_list[i:i + chunk_size]
        chunks.append(DataSample(data, rs.data.data_type))

    return chunks


def generate_run_inputs(run_conf, args, progress_queue):
    """
    Generate proper run inputs from configuration
    """
    inputs = []
    if run_conf.input_files is None and run_conf.input_dir is None:
        logging.error("Error: No input file provided")
        args.print_help()
        sys.exit(2)
    if run_conf.input_files is not None:
        if run_conf.chunks:
            inputs = [(run_conf, data, progress_queue) for data in get_chunks_from_files(run_conf.input_files, run_conf)]
        else:
            inputs = [(run_conf, file, progress_queue) for file in run_conf.input_files]
        return inputs
    if run_conf.input_dir is not None:
        try:
            if run_conf.chunks:
                files = [f"{run_conf.input_dir}/{file}" for file in os.listdir(run_conf.input_dir)]
                inputs = [(run_conf, data, progress_queue) for data in get_chunks_from_files(files, run_conf)]
            else:
                inputs = [(run_conf, f"{run_conf.input_dir}/{file}", progress_queue) for file in os.listdir(run_conf.input_dir)]
        except FileNotFoundError:
            raise RTTException(f"Input directory '{run_conf.input_dir}' not found.")
    return inputs
