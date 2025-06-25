from .models import Asteroid

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

def load_asteroids():
    with open('generated_data/bright_asteroids.txt') as f:
        lines = f.readlines()

    for line in lines:
        if line[0] != '0':
            continue # skip headers
        id = tr(line, 1, 7, 'int')
        asteroid = Asteroid.objects.filter(number=id).first() or Asteroid()
        asteroid.pk = id
        asteroid.number = id
        # H
        asteroid.h = tr(line, 9, 5, 'float')
        # G
        asteroid.g = tr(line, 15, 5, 'float')
        # Epoch
        asteroid.epoch = tr(line, 21, 5, 'str')
        # Mean Anomaly
        asteroid.mean_anomaly = tr(line, 27, 9, 'float')
        # Argument of Perihelion
        asteroid.arg_perihelion = tr(line, 38, 9, 'float')
        # Long. of Asc. Node
        asteroid.long_asc_node = tr(line, 49, 9, 'float')
        # Inclination
        asteroid.inclination = tr(line, 60, 9, 'float')
        # Eccentricity
        asteroid.eccentricity = tr(line, 71, 9, 'float')
        # Mean daily motion
        asteroid.daily_motion = tr(line, 81, 11, 'float')
        # Semimajor Axis
        asteroid.semi_major_axis = tr(line, 93, 11, 'float')
        # Name
        asteroid.name = tr(line, 176, 12, 'str')

        asteroid.save()

def update_planet_wiki(planet=None):
    if planet is None:
        return None
    
