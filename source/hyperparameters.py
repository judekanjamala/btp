action_tag_dict = {"One digit addition without carry.": 'A',
                   "One digit addition with carry.": 'B',
                   "Writing a carry.": 'C',
                   "Bringing down a carry.": 'D'}
tag_action_dict = {tag: action for action, tag in action_tag_dict.items()}
ngram_size = 3
ndigit_n_dict = {1: 15, 2: 15, 3: 15, 4: 15}
trace_file = "traces.csv"
progression_graph_file = "progression_graph.txt"
trace_problems_file = "trace_problems_dict.txt"

init_zpd_regularisation_0 = 4
init_zpd_entropy_threshold = 0.35

zpdes_beta = 0.9
zpdes_eta = 0.4
zpdes_d = 6
zpdes_h = 0.9
zpdes_initial_weight = 1
zpdes_gamma = 0.3

knowledge_components = {1: "One digit addition without overflow.",
                        2: "One digit addition with overflow.",
                        3: "Two digit addition without carry.",
                        4: "Two digit addition with carry.",
                        5: "Three digit addition without carry.",
                        6: "Three digit addition with carry.",
                        7: "Four digit addition without carry.",
                        8: "Four digit addition with carry."}
student1_kc_states = {1: 0,
                      2: 0,
                      3: 0,
                      4: 0,
                      5: 0,
                      6: 0,
                      7: 0,
                      8: 0}
student2_kc_states = {1: 1,
                      2: 1,
                      3: 1,
                      4: 1,
                      5: 1,
                      6: 1,
                      7: 1,
                      8: 1}
student3_kc_states = {1: 1,
                      2: 1,
                      3: 1,
                      4: 1,
                      5: 0,
                      6: 0,
                      7: 0,
                      8: 0}
student4_kc_states = {1: 1,
                      2: 1,
                      3: 1,
                      4: 1,
                      5: 1,
                      6: 1,
                      7: 0,
                      8: 0}

knowledge_component_prerequisites = {1: [],
                                     2: [1],
                                     3: [1, 2],
                                     4: [2, 3],
                                     5: [3],
                                     6: [4],
                                     7: [5],
                                     8: [6]}
transition_probabilities_kl_ucb = {1: {"low":0.2, "high":0.6},
                                  2: {"low":0.2, "high":0.6},
                                  3: {"low":0.2, "high":0.6},
                                  4: {"low":0.2, "high":0.6},
                                  5: {"low":0.2, "high":0.6},
                                  6: {"low":0.2, "high":0.6},
                                  7: {"low":0.2, "high":0.6},
                                  8: {"low":0.2, "high":0.6}}
transition_probabilities_zpdes = {1: {"low":0.2, "high":0.6},
                                  2: {"low":0.2, "high":0.6},
                                  3: {"low":0.2, "high":0.6},
                                  4: {"low":0.2, "high":0.6},
                                  5: {"low":0.2, "high":0.6},
                                  6: {"low":0.2, "high":0.6},
                                  7: {"low":0.2, "high":0.6},
                                  8: {"low":0.2, "high":0.6}}
transition_probabilities_init_zpd = {1: {"low":0, "high":0},
                                     2: {"low":0, "high":0},
                                     3: {"low":0, "high":0},
                                     4: {"low":0, "high":0},
                                     5: {"low":0, "high":0},
                                     6: {"low":0, "high":0},
                                     7: {"low":0, "high":0},
                                     8: {"low":0, "high":0}}
guess_probabilities = {1: 0.01,
                       2: 0.01,
                       3: 0.01,
                       4: 0.01,
                       5: 0.01,
                       6: 0.01,
                       7: 0.01,
                       8: 0.01}
slip_probabilities = {1: 0.02,
                      2: 0.02,
                      3: 0.02,
                      4: 0.02,
                      5: 0.02,
                      6: 0.02,
                      7: 0.02,
                      8: 0.02}

bayesian_initialzpd_start = "start"
bayesian_initialzpd_threshold = 0.7
bayesian_initialzpd_alpha, bayesian_initialzpd_beta = (1, 3)
bayesian_initialzpd_timeout = 6

kl_ucb_timeout = 1000
kl_ucb_lower_threshold = 0.5
kl_ucb_n0 = 1
kl_ucb_n1 = 1
kl_ucb_p_threshold = 0.7