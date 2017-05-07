import math
def round_num(unrounded, roundUp):
    """
    implents "round to zero" and "round to infinity
    :param unrounded: 
    :param roundUp: 
    :return: 
    """
    if roundUp:
        if float(unrounded - int(unrounded)) < 0.01:
            return int(unrounded)
        else:
            return math.ceil(unrounded)
    elif math.ceil(unrounded) - unrounded < 0.01:
        return math.ceil(unrounded)
    return int(unrounded)