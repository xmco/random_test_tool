import logging
from enum import Enum


class DataType(Enum):
    """
    Class implementing the different data types supported in the statistical_tests.
    """
    INT = 1
    BITSTRING = 2
    BYTES = 3
    FLOAT = 4  # not implemented

    @classmethod
    def get_data_type(cls, data_code):
        """
        Compute the input data type.
        :param data_code: string code given in input
        :return: type
        """
        # test if data is a bitstring
        if data_code == "int":
            return DataType.INT
        if data_code == "bits":
            return DataType.BITSTRING
        if data_code == "bytes":
            return DataType.BYTES

        # Unknown code
        logging.error("Unkown data type.")
        raise ValueError
