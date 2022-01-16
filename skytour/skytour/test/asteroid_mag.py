import gzip
import math

def tr(line, col, length, type):
    start = col-1
    end = col-1+length
    str = line[start:end]
    if str.isspace() or str == '':
        return None
    if type == 'int':
        return int(str)
    elif type == 'float':
        str.replace('+', ' ')
        return float(str)
    return str.strip()

def get_target_asteroids():
    file = gzip.open('MPCORB.DAT.gz', 'rt')
    contents = file.read()
    lines = contents.split('\n')[43:]

    for line in lines[:10000]:
        id = tr(line, 1, 7, 'int')
        # H
        h = tr(line, 9, 5, 'float')
        # G
        g = tr(line, 15, 5, 'float')
        # Epoch
        #epoch = tr(line, 21, 5, 'str')
        # Mean Anomaly
        #mean_anomaly = tr(line, 27, 9, 'float')
        # Argument of Perihelion
        #arg_perihelion = tr(line, 38, 9, 'float')
        # Long. of Asc. Node
        #long_asc_node = tr(line, 49, 9, 'float')
        # Inclination
        #inclination = tr(line, 60, 9, 'float')
        # Eccentricity
        eccentricity = tr(line, 71, 9, 'float')
        # Mean daily motion
        #daily_motion = tr(line, 81, 11, 'float')
        # Semimajor Axis
        semi_major_axis = tr(line, 93, 11, 'float')
        # Name
        name = tr(line, 176, 12, 'str')

        q = semi_major_axis * (1. - eccentricity)
        dq = q - 1.017
        type = 'MBA'
        if dq < 0.:
            tq = .01
            type = 'NEO'
            continue

        tq = 0.001 if dq < 0. else dq

        # let beta = 0 which makes phi_1 and phi_2 = 1.
        mag = h + 5 * math.log10(tq * q)
        if mag >= 12.:
            continue
      

        print ("{} {:-6d} {:12s}:  {:5.2f}  {:7.4f}  {:7.4f}  {:5.1f}  {:7.4f}  {:6.4f}".format(
            type, id, name, mag, tq, q, h, semi_major_axis, eccentricity
        ))
