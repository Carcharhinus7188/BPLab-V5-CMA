
def average(values):
    values=[v for v in values if v is not None]
    return sum(values)/len(values) if values else 0

def warp_delta(h1,h2):
    return h1-h2
