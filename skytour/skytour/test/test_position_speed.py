import time, datetime, pytz
from skyfield.api import utc
from skytour.apps.solar_system.position import get_object_metadata
from skytour.apps.solar_system.models import Asteroid, Comet
from skytour.apps.observe.models import ObservingLocation

MY_LOC = ObservingLocation.objects.get(pk=1)

def get_metadata(d):
    equ = d['apparent']['equ']
    radec = f"{equ['ra_str']} {equ['dec_str']}"
    dist = f"{d['apparent']['distance']['au']:.3f} AU"
    mag = f"{d['observe']['apparent_magnitude']:.2f}"
    const = d['observe']['constellation']['abbr']
    return '\t'.join([radec, dist, mag, const])

def show_time(t0, t1, t2, label):
    dtall = t2 - t0
    dtlast = t2 - t1
    print (f'{t2:.3f}s\t{dtlast:.3f} ∆t\t{dtall:.3f}\t{label}')

def time_objects(utdt, objtype, objects):
    t0 = t1 = t2 = time.perf_counter()
    show_time(t0, t0, t0, 'Start Asteroid Test')
    n = 1
    for obj in objects:
        label = f"{n}: {obj}"
        d = get_object_metadata(
            utdt, 'None', objtype, 
            instance=obj, 
            location=None, 
            time_zone=None
        )
        t1 = t2
        t2 = time.perf_counter()
        show_time(t0, t1, t2, f"{label}\t{get_metadata(d)}")
        n += 1
    return

def test_asteroids(utdt):
    objects = Asteroid.objects.all()
    time_objects(utdt, 'asteroid', objects)

def test_comets(utdt):
    objects = Comet.objects.all()
    time_objects(utdt, 'comet', objects)

def run_tests():
    utdt = datetime.datetime.now(datetime.timezone.utc)
    test_asteroids(utdt)
    test_comets(utdt)



        