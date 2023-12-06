"""
Copyright 2023 XMCO

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

    def _add_input_opts(self):
        """
        Private method used to configure options.
        """
        self.add_argument("-i", "--input_files", dest="input_files", type=str, nargs="+",
                          help="List of files to test.")
        self.add_argument("-d", "--input_dir", dest="input_dir", type=str,
                          help="Input directory, statistical_tests will be launched on each file.")
        self.add_argument("-o", "--output", dest="output", type=str, default='terminal',
                          choices=["terminal", "file", "graph", "all"],
                          help="Output report options.")
        self.add_argument("-j", "--n_cores", dest="n_cores", type=int, default=1, choices=range(1, 32),
                          help="Number of processes used, 1 by default, maximum 31")
        self.add_argument("-t", "--test", dest="statistical_tests", default="all", nargs="*",
                          help="Specifies which statistical_tests to launch. By default all statistical_tests are "
                               "launched.")
        self.add_argument("-dt", "--data_type", dest="data_type", type=str, default="int", choices=["int", "bits",
                                                                                                    "bytes"],
                          help="Used to select data type of sample, by default integer (int)")

        self.add_argument("-s", "--separator", dest="separator", type=str, default="\\n", choices=["\\n", " ", ",", ";"],
                          help="Separator used for integer files.")
        self.add_argument("-ll", "--log_level", dest="log_level", default='INFO', type=str,
                          choices=['ALL', 'DEBUG', 'INFO', 'WARN', 'ERROR', 'FATAL', 'OFF', 'TRACE'],
                          help="Log level (default: INFO).")

    def parse_options(self):
        """
        Parse input arguments from command line.
        """
        self.conf = self.parse_args()


def run_random_test_tool(tool_args, files, progress_queue):
    """
    Run the tool on a file.
    """
    rst = RandomSampleTester()
    rst.get_data(files, tool_args.conf.data_type, tool_args.conf.separator)
    rst.register_tests_for_run(tool_args.conf.statistical_tests)
    rst.run_tests(progress_queue)
    return rst.test_results


def identity(string):
    """
    Function used for compatibility between argparse and multiprocessing.
    """
    return string


def print_run_summary(n_files):
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
    print(f"Launching tests on {n_files} file...\n")
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


if __name__ == '__main__':
    args = ArgumentParser()
    args.register('type', None, identity)
    args.parse_options()

    exec_start = time.time()

    # Input preparation
    logging.basicConfig(level=args.conf.log_level)

    # Setup of queue for process tracking
    manager = multiprocessing.Manager()
    progress_queue = manager.Queue()

    if args.conf.input_files is None and args.conf.input_dir is None:
        logging.error("Error: No input file provided")
        args.print_help()
        sys.exit(2)
    if args.conf.input_files is not None:
        inputs = [(args, file, progress_queue) for file in args.conf.input_files]
    if args.conf.input_dir is not None:
        inputs = [(args, f"{args.conf.input_dir}/{file}", progress_queue) for file in os.listdir(args.conf.input_dir)]

    # Run summary
    total_n_tests = print_run_summary(len(inputs))

    # Run statistical_tests in parallel
    pool = multiprocessing.Pool(processes=args.conf.n_cores + 1)
    pool.apply_async(listener, (progress_queue, total_n_tests))
    results = pool.starmap(run_random_test_tool, inputs)
    progress_queue.put(None)
    pool.close()
    pool.join()

    exec_stop = time.time()

    execution_datas = {
        "exec_time": exec_stop-exec_start,
        "processed_files": inputs
    }

    # Output report generation
    generate_report(results, args.conf.output, execution_datas)
