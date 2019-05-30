import csv
from collections import defaultdict
import logging
import json

logger = logging.getLogger(f"zpd.{__name__}")
logger.setLevel(logging.DEBUG)

def form_progression(traces, cmp_trace):
    """
    Function takes a set of traces and forms a progression of the traces
    based on their complexity.

    Parameter(s):
        traces: set(string)

    Returns:
        trimmed_progression_graph: dict(string -> list(string))
    """
    
    # Create a graph traces with directed edges from less complex trace
    # to a more complex trace according to their respective ngrams.
    progression_graph = {}
    for trace in traces:
        progression_graph[trace] = set()
    
    for trace in traces:
        for t in traces:
            if cmp_trace(t, trace) > 0:
                progression_graph[trace].add(t)           

    # Remove excess edges from the progression graph.
    trimmed_progression_graph = {}
    for trace, more_complex_traces in progression_graph.items():
        revised_traces = list()
        for t in more_complex_traces:
            if any([(cmp_trace(t, x) > 0) for x in more_complex_traces]):
                continue
            else:
                revised_traces.append(t)
        trimmed_progression_graph[trace] = revised_traces
    
    return trimmed_progression_graph

def generate_curriculum(trace_file_path,
                        progression_graph_file_path,
                        trace_problems_file_path,
                        cmp_trace):
    """
    Function takes trace file and generates a progression graph from those
    traces. It then writes the progression graph and the trace-problem map as
    json objects to text files.

    Parameter(s):
        trace_file_path: string
    
    Returns:
        None
    """
    
    # Create a map between trace and corresponding problems. Also create a
    # traces set.
    logger.info("Creating progression from trace file.")
    with open(trace_file_path, 'r') as trace_file:
        reader = csv.reader(trace_file)
        # Skip header.
        next(reader)
        traces = set()
        trace_problems_dict = defaultdict(list)
        for row in reader:
            trace = row[-1]
            traces.add(trace)
            trace_problems_dict[trace].append((int(row[0]),
                                               int(row[1]),
                                               int(row[2]),
                                               row[3]))

    # Add the null/start trace to trace_problems_dict and traces set.
    trace_problems_dict[""] = []
    traces.add("")

    # Create the progression by ordering traces according to relative n_gram
    # complexity.
    progression_graph = form_progression(traces,cmp_trace)
    logger.info("Finished creating progression.")

    log = f"Progression graph."
    for trace, more_complex_traces in progression_graph.items():
        log += f"\n{trace} -> {more_complex_traces}"
    logger.info(log)

    log = f"Trace-Problems dictionary."
    for trace, problems in trace_problems_dict.items():
        log += f"\n{trace} -> {problems}"
    logger.info(log)

    with open(progression_graph_file_path, "w") as f:
        json.dump(progression_graph, f)
    
    with open(trace_problems_file_path, "w") as f:
        json.dump(trace_problems_dict, f)

    return None
