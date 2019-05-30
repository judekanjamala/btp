from collections import defaultdict
from functools import cmp_to_key
from operator import itemgetter
import math
import cvxpy as cp

import logging

from hyperparameters import ngram_size
from compare_traces import cmp_trace

from student import KC_STATE
logger = logging.getLogger(f"zpd.{__name__}")
logger.setLevel(logging.DEBUG)


class KL_UCB_node():

    def __init__(self, n0, n1):

        self.n0_t0 = n0
        self.n1_t0 = n1
        self.p_t0 = n1 / (n0 + n1)
        self.n0_t1 = self.n0_t0
        self.n1_t1 = self.n1_t0
        self.p_t1 = self.p_t0
        # self.known = False
        # self.dependency_prob_dict = {}
    
    def update(self):
        self.n0_t0 = self.n0_t1
        self.n1_t0 = self.n1_t1
        self.p_t0 = self.p_t1

    def __repr__(self):
        return f"KL_UCB_node(n0={self.n0_t0}, n1={self.n1_t0})"
    
    def __str__(self):
        s = (f"KL_UCB_node:n0={self.n0_t0}, n1={self.n1_t0}, p={self.p_t0}")
        return s


def kl_ucb_zpd(progression_graph,
               trace_problems_dict,
               kl_ucb_lower_threshold,
               kl_ucb_n0,
               kl_ucb_n1,
               timeout,
               p_threshold,
               student):
    
    def is_correct(problem, answer):
        return answer == problem[2]
    
    traces = set(progression_graph.keys())
    traces.remove("")

    # Create nodes to store algorithm-specific trace details.
    trace_node_dict = {trace: KL_UCB_node(kl_ucb_n0, kl_ucb_n1)
                       for trace
                       in traces}
    trace_node_dict[""] = KL_UCB_node(0, 1) # Jon Snow knows nothing.
    log = f'Trace -> KL-UCB Node dictionary created.'
    logger.info(log)

    # Create a dependency graph of traces. (Reverse of the progression graph.)
    dependency_graph = {}
    for trace in progression_graph.keys():
        dependency_graph[trace] = []

    for trace, more_complex_traces in progression_graph.items():
        for i in more_complex_traces:
            dependency_graph[i].append(trace)

    log = f"Generated dependency graph: "
    for trace, less_complex_trace in dependency_graph.items():
        log += f"\n{trace} -> {less_complex_trace}"
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

    # Do topological ordering of the progression graph.
    sorted_traces = sorted(traces, key=cmp_to_key(cmp_trace))
    
    log = f'Generalised topological sort of the traces.\n'
    for trace in sorted_traces:
        log += f'\nTrace - {trace}'
    logger.info(log)

    # Run the kl-ucb bandit algorithm.
    # t = 1 is over when initialising the nodes.
    t = 2
    while t < timeout:
        # Create a dict that maps each max entropy value to the corresponding
        # traces.
        fp_traces_dict = defaultdict(set)
        for trace in traces:
            node = trace_node_dict[trace]
            kl_limit = (math.log(1 + t * math.log(math.log(t, 2), 2), 2) /
                        (node.n0_t0 + node.n1_t0))
            # print(kl_limit)
            u = cp.Variable()
            kl_d = ((cp.kl_div(node.p_t0, u) + cp.kl_div(1 - node.p_t0, 1 - u))
                     / math.log(2))
            constraints = [kl_d <= kl_limit,
                          u <= 1,
                          u >= 0]
#            obj = cp.Maximize((cp.entr(u) + cp.entr(1 - u)) / math.log(2))
            obj = cp.Minimize(u)
            # print(f"obj is dcp {obj.is_dcp()}") 
            prob = cp.Problem(obj, constraints)
            prob.solve()
            # print(f"Trace {trace} and p:{u.value}")
            if prob.value < kl_ucb_lower_threshold:
                fp_traces_dict[prob.value].add(trace)
        
        if len(fp_traces_dict) == 0:
            logger.info(f"No traces above kl_ucb_lower_threshold")
            continue

        log = (f'f(p) for each trace calculated for round {t}.')
        for fp, ts in fp_traces_dict.items():
            log += f'\nfp: {fp} -> Traces: {ts}'
        logger.info(log)

        # Select the trace with the maximum entropy among all traces, i.e. the
        # arm, in topological order.
        max_fp, max_fp_traces_set = itemgetter(0)(sorted(
                                             fp_traces_dict.items(),
                                             key=itemgetter(0),
                                             reverse=True))

        for trace in sorted_traces:
            if trace in max_fp_traces_set:
                trace_arm = trace
                break

        # Ask the student a problem corresponding to the chosen trace and record
        # the answer.
        chosen_problem = trace_problems_dict[trace_arm][0]
        answer = student.solve(chosen_problem)
        node = trace_node_dict[trace_arm]
        
        log = (f'\nMax fp: {max_fp}\nMax traces: {max_fp_traces_set}'
               f'\nTrace-arm: {trace_arm}\nProblem: {chosen_problem}'
               f'\nAnswer: {answer}')
        logger.info(log)
        
        # Update the nodes of the algorithm according to the correctness of the 
        # answer.
        if is_correct(chosen_problem, answer):
            node = trace_node_dict[trace_arm]
            node.n1_t1 = node.n1_t0 + 1
            node.n0_t1 = node.n0_t0
            node.p_t1 = node.n1_t1 / (node.n0_t1 + node.n1_t1)
            for trace in trace_to_less_complex_traces_dict[trace_arm]:
                node = trace_node_dict[trace]
                node.n1_t1 = node.n1_t0 + 1
                node.n0_t1 = node.n0_t0
                node.p_t1 = node.n1_t1 / (node.n0_t1 + node.n1_t1)
        else:
            # Calculate probability of answering by taking product of the
            # probabilities of the dependants of chosen trace. 
            node = trace_node_dict[trace_arm]
            node.n1_t1 = node.n1_t0 
            node.n0_t1 = node.n0_t0 + 1
            node.p_t1 = node.n1_t1 / (node.n0_t1 + node.n1_t1)

            for trace in trace_to_more_complex_traces_dict[trace_arm]:
                node = trace_node_dict[trace]
                node.n1_t1 = node.n1_t0
                node.n0_t1 = node.n0_t0 + 1
                node.p_t1 = node.n1_t1 / (node.n0_t1 + node.n1_t1)


        for trace, node in trace_node_dict.items():
            node.update()

        log = f'Updation of nodes completed.'
        for trace, node in trace_node_dict.items():
            log += f'\nTrace: {trace} -> Node: {node}'
        logger.info(log)

        if all([s == KC_STATE.LEARNED for s in student.kc_states.values()]):
            print("Yipe")
            break

        t += 1

    init_zpd = set()
    for trace, dependencies in dependency_graph.items():
        if trace_node_dict[trace].p_t0 <= p_threshold:
            dependency_threshold = [trace_node_dict[t].p_t0 > p_threshold
                                    for t in dependencies]
            for i, threshold in enumerate(dependency_threshold):
                if threshold:
                    init_zpd.add(dependencies[i])
            if any(dependency_threshold):
                init_zpd.add(trace)

    return init_zpd
