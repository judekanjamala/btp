import time
import logging
from datetime import datetime
import json

from copy import deepcopy
from generate_trace import generate_2digitaddition_traces
from generate_curriculum import generate_curriculum
from compare_traces import cmp_trace
from kl_ucb_zpd import kl_ucb_zpd
from hyperparameters import ndigit_n_dict, trace_file, progression_graph_file, \
    trace_problems_file, init_zpd_entropy_threshold, \
    init_zpd_regularisation_0, zpdes_beta, zpdes_eta, \
    zpdes_d, zpdes_h, zpdes_initial_weight, zpdes_gamma, \
    guess_probabilities, slip_probabilities, knowledge_components,\
    knowledge_component_prerequisites, student1_kc_states, student2_kc_states,\
    student3_kc_states, student4_kc_states, \
    transition_probabilities_zpdes, transition_probabilities_init_zpd, \
    transition_probabilities_kl_ucb, kl_ucb_timeout, \
    kl_ucb_p_threshold, kl_ucb_lower_threshold, kl_ucb_n0, kl_ucb_n1

from student import Student

# Create test logger.
logger = logging.getLogger("zpd")
logger.setLevel(logging.DEBUG)

# Create file handler that logs to file tagged current date and time.
time_stamp = time.strftime("%Y%m%d_%H%M", datetime.now().timetuple())
fh = logging.FileHandler(f"logs/log", mode='w+')
fh.setLevel(logging.DEBUG)

# Create console handler that log warnings and above.
ch = logging.StreamHandler()
ch.setLevel(logging.WARNING)

# create formatter and add it to the handlers
formatter = logging.Formatter('%(name)s - %(funcName)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)

# add the handlers to the logger
logger.addHandler(fh)
logger.addHandler(ch)
def get_kc(problem):
    trace = problem[3]
    
    n_symbols_dict = {key:0 for key in ["A", "B", "C"]}
    for t in trace:
        if t == "A":
            n_symbols_dict["A"] += 1
        elif t == "B":
            n_symbols_dict["B"] += 1
        elif t == "C":
            n_symbols_dict["C"] += 1
    
    # 8: "Four digit addition with carry." (A, B)
    if n_symbols_dict["A"] + n_symbols_dict["B"] == 4 and n_symbols_dict["C"] > 0:
        kc = 8
    # 7: "Four digit addition without carry.", (A, A, A, A)
    elif n_symbols_dict["A"] == 4:
        kc = 7
    # 6: "Three digit addition with carry."
    elif n_symbols_dict["A"] + n_symbols_dict["B"] == 3 and n_symbols_dict["C"] > 0:
        kc = 6
    # 5: "Three digit addition without carry.", (A, A, A)
    elif n_symbols_dict["A"] == 3:
        kc = 5
    # 4: "Two digit addition with carry.", (A, A, C) or (A, C, B)
    elif n_symbols_dict["A"] + n_symbols_dict["B"] == 2 and n_symbols_dict["C"] > 0:
        kc = 4
    # 3: "Two digit addition without carry.", (A, A)
    elif n_symbols_dict["A"] == 2:
        kc = 3
    # 2: "One digit addition with overflow.", (A, C)
    elif n_symbols_dict["A"] == 1 and n_symbols_dict["C"] == 1:
        kc = 2
    # 1: "One digit addition without overflow.", (A)
    elif n_symbols_dict["A"] == 1:
        kc = 1
    
    # logger.info(f"KC: {kc}")
    
    return kc                        

def get_prerequisites(kc):
    return knowledge_component_prerequisites[kc]

def get_solution(problem):
    return problem[2]

def main():
    
    logger.info("Test started.")
    kl_ucb_student = Student(student2_kc_states,
                            transition_probabilities_kl_ucb,
                            slip_probabilities,
                            guess_probabilities,
                            get_prerequisites,
                            get_kc,
                            get_solution)
    init_student = Student(student3_kc_states,
                           transition_probabilities_init_zpd,
                           slip_probabilities,
                           guess_probabilities,
                           get_prerequisites,
                           get_kc,
                           get_solution)


    generate_2digitaddition_traces(ndigit_n_dict, trace_file)

    generate_curriculum(trace_file,
                        progression_graph_file,
                        trace_problems_file,
                        cmp_trace)

    with open(progression_graph_file, "r") as f:
        progression_graph = json.load(f)
    
    with open(trace_problems_file, "r") as f:
        trace_problems_dict = json.load(f)

    zpd = kl_ucb_zpd(progression_graph,
                               trace_problems_dict,
                               kl_ucb_lower_threshold,
                               kl_ucb_n0,
                               kl_ucb_n1,
                               kl_ucb_timeout,
                               kl_ucb_p_threshold,
                               kl_ucb_student)
    logger.info(f"Student status:{kl_ucb_student.status()}")
    log = f"Current ZPD:"
    for trace in zpd:
        log += f'\nTrace: {trace}'
    logger.info(log)

    logger.info("Test finished.")

    return

if __name__ == "__main__":
    main()