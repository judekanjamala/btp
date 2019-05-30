from collections import defaultdict
from operator import mul
from numpy import random
import sympy as sp
import logging
from math import gamma
from scipy import stats

from hyperparameters import bayesian_initialzpd_start

logger = logging.getLogger(f"zpd.{__name__}")
logger.setLevel(logging.DEBUG)

class Bayesian_initialzpd_node():

    def __init__(self):

        # self.probability_of_answering = 0
        self.visited = False
        self.known = False
        self.dependency_prob_dict = {}
    
    def __repr__(self):
        return f"Bayesian_initialzpd_node()"
    
    def __str__(self):
        s = (f"Bayesian_initialzpd_node:\nvisited: {self.visited},"
               f"\nknown: {self.known},\ndependency_prob_dict: ")
        
        for trace, prob in self.dependency_prob_dict.items():
            s += f"\n\t{trace} -> Prob: {prob}"
        
        return s


def get_solution(problem):
    """
    Helper function that returns solution for the given problem.
    """
    return problem[2]

# def get_answering_probability(trace_node_dict, trace):
#     node = trace_node_dict[trace]

#     if not node.visited:
#         node.visited = True
#         total_prob = sum(node.dependency_prob_dict.values())
#         if total_prob > 1:
#             for t, prob in node.dependency_prob_dict.items():
#                 node.probability_of_answering += ((prob / total_prob) *
#                         get_answering_probability(trace_node_dict, t))
#         else:
#             for t, prob in node.dependency_prob_dict.items():
#                 node.probability_of_answering += (prob * 
#                     get_answering_probability(trace_node_dict, t))

#     return node.probability_of_answering

def get_zpd_boundary(trace_node_dict, progression_graph):

    init_zpd = set()    
    for trace, node in trace_node_dict.items():
        if node.visited:
            continue
        node.visited = True
        is_boundary = any([(not trace_node_dict[t].known for t
                                          in progression_graph[trace])])
        if node.known and is_boundary:
            init_zpd.add(trace)

    return init_zpd

