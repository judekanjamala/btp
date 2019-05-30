import csv
import math
import logging

import numpy as np

from hyperparameters import action_tag_dict

logger = logging.getLogger(f"zpd.{__name__}")
logger.setLevel(logging.DEBUG)


def length(n):
    """ 
    Function that takes an integer and returns the number of digits in it.

    Parameter(s):
        n: int

    Returns:
        n_digits: int
    """

    if n == 0:
        n_digits = 1
    else:
        n_digits = int(math.log10(n))+1

    return n_digits


def generate_2digitaddition_trace(op1, op2):
    """
    Function takes two integers and returns trace of their absolute value
    addtion.
    
    Parameter(s):
        op1: int
        op2: int
    
    Returns:
        trace: string
    """
    result = op1 + op2

    # Make the operands equal in length.
    n_digits = max(length(int(op1)), length(int(op2)))
    op1 = "{op:0{width}}".format(op=abs(int(op1)), width=n_digits)
    op2 = "{op:0{width}}".format(op=abs(int(op2)), width=n_digits)
    
    # Split the operands into single digit lists.
    op1 = [int(x) for x in op1]
    op2 = [int(x) for x in op2]  
    
    carry = 0
    trace = ""

    # Add digit by digit and tag appropriately.
    for i in range(n_digits - 1, -1, -1):
        if carry == 0:
            trace += action_tag_dict["One digit addition without carry."]
        else:
            trace += action_tag_dict["One digit addition with carry."]
        
        digits_sum = op1[i] + op2[i] + carry
        carry = digits_sum // 10
        
        if carry > 0:
            trace += action_tag_dict["Writing a carry."]
    
    if carry > 0:
        trace += action_tag_dict["Bringing down a carry."]
    
    return (result,  trace)


def generate_2digitaddition_traces(ndigit_n_dict, trace_file_path):
    """
    Function takes ndigit_n_dict, a map from the length of the integers
    and the number of integers/additions. It then computes traces for that many
    additions of two integers and writes them trace_file_path.
    
    Parameter(s):
        ndigit_n_dict: dict(int -> int)
        trace_file_path: string

    Returns:
        None
    """

    logger.info("Opening trace file for writing.")
    with open(trace_file_path, 'w') as trace_file:
        writer = csv.writer(trace_file)
        writer.writerow(['operand1', 'operand2', 'sum', 'trace'])
        for ndigit, n in ndigit_n_dict.items():
            int_range = (pow(10, ndigit - 1), pow(10, ndigit))
            if int_range[0] == 1:
                int_range = (0, int_range[1])
            
            # Generate ntraces random numbers for each length.
            ops_ndigit = np.random.randint(int_range[0],
                                           int_range[1],
                                           (n, 2))

            log = f"{n} addition pairs of {ndigit} digit(s) generated."
            logger.info(log)

            for op1, op2 in ops_ndigit:
                result, trace = generate_2digitaddition_trace(op1, op2)
                writer.writerow([op1, op2, result, trace])

            log = f"Finished generating traces for {ndigit} digit additions."
            logger.info(log)

    logger.info("Finished writing to trace file.")
    
    return