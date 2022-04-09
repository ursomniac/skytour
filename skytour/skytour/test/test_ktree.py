import math
from scipy import spatial
from skytour.apps.dso.models import DSO
from skytour.apps.astro.transform import get_cartesian

def arc_angle(d, r = 1, degrees=False):
    theta = 2. * math.asin(d / r / 2)
    if degrees:
        theta = math.degrees(theta)
    return theta # radians

def chord_length(theta, r = 1, degrees=False):
    if degrees:
        theta = math.radians(theta)
    return 2 * r * math.sin(theta/2.)

def get_neighbors(dso, fov=8., fudge=90, sort=False):
    """
    Given a circle of N degrees, what DSOs are in that circle
    centered on some (ra, dec)?

    This uses scipy.spatial KDTrees to do this efficiently.
    It might not be TERRIBLY precise, but good enough.
    """ 
    radius = chord_length(fov, degrees=True) * fudge
    print("FOV: ", fov, "RADIUS: ", radius)
    dso_objects = DSO.objects.exclude(pk=dso.pk)
    dso_list = []
    closest_dsos = []
    for other_dso in dso_objects:
        dso_list.append(other_dso.get_xyz)
    print("DSO LIST SIZE: ", len(dso_list))
    center = get_cartesian(dso.ra_float, dso.dec_float, ra_dec=True)
    tree = spatial.KDTree(dso_list)
    closest = tree.query_ball_point([center], radius, return_sorted=sort)
    for x in closest[[0][0]]:
        #print("X: ", x, type(x))
        d = dso_objects[x]
        closest_dsos.append(d)
    print("# FOUND: ", len(closest_dsos))
    print("DSOS: ",closest_dsos)
    return tree, closest, closest_dsos

#lat1 = math.radians(90)
#lat2 = math.radians(-90)
#lon1 = 0
#lon2 = 0
#r = 1.

def ctest(dlat1, dlon1, dlat2, dlon2, r):
    lat1 = math.radians(dlat1)
    lat2 = math.radians(dlat2)
    lon1 = math.radians(dlon1)
    lon2 = math.radians(dlon2)

    x1 = r * math.cos(lat1) * math.cos(lon1)
    x2 = r * math.cos(lat2) * math.cos(lon2)
    y1 = r * math.cos(lat1) * math.sin(lon1)
    y2 = r * math.cos(lat2) * math.sin(lon2)
    z1 = r * math.sin(lat1)
    z2 = r * math.sin(lat2)
    print (f"X1: {x1:.5f}  Y1: {y1:.5f}  Z1: {z1:.5f}")
    print (f"X2: {x2:.5f}  Y2: {y2:.5f}  Z2: {z2:.5f}")

    dx = x2 - x1
    dy = y2 - y1
    dz = z2 - z1
    print (f"dX: {dx:.5f}  dY: {dy:.5f}  dZ: {dz:.5f}")

    dd = dx*dx + dy*dy + dz*dz
    d = math.sqrt(dd)
    print (F"DD: {dd:.5f}  D: {d:.5f}")
    is_deg = math.degrees(d * 1.1107207345)
    print (f"Got: {is_deg:.5f}  Ratio: {1. - (90-dlat2)/is_deg:.5f}")