def bayesian_initialzpd(progression_graph,
                        trace_problems_dict,
                        timeout,
                        alpha,
                        beta,
                        threshold,
                        student):
    """
    """
    
    prior, =  random.beta(alpha, beta, 1)

    # Construct a probability graph with nodes corresponding to traces and with
    # edge weights as priors and edge direction opposite to that in progression
    # graph.
    trace_node_dict = {}
    non_basic_traces_set = set()
    for trace, more_complex_traces in progression_graph.items():
        trace_node_dict[trace] = Bayesian_initialzpd_node()
        non_basic_traces_set |= set(more_complex_traces)
    
    for trace, more_complex_traces in progression_graph.items():
        for t in more_complex_traces: 
            trace_node_dict[t].dependency_prob_dict[trace] = prior

    basic_traces_set = set(progression_graph.keys())
    basic_traces_set = basic_traces_set.difference(non_basic_traces_set)
    for trace in basic_traces_set:
        trace_node_dict[trace] = Bayesian_initialzpd_node()
        node = trace_node_dict[trace]
        node.dependency_prob_dict[bayesian_initialzpd_start] = prior
    
    trace_node_dict[bayesian_initialzpd_start] = Bayesian_initialzpd_node()
    # trace_node_dict[bayesian_initialzpd_start].probability_of_answering = 1

    updated_progression_graph = {}
    updated_progression_graph[bayesian_initialzpd_start] = list(
                                                            basic_traces_set)
    for trace, progression in progression_graph.items():
        updated_progression_graph[trace] = progression
    progression_graph = updated_progression_graph

    log = f"Generated trace node dict: "
    for trace, node in trace_node_dict.items():
        log += f"\n{trace} -> Node {node}"
    logger.info(log)

    # # Compute prior probability of answering for each trace.
    # for trace in progression_graph.keys():
    #     get_answering_probability(trace_node_dict, trace)

    # log = f"Generated prior probabilities of answering: "
    # for trace, node in trace_node_dict.items():
    #     log += f"\n{trace} -> prob: {node.probability_of_answering}"
    # logger.info(log)

    # A map from traces to iterators of the corresponding problem list. 
    trace_problemsIter_dict = {}
    for trace, problems in trace_problems_dict.items():
        trace_problemsIter_dict[trace] = iter(problems)
    
    logger.info(f"Generated iters.")

    # Generate answers.
    answers = defaultdict(list)
    for i in range(timeout):
        for trace in trace_problems_dict.keys():
            try:
                chosen_problem = next(trace_problemsIter_dict[trace])
            except StopIteration:
                trace_problemsIter_dict[trace] = iter(trace_problems_dict[trace])
                chosen_problem = next(trace_problemsIter_dict[trace])
            
            result = student.solve(chosen_problem)
            answers[trace].append(result == get_solution(chosen_problem))
    
    log = f"Recorded answers: "
    for trace, result in answers.items():
        log += f"\n{trace} -> {result}"
    logger.info(log)

    # # Calculate likelihood.
    # trace_likelihood_dict = {}
    # for trace, node in trace_node_dict.items():
    #     p = node.probability_of_answering
    #     n = sum(answers[trace])
    #     trace_likelihood_dict[trace] = pow(p, n) * pow(1 - p, timeout - n)
    
    # log = f"Calculated likelihood: "
    # for trace, likelihood in trace_likelihood_dict.items():
    #     log += f"\n{trace} -> {likelihood}"
    # logger.info(log)

    # # Find p(E).
    # x = sp.Symbol("x")
    # i = sp.integrate(x ** (n + alpha - 1) * (1 - x) ** (timeout - n + beta - 1),
    #                  (x, 0, 1))
    # beta_constant = 
    # print(i)

    # # Update posterior probability of answering of each trace and mark known
    # # nodes.
    # for trace, node in trace_node_dict.items():
    #     node.probability_of_answering *= trace_likelihood_dict[trace]
    #     if node.probability_of_answering > threshold:
    #         node.known = True

    # log = f"Calculated posterior probability of answering: "
    # for trace, node in trace_node_dict.items():
    #     log += f"\n{trace} -> {node.probability_of_answering}"
    # logger.info(log)

    # Updating prior belief.
    beta_constant = (gamma(alpha) * gamma(beta)) / gamma(alpha + beta)
    for trace, node in trace_node_dict.items():
        updated_dependency_prob_dict = {}
        for dependency, p in node.dependency_prob_dict.items():
            n = sum(answers[trace])
            likelihood = pow(p, n) * pow(1 - p, timeout - n)

            # Find p(E).
            x = sp.Symbol("x")
            i = sp.integrate(x ** (n + alpha - 1) * (1 - x) **
                            (timeout - n + beta - 1), (x, 0, 1))
            i /= beta_constant
            print(f"{trace} => {i}")

            # Update posterior probability and mark known nodes.
            posterior = stats.beta.pdf(p, alpha, beta) * likelihood / i
            if posterior > threshold:
                node.known = True
            updated_dependency_prob_dict[dependency] = posterior

            log = (f"Bayesian Update: {dependency} --> {trace}, Prior:{prior},"
                   f"Likelihood: {likelihood}, Posterior: {posterior}")
            logger.info(log)

        node.dependency_prob_dict = updated_dependency_prob_dict

    # Reset the visit parameter of the nodes.
    for trace, node in trace_node_dict.items():
        node.visit = False

    # Find the zpd from the topological strings.
    init_zpd = get_zpd_boundary(trace_node_dict,
                                progression_graph)

    if not init_zpd:
        init_zpd = set(progression_graph[bayesian_initialzpd_start])

    log = f"Generated initial zpd: "
    for trace in init_zpd:
        log += f"\n{trace}"
    logger.info(log)

    return init_zpd