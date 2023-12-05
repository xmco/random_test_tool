import logging
from abc import ABC, abstractmethod
import math


class StatisticalTest(ABC):
    """
    Abstract class for statistical test implementing asbtract methods get_data_for_test, run_test and generate_report.
    """

    def __init__(self):
        self.data = None
        # Default values
        self.n_values = 0
        self.p_value_limit = 0.05
        self.p_value_limit_strict = 0.01
        self.test_output = None

    @abstractmethod
    def get_data_for_test(self, data_generator):
        """
        Take the data input and format it for the test. Data is stored in self.data.
        """
        raise NotImplementedError

    @abstractmethod
    def run_test(self):
        """
        Run the test on self.data.
        """
        raise NotImplementedError

    @abstractmethod
    def generate_report(self):
        """
        Summarize test results in a dictionnary.
        :return: (dict) test results.
        """
        raise NotImplementedError

    @staticmethod
    def highest_power_2(n):
        p = int(math.log(n, 2))
        return int(pow(2, p)), p

    def transform_to_bits(self):
        """
        Transform integer data into equally probable bitstring string. Biggest existing [1, 2^n] interval is taken from
        the data set and inetegers are stack in their binary form.
        """
        # If integer data does not start at 1, we shift the data.
        if min(self.data) == 0:
            self.data = list(map(lambda x: x + 1, self.data))

        max_value = max(self.data)

        max_power_number, exponent = self.highest_power_2(max_value)

        trimmed_integers = filter(lambda n: n <= max_power_number, self.data)
        big_string = ""

        for i in trimmed_integers:
            big_string += format(i - 1, "b").zfill(exponent)

        return big_string

    def generate_test_report(self, test_name):
        """
        Generic method used for generating test_report.
        :param test_name : test name.
        :return: Dictionary displaying test results.
        """
        cond_value = math.fabs(self.test_output - 1)
        if cond_value < self.p_value_limit:
            test_pass = "SUSPECT"
            if cond_value < self.p_value_limit_strict:
                test_pass = "KO"
        else:
            test_pass = "OK"
        report = {"test_name": test_name,
                  "n_sample": self.n_values,
                  "p_value": self.test_output,
                  "criterias": f"0 -KO- {self.p_value_limit_strict} -SUSPECT- {self.p_value_limit} -OK- "
                               f"{1- self.p_value_limit} -SUSPECT- {1-self.p_value_limit_strict} -KO- 1",
                  "status": test_pass}
        return report


class TestRegistry:
    """
    Class managing which statistical_tests are available.
    available_tests is a dictionary :
    available_tests[cls_name] : (test_class, data_type)
    """

    available_tests = {}

    @classmethod
    def register(cls, test_name, data_types):
        """
        Add a new test in the test registry.
        :param data_types: data types supported by the test
        :param test_name: test name
        :return: test class
        """

        def _register(test_cls):
            if not issubclass(test_cls, StatisticalTest):
                logging.error(f"Test {test_name} does not inherit from class StatisticalTest.")
                raise ValueError
            cls.available_tests[test_name] = (test_cls, data_types)
            return test_cls

        return _register

    @classmethod
    def get_available_tests(cls):
        return cls.available_tests
