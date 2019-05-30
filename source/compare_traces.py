from hyperparameters import ngram_size

def atleast_complex(t1, t2):
    """
    Functions takes two trace string, t1 and t2, and returns True is t1 >= t2,
    otherwise False
    """

    def split(trace):
        """
        Function takes a trace and splits it into n sized contiguous pieces.

        Parameter(s):
            trace: string
            n: int

        Returns:
            n_grams: set(string)
        """
        n_grams = set()
        if len(trace) < ngram_size:
            n_grams.add(trace)
        else:
            for i in range(len(trace) - ngram_size + 1):
                n_grams.add(trace[i:i + ngram_size])
        
        return n_grams

    t1_ngrams = split(t1)
    t2_ngrams = split(t2)
    
    result = False
    
    # Condition corresponding t1 being as complex as t2
    if t1_ngrams == t2_ngrams:
        result = True
    
    # Condition corresponding to t1's ngrams being a strict
    # superset of t2's ngrams
    elif t1_ngrams.issuperset(t2_ngrams):
        result = True  
    
    # Condition corresponding to t1 and t2 being smaller than the
    # the ngram_size parameter but t1 is contiguous sequence in t2.
    elif t1 not in t2 and t2 in t1:
        result = True
    
    return result

def cmp_trace(t1, t2):
    """
    Compares two trace strings, t1 and t2 and returns 1 if t1 > t2, -1 if
    t1 < t2, else 0.

    Parameter(s):
        t1: string
        t2: string
    
    Returns:
        result: int (1, 0, -1)
    """

    t1_ge_t2 = atleast_complex(t1, t2)
    t2_ge_t1 = atleast_complex(t2, t1)
    
    if t1_ge_t2 and t2_ge_t1:
        result = 0
    elif t1_ge_t2:
        result = 1
    elif t2_ge_t1:
        result = -1
    else:
        result = 0

    return result
