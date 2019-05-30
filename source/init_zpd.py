from collections import defaultdict
from enum import Enum
from math import log
import logging

from compare_traces import atleast_complex

logger = logging.getLogger(f"zpd.{__name__}")
logger.setLevel(logging.DEBUG)

class Colour(Enum):
    UNCOLOURED = 0
    SOLVABLE = 1
    UNSOLVABLE = 2

class Visit(Enum):
    VISITED = 0
    UNVISITED = 1

class Node_initZPD():
    """
    Class for objects corresponding to the nodes in init_zpd algorithm
    described in the paper.
    """

    def __init__(self, c0):
        self.c = 0
        self.ic = 0
        self.colour = Colour.UNCOLOURED
        self.c0 = c0
        self.update_weight()
        # self.previous = 0

    def update_weight(self):
        arg = (self.c + self.c0) / (self.ic + 2 * self.c0)

        if arg <= 0 or arg >= 1:
            self.weight = 0
        else:
            self.weight = self.entropy(arg)

    def update_correctness(self, correct):
        if correct:
            if self.ic == 0:
                self.c += 1
            else:
                self.ic -= 1
        else:
            if self.c == 0:
                self.ic += 1
            else:
                self.c -= 1


    def entropy(self, arg):
        return -(arg * log(arg, 2) + (1 - arg) * log((1 - arg), 2))
    
    def __repr__(self):
        return (f"Node_initZPD(c0={self.c0}")
    
    def __str__(self):
        return (f"Node_initZPD(c0: {self.c0}, colour: {self.colour}, "
                f"c: {self.c}, ic: {self.ic}, weight: {self.weight})")


def split_nodes(trace, dependency_graph):
    """
    Function that splits a given dependency graph using a given trace into two
    sets corresponding to more complex and less complex traces.

    Parameter(s):
        trace: string
        dependency_graph: dict(string -> list(string))
    
    Returns(s):
        trace_plus_set: set(string)
        trace_minus_set: set(string)


    trace_minus_set = set()
    dependencies = set(dependency_graph[trace])
    """
    pass


def calculate_total_weights(trace, dependency_graph, trace_node_dict):
    """
    Function that takes trace and a dependency graph and computes two sums, one 
    is of the weights of all nodes more complex than trace in the graph and the
    other is of the weights of all nodes less complex than trace in the graph.
    
    Parameter(s):
        trace: string
        dependency_graph: dict(string -> list(string))
        trace_node_dict: dict(string -> Node_initZPD)

    Returns:
        total_w_plus: int
        total_w_minus: int
    """

    pass


def update_nodes(trace,
                 dependency_graph,
                 trace_node_dict,
                 correct,
                 threshold):
    """
    Function to update the weights of the nodes corresponding to the traces in
    the dependency graph depending on the correct value and the given trace.

    Parameter(s):
        trace: string
        dependency_graph: dict(string -> list(string))
        trace_node_dict: dict(string -> Node_initZPD)
        correct: bool
        threshold: float
    
    Returns:
        None
    """    
    pass


def update_dependency_graph(dependency_graph, trace_node_dict):
    """
    Function that returns an updated dependency graph made by removing traces
    from the previous one according to the weight of the nodes of those traces.

    Parameter(s):
        dependency_graph: dict(string -> list(string))
        trace_node_dict: dict(string -> Node_initZPD)
    
    Returns:
        updated_dependency_graph: dict(string -> Node_initZPD)
    """
    uncoloured_traces = set()
    for trace in dependency_graph:
        if trace_node_dict[trace].colour == Colour.UNCOLOURED:
            uncoloured_traces.add(trace)
    
    updated_dependency_graph = {}
    for trace in uncoloured_traces:
        updated_dependency_graph[trace] = []
        for t in dependency_graph[trace]:
            if t in uncoloured_traces:
                updated_dependency_graph[trace].append(t)
    
    return updated_dependency_graph


