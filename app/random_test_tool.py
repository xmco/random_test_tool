"""
Copyright 2024 XMCO

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the “Software”), to deal in the Software without restriction, including without limitation the
rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit
persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the
Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import argparse
import logging
import multiprocessing
import os
import sys
import time

from tqdm import tqdm

from random_sample_tester.generate_reports import generate_report
from statistical_tests.statistical_test import TestRegistry
from statistical_tests.statistical_tests import load_tests
from random_sample_tester.random_sample_tester import RandomSampleTester
from utils.config_manager import get_conf_from_file, get_conf_from_args, generate_run_inputs
from utils.exceptions import RTTException

load_tests()


class ArgumentParser(argparse.ArgumentParser):
    """
    Class used to parse and save input options.
    """

    def __init__(self):
        super(ArgumentParser, self).__init__(description="Script testing the randomness of a serie of integer"
                                                         "or bits via statistical statistical_tests.")
        self.conf = argparse.Namespace()
        self._add_input_opts()

    def error(self, message):
        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        sys.exit(2)

    @staticmethod
    def check_positive(value):
        ivalue = int(value)
        if ivalue <= 0:
            raise argparse.ArgumentTypeError("%s is an invalid positive int value" % value)
        return ivalue

    def _add_input_opts(self):
        """
        Private method used to configure options.
        """
        self.add_argument("-i", "--input_files", dest="input_files", type=str, nargs="+",
                          help="List of files to test.")
        self.add_argument("-d", "--input_dir", dest="input_dir", type=str,
                          help="Input directory, statistical_tests will be launched on each file.")
        self.add_argument("-o", "--output", dest="output", type=str, default='terminal',
                          choices=["terminal", "csv", "graph", "html", "all"],
                          help="Output report options.")
        self.add_argument("-O", "--output_dir", dest="output_dir", type=str, default='.',
                          help="Output directory.")
        self.add_argument("-j", "--n_cores", dest="n_cores", type=int, default=1, choices=range(1, 32),
                          help="Number of processes used, 1 by default, maximum 31")
        self.add_argument("-t", "--test", dest="statistical_tests", default="all", nargs="*",
                          help="Specifies which statistical_tests to launch. By default all statistical_tests are "
                               "launched.")
        self.add_argument("-dt", "--data_type", dest="data_type", type=str, default="int", choices=["int", "bits",
                                                                                                    "bytes"],
                          help="Used to select data type of sample, by default integer (int)")

        self.add_argument("-s", "--separator", dest="separator", type=str, default="\\n",
                          choices=["\\n", " ", ",", ";"],
                          help="Separator used for integer files.")
        self.add_argument("-ll", "--log_level", dest="log_level", default='INFO', type=str,
                          choices=['ALL', 'DEBUG', 'INFO', 'WARN', 'ERROR', 'FATAL', 'OFF', 'TRACE'],
                          help="Log level (default: INFO).")
        self.add_argument("-c", "--config", dest="config", type=str, help="Configuration file of the run, if used will "
                                                                          "override other options.")
        self.add_argument("-C", "--chunks", dest="chunks", type=self.check_positive,
                          help="If this option is given, the inputs will be merged and splited into n chunks then "
                               "processed independently.")

    def parse_options(self):
        """
        Parse input arguments from command line.
        """
        self.conf = self.parse_args()


def run_random_test_tool(run_conf, data, progress_queue):
    """
    Run the tool on a file.
    """
    rst = RandomSampleTester()
    rst.get_data(data, run_conf.data_type, run_conf.separator, run_conf.chunks)
    rst.register_tests_for_run(run_conf.statistical_tests)
    rst.run_tests(progress_queue)
    return rst.test_results


def identity(string):
    """
    Function used for compatibility between argparse and multiprocessing.
    """
    return string


def print_run_summary(n_files, args):
    """
    Print a run summary in the terminal before launch.
    """
    test_dic = TestRegistry.get_available_tests()
    if args.conf.statistical_tests == "all":
        tests = test_dic.keys()
    else:
        tests = []
        for test_name in args.conf.statistical_tests:
            if test_name in list(test_dic.keys()):
                tests.append(test_name)

    print("\n")
    print(f"Launching tests on {n_files} batches...\n")
    print("Tests launched:")
    for test_name in tests:
        print(f"- {test_name}")
    print("\n")

    return n_files * len(tests)


def listener(q, total_n_tests):
    """
    Function used to track progress.
    """
    pbar = tqdm(total=total_n_tests)
    while True:
        item = q.get()
        if item is None:
            break
        else:
            pbar.update()


def run_rtt():
    """
    Main function for RTT.
    """
    args = ArgumentParser()
    args.register('type', None, identity)
    args.parse_options()

    exec_start = time.time()

    # Input preparation
    logging.basicConfig(level=args.conf.log_level)

    # Setup of queue for process tracking
    manager = multiprocessing.Manager()
    progress_queue = manager.Queue()

    # Generate run configuration
    if args.conf.config:
        run_conf = get_conf_from_file(args.conf.config)
    else:
        run_conf = get_conf_from_args(args.conf)

    # Test if output directory exists
    if not os.path.exists(run_conf.output_dir):
        raise RTTException(f'Output dir "{run_conf.output_dir}" does not exists.')

    # Generate inputs from configuration
    inputs = generate_run_inputs(run_conf, args, progress_queue)

    # Run summary
    total_n_tests = print_run_summary(len(inputs), args)

    # Run statistical_tests in parallel
    pool = multiprocessing.Pool(processes=run_conf.n_cores + 1)
    try:
        # This try/except block makes sure we close correctly the threading pool in cas of an exception
        pool.apply_async(listener, (progress_queue, total_n_tests))
        results = pool.starmap(run_random_test_tool, inputs)
        progress_queue.put(None)
    except RTTException:
        pool.terminate()
        pool.join()
        raise
    pool.close()
    pool.join()

    exec_stop = time.time()

    execution_datas = {
        "exec_time": exec_stop - exec_start,
        "processed_files": run_conf.input_files if run_conf.input_files else [f"{run_conf.input_dir}/{file}" for file in
                                                                              os.listdir(run_conf.input_dir)]
    }

    # Output report generation
    generate_report(run_conf.output_dir, results, run_conf.output, execution_datas)

def main():
    try:
        run_rtt()
    except RTTException as e:
        # here we catch RRTExceptions, print their messages as error and qui the program properly
        logging.error(f"Execution failed, stopping execution: {str(e)}")
