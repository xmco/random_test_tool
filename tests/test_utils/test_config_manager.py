from unittest import TestCase

from random_test_tool import ArgumentParser
from utils.config_manager import get_conf_from_args, get_conf_from_file


class TestGetConf(TestCase):

    def test_get_conf_from_args_all_tests(self):
        """
        Test configuration object generation from command line arguments when all tests option is selected.
        """
        mock_args = ["-j", "8", "-o", "all", "-i", "mock_file.txt", '-s', ';']
        args = ArgumentParser().parse_args(mock_args)

        run_conf = get_conf_from_args(args)

        self.assertEqual(run_conf.separator, ";")
        self.assertEqual(run_conf.data_type, "int")
        self.assertEqual(run_conf.output, "all")
        self.assertEqual(len(run_conf.statistical_tests), 10)

    def test_get_conf_from_args_few_tests(self):
        """
        Test configuration object generation from command line arguments when specific tests are selected.
        """
        mock_args = ["-j", "8", "-o", "all", "-i", "mock_file.txt", '-s', ';', '-t', 'sign', 'serial']
        args = ArgumentParser().parse_args(mock_args)

        run_conf = get_conf_from_args(args)

        self.assertEqual(run_conf.separator, ";")
        self.assertEqual(run_conf.data_type, "int")
        self.assertEqual(run_conf.output, "all")
        self.assertEqual(len(run_conf.statistical_tests), 2)

    def test_get_conf_from_args_incorrect_test(self):
        """
        Test configuration object generation from command line arguments when specific tests are selected and an
        incorrect test name is given.
        """
        mock_args = ["-j", "8", "-o", "all", "-i", "mock_file.txt", '-s', ';', '-t', 'sign', 'foo']
        args = ArgumentParser().parse_args(mock_args)

        run_conf = get_conf_from_args(args)

        self.assertEqual(run_conf.separator, ";")
        self.assertEqual(run_conf.data_type, "int")
        self.assertEqual(run_conf.output, "all")
        self.assertEqual(len(run_conf.statistical_tests), 1)

    def test_conf_from_file(self):
        """
        Test configuration object generation from configuration file.
        """
        run_conf = get_conf_from_file("../test_data/base_run_config.yaml")
        self.assertEqual(run_conf.separator, "\\n")
        self.assertEqual(run_conf.data_type, "bits")
        self.assertEqual(run_conf.output, "terminal")
        self.assertEqual(len(run_conf.statistical_tests), 10)

    def test_conf_no_file(self):
        """
        Test configuration object generation from configuration file.
        """
        with self.assertRaises(FileNotFoundError):
            run_conf = get_conf_from_file("../test_data/toto.yaml")
