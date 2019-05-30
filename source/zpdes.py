from random import choices
from collections import defaultdict, deque
import logging

# TODO: Clarify substitution of problems with traces in the zpdes algorithm unlike in the paper.
# TODO: Clarify Correctness values.

logger = logging.getLogger(f"zpd.{__name__}")
logger.setLevel(logging.DEBUG)

 # A class for object made by collecting properties or values
 # specific to each element in the ZPD as per the ZPDES algorithm.
class ZPDES_Node(object):
    """
    Class for objects corresponding to the nodes in the ZPDES algorithm given
    in the paper.
    """
    
    def __init__(self, weight, queue_limit):
        self.weight = weight
        self.queue_size = 0
        self.queue_limit = queue_limit
        self.correctness_record = deque()

    def record_correctness(self, correctness):
        if self.queue_size < self.queue_limit:
            self.queue_size += 1
        else:
            self.correctness_record.pop()
        
        self.correctness_record.appendleft(correctness)
    
    def __repr__(self):
        return f"ZPDES_Node(w0={self.weight}, queue_limit={self.queue_limit})"
    
    def __str__(self):
        return (f"ZPDES_Node(weight: {self.weight}, queue_size:"
                f"{self.queue_size}, queue_limit: {self.queue_limit}, "
                f"correctness_record: {self.correctness_record})")


def calculate_reward(node):
    """
    Function that calculates the possible reward for picking the trace
    corresponding to the given node.
    
    Parameter(s):
        node: ZPDES_Node

    Returns:
        reward: float
    """

    i = 0
    half = node.queue_limit / 2
    # Sum of first half of the stored results.
    latest_sum = 0
    # SUm of second half or older half of the stored results.
    earliest_sum = 0
    for correctness in node.correctness_record:
        if i < half:
            latest_sum += correctness
        else:
            earliest_sum += correctness
        i += 1

    reward = ((latest_sum / half) + (earliest_sum / half))

    return reward


def get_probabilities(trace_node_dict, gamma):
    """
    Function that returns the probabilities with which each trace in the given
    trace node dictionary should be chosen with respect to the gamma parameter.

    Parameter(s):
        trace_node_dict: dict(string -> ZPDES_Node)
        gamma: float
    
    Returns:
        trace_probability_dict: dict(string -> float)
    """
    sum_weights = 0
    for trace, node in trace_node_dict.items():
        sum_weights += node.weight
    
    trace_probability_dict = {}
    for trace, node in trace_node_dict.items():
        prob = (node.weight / sum_weights) * (1 - gamma) +  gamma / len(trace_node_dict)
        trace_probability_dict[trace] = prob

    return trace_probability_dict

def is_correct(problem, answer):
    """
    Helper function that returns correctness of answer for the given problem.
    """
    return problem[2] == answer

def zpdes(init_zpd,
          trace_problems_dict,
          progression_graph,
          beta,
          eta,
          h,
          d,
          gamma,
          w0,
          student):
    """
    Function that runs the ZPDES algorithm on the given student according to the
    given parameters.
    
    Parameter(s):
        init_zpd: set(string)
        trace_problems_dict: dict(string -> list(tuple(int, int, int, string)))
        progression_graph: dict(string -> list(string))
        beta: float
        eta: float
        h: int
        d: int
        gamma: float
        w0: float
        student: Student
    
    Returns:
        None
    """
    problem_count = 0

    # A map from traces to iterators of the corresponding problem list. 
    trace_problemsIter_dict = {}
    for trace, problems in trace_problems_dict.items():
        trace_problemsIter_dict[trace] = iter(problems)

    # A map from all traces in ZPD to a corresponding ZPDES_node object.
    zpdes_trace_node_dict = {}
    for trace in init_zpd:
        zpdes_trace_node_dict[trace] = ZPDES_Node(w0, d)

    log = f"ZPDES nodes generated."
    for trace, node in zpdes_trace_node_dict.items():
        log += f"\n{trace} -> NODE: {node}"
    logger.info(log)

    while len(zpdes_trace_node_dict) > 0:
        # print(len(zpdes_trace_node_dict))
        trace_probability_dict = get_probabilities(zpdes_trace_node_dict, gamma)
        traces, probabilities = zip(*trace_probability_dict.items())
        [chosen_trace] = choices(traces, weights=probabilities)
        
        log = f"Generated trace probabilities."
        for t, p in trace_probability_dict.items():
            log += f"\ntrace: {t}; p:{p}"
        logger.info(log)

        # Select a problem from the problem list of the chosen_trace consecutively
        # and loop around the list when exhausted. 
        try:
            problem = next(trace_problemsIter_dict[chosen_trace])
        except StopIteration:
            trace_problemsIter_dict[chosen_trace] = iter(trace_problems_dict[chosen_trace])
            problem = next(trace_problemsIter_dict[chosen_trace])
        
        answer = student.solve(problem)
        problem_count += 1
        correctness = is_correct(problem, answer)
        chosen_node = zpdes_trace_node_dict[chosen_trace]
        chosen_node.record_correctness(correctness)
        
        log = (f"chosen trace: {chosen_trace}, problem: {problem}"
               f", answer:{answer}, Is correct: {correctness}")
        logger.info(log)

        reward = calculate_reward(chosen_node)
        chosen_node.weight = (beta * chosen_node.weight + eta * reward)
        accuracy = sum(chosen_node.correctness_record) / chosen_node.queue_limit
        if accuracy >= h:
            # Update ZPD.
            for t in progression_graph[chosen_trace]:
                if t not in zpdes_trace_node_dict: # Probably not needed.
                    zpdes_trace_node_dict[t] = ZPDES_Node(w0, d)
            
            del zpdes_trace_node_dict[chosen_trace]
            # del trace_problemIters_dict[chosen_trace]
        
        log  = f"Updated trace node dictionary."
        for trace, node in zpdes_trace_node_dict.items():
            log += f"\n{trace} -> NODE: {node}"
        logger.info(log)
    
    logger.info(f"Number of problems asked: {problem_count}")
    print(f"Zpdes: {problem_count}")

    return   