def get_initial_zpd(trace_to_node_dict, progression_graph):
    """
    Function that takes a trace node dictionary and makes a zpd set containing
    traces that lie in the zpd according to the colour of the corresponding
    nodes.

    Parameter(s):
        trace_node_dict: dict(string -> Node_initZPD)
        progression_graph: dict(string -> list(string))
    
    Returns:
        zpd: set(string)
    """

    zpd = set()
    solvable_traces = set()
    for trace, node in trace_to_node_dict.items():
        if node.colour == Colour.SOLVABLE:
            solvable_traces.add(trace)
    
    if not solvable_traces:
        zpd |= set(progression_graph[""])
    else:
        # Collect the traces corresponding to the ZPD region.
        for trace in solvable_traces:
            unsolved_set = set()
            for t in progression_graph[trace]:
                if t not in solvable_traces:
                    unsolved_set.add(t)

            if unsolved_set:
                zpd |= unsolved_set
                zpd.add(trace)

    return zpd

def is_correct(problem, answer):
    return answer == problem[2]

def initial_zpd(progression_graph,
                trace_problems_dict,
                regularisation_0,
                entropy_threshold,
                student):
    """
    Function that computes the initial zpd for a student object.

    Parameter(s):
        progression_graph: dict(string -> list(string))
        trace_problems_dict: dict(string -> list(int, int, int, string))
        regularisation_0: float
        entropy_threshold: float
        student: Student
    
    Returns:
        zpd: set(string)
    """
    problem_count = 0

    # Traces set without the start trace.
    traces = set(progression_graph.keys())
    traces.remove("")
    
    # Create a map from trace to corresponding problem list iters. (To ask 
    # all questions of a particular type, to prevent repitition)
    trace_to_problem_iters_dict = {}
    for t, probs in trace_problems_dict.items():
        trace_to_problem_iters_dict[t] = iter(probs)

    # Create a map from every trace to a corresponding initZPD node.
    trace_to_node_dict = {}
    for trace in traces:
        # Problem: list or single instance?
        trace_to_node_dict[trace] = Node_initZPD(regularisation_0)
    
    log = f"Generated dictionary: "
    for t, n in trace_to_node_dict.items():
        log += f"\n{t} -> NODE: {n}"
    logger.info(log)

    # Create a map from trace to traces at least as complex as it.
    trace_to_at_least_complex_traces_dict = {}
    for t1 in traces:
        at_least_complex_traces_set = set()
        for t2 in traces:
            if atleast_complex(t2, t1):
                at_least_complex_traces_set.add(t2)
            
        at_least_complex_traces_set.remove(t1)
        trace_to_at_least_complex_traces_dict[t1] = at_least_complex_traces_set
 
    # Create a map from trace to traces at most as complex as it.
    trace_to_at_most_complex_traces_dict = {}
    for t1 in traces:
        at_most_complex_traces_set = set()
        for t2 in traces:
            if atleast_complex(t1, t2):
                at_most_complex_traces_set.add(t2)
            
        at_most_complex_traces_set.remove(t1)
        trace_to_at_most_complex_traces_dict[t1] = at_most_complex_traces_set
 
    log = f"Generated map from trace to traces at least as complex: "
    for t, alct in trace_to_at_least_complex_traces_dict.items():
        log += f"\n{t} -> {alct}"
    logger.info(log)

    log = f"Generated map from trace to traces at most as complex: "
    for t, amct in trace_to_at_most_complex_traces_dict.items():
        log += f"\n{t} -> {amct}"
    logger.info(log)

    # Create two maps One from trace to traces less-complex than it. Another 
    # from trace to traces more-complex than it.
    trace_to_less_complex_traces_dict = {}
    trace_to_more_complex_traces_dict = {}
    for trace in traces:
        trace_to_less_complex_traces_dict[trace] = set()
        trace_to_more_complex_traces_dict[trace] = set()

    for trace in traces:
        unadded_set = set(progression_graph[trace])
        more_complex_traces_set = set()
        while len(unadded_set) > 0:
            elem = unadded_set.pop()
            unadded_set |= set(progression_graph[elem])
            more_complex_traces_set.add(elem)
            trace_to_less_complex_traces_dict[elem].add(trace)
        
        trace_to_more_complex_traces_dict[trace] = more_complex_traces_set

    log = f"Generated map from trace to less complex traces: "
    for t, lct in trace_to_less_complex_traces_dict.items():
        log += f"\n{t} -> {lct}"
    logger.info(log)

    log = f"Generated map from trace to more complex traces: "
    for t, mct in trace_to_more_complex_traces_dict.items():
        log += f"\n{t} -> {mct}"
    logger.info(log)

    # Uncoloured set of nodes.
    uncoloured_traces = set(traces)

    # Loop.
    logger.info("Starting loop.")
    while len(uncoloured_traces) > 0:

        # Find trace with max min of total plus weights and total minus weights.
        max_min_weight = 0
        # Pick an arbitrary trace.
        chosen_trace = next(iter(uncoloured_traces))
        for t1 in uncoloured_traces:
            # Calculate total plus weight for t1.
            amct_set = trace_to_at_most_complex_traces_dict[t]
            tw_plus = 0
            for t2 in amct_set:
                if t2 in uncoloured_traces:
                    tw_plus += trace_to_node_dict[t2].weight
            
            # Calculate total minus weight for t1.
            alct_set = trace_to_at_least_complex_traces_dict[t]
            tw_minus = 0
            for t2 in alct_set:
                if t2 in uncoloured_traces:
                    tw_minus += trace_to_node_dict[t2].weight

            min_weight = min(tw_plus, tw_minus)
            if min_weight > max_min_weight:
                chosen_trace = t1
                max_min_weight = min_weight

        # Suggest a problem of chosen trace type to the student and record the 
        # result.
        try:
            problem = next(trace_to_problem_iters_dict[chosen_trace])
        except StopIteration:
            trace_to_problem_iters_dict[chosen_trace] = iter(
                                    trace_problems_dict[chosen_trace])
            problem = next(trace_to_problem_iters_dict[chosen_trace])

        answer = student.solve(problem)
        problem_count += 1
        correctness = is_correct(problem, answer)

        log = (f"Chosen trace: {chosen_trace}, chosen problem: {problem},"
               f"answer: {answer}, Is correct: {correctness}")
        logger.info(log)

        # Update the correctness for node and all node dependencies.
        node = trace_to_node_dict[chosen_trace]
        node.update_correctness(correctness)
        node.update_weight()

        if correctness:
            for t in trace_to_less_complex_traces_dict[chosen_trace]:
                if t in uncoloured_traces:
                    node  = trace_to_node_dict[t]
                    node.update_correctness(correctness)
                    node.update_weight()
        
        else:
            for t in trace_to_more_complex_traces_dict[chosen_trace]:
                if t in uncoloured_traces:
                    node  = trace_to_node_dict[t]
                    node.update_correctness(correctness)
                    node.update_weight()
        
        # Remove traces that have gone below the entropy threshold.
        coloured_traces_set = set()
        for t in uncoloured_traces:
            n = trace_to_node_dict[t]
            if n.weight < entropy_threshold:
                if n.c > 0:
                    n.colour = Colour.SOLVABLE
                else:
                    n.colour = Colour.UNSOLVABLE
                
                coloured_traces_set.add(t)
        
        uncoloured_traces.difference_update(coloured_traces_set)

        log = f"Updated nodes: "
        for trace, node in trace_to_node_dict.items():
            log += f"\n{trace} -> {node}"
        logger.info(log)

    logger.info("Finished loop.")

    zpd = get_initial_zpd(trace_to_node_dict, progression_graph)
    
    log = f"Generated initial ZPD: "
    for trace in zpd:
        log += f"\nTrace: {trace}"
    logger.info(log)

    logger.info(f"Number of problems asked: {problem_count}")
    print(f"Init ZPD: {problem_count}")

    return zpd

