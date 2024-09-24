"""
Some utility function for unit tests.
"""
import random


def generate_unbalanced_sequence(length, proportion):
    """
    Generate a sequence with a higher proportion of 0.
    Proportion: number between 0 and 1.
    """
    if proportion <= 0 or proportion >= 1:
        raise ValueError("Proportion must be in ]0;1[")
    output = ""
    for i in range(length):
        rand = random.random()
        if rand <= proportion:
            output += "0"
        else:
            output += "1"

    return output


def generate_periodic_sequence(length, period):
    """
    Generate a non-random periodic sequence  of length L with period P.
    A sequence of length P is randomly generated then is repeated as many times as necessary to fill the output sequence.
    """
    pattern = ""
    for i in range(period):
        rand = random.random()
        if rand <= 0.5:
            pattern += "0"
        else:
            pattern += "1"
    output = ""
    while len(output) < length:
        output += pattern
    return output[:length]
