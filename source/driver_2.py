import time
import logging
from datetime import datetime

from copy import deepcopy
from generate_progression import generate_progression
from bayesian_initialzpd import bayesian_initialzpd
from zpdes import zpdes
from hyperparameters import progression_size, bayesian_initialzpd_threshold,\
    bayesian_initialzpd_alpha, bayesian_initialzpd_beta, \
    bayesian_initialzpd_timeout, zpdes_beta, zpdes_eta, zpdes_d, zpdes_h, \
    zpdes_initial_weight, zpdes_gamma, transition_probabilities_1, \
    transition_probabilities_2, guess_probabilities, slip_probabilities, \
    kc_states, knowledge_component_prerequisites

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
    
    n_symbols_dict = {key:0 for key in ["A", "B", "C", "D"]}
    for t in trace:
        if t == "A":
            n_symbols_dict["A"] += 1
        elif t == "B":
            n_symbols_dict["B"] += 1
        elif t == "C":
            n_symbols_dict["C"] += 1
    
    # 1: "One digit addition without overflow.", (A)
    if n_symbols_dict["A"] == 1:
        kc = 1
    # 2: "One digit addition with overflow.", (A, C)
    elif n_symbols_dict["A"] == 1 and n_symbols_dict["C"] == 1:
        kc = 2
    # 4: "Two digit addition with carry.", (A, A, C) or (A, C, B)
    elif n_symbols_dict["A"] + n_symbols_dict["B"] == 2 and n_symbols_dict["C"] > 0:
        kc = 4
    # 3: "Two digit addition without carry.", (A, A)
    elif n_symbols_dict["A"] == 2:
        kc = 3
    # 6: "Three digit addition with carry."
    elif n_symbols_dict["A"] + n_symbols_dict["B"] == 3 and n_symbols_dict["C"] > 0:
        kc = 6
    # 5: "Three digit addition without carry.", (A, A, A)
    elif n_symbols_dict["A"] == 3:
        kc = 5
    # 8: "Four digit addition with carry." (A, B)
    elif n_symbols_dict["A"] + n_symbols_dict["B"] == 4 and n_symbols_dict["C"] > 0:
        kc = 8
    # 7: "Four digit addition without carry.", (A, A, A, A)
    elif n_symbols_dict["A"] == 4:
        kc = 7
    
    return kc                        

def get_prerequisites(kc):
    return knowledge_component_prerequisites[kc]

def get_solution(problem):
    return problem[2]

def main():
    
    logger.info("Test started.")
    zpdes_student = Student(kc_states,
                            transition_probabilities_1,
                            slip_probabilities,
                            guess_probabilities,
                            get_prerequisites,
                            get_kc,
                            get_solution)
    init_student = Student(kc_states,
                           transition_probabilities_2,
                           slip_probabilities,
                           guess_probabilities,
                           get_prerequisites,
                           get_kc,
                           get_solution)

    trace_problems_dict, progression_graph = generate_progression(progression_size)

    init_zpd = bayesian_initialzpd(progression_graph,
                                   trace_problems_dict,
                                   bayesian_initialzpd_timeout,
                                   bayesian_initialzpd_alpha,
                                   bayesian_initialzpd_beta,
                                   bayesian_initialzpd_threshold,
                                   init_student)

    zpdes(init_zpd,
          trace_problems_dict,
          progression_graph,
          zpdes_beta,
          zpdes_eta,
          zpdes_h,
          zpdes_d,
          zpdes_gamma,
          zpdes_initial_weight,
          zpdes_student)

    logger.info(f"{zpdes_student.status()}")
    logger.info("Test finished.")

    return

if __name__ == "__main__":
    main()