import math
from scipy import spatial
from ..utils.python import grid_and_transpose_list
"""
These methods sort out finding a set of objects within an angular distance from a target.
"""

def chord_length(theta, r = 1, degrees=False):
    if degrees:
        theta = math.radians(theta)
        return 2 * r * math.sin(theta/2.)

def get_neighbors(
        object, 
        fov=8., 
        fudge=120,
        grid = True
    ):
    """
    For some reason the KDTree distances are 90 "off" for a FOV of 8°.
    I'm GUESSING it has something to do with there being a unit sphere.
    There are other weirdnessess that I can't suss out the math:
        1. the ratio between arc length and chord length for theta < 180
            is 1.1107207345 = pi/sqrt(8)
        2. 2. * sin(FOV/2*r) / FOV = pi
    """
    object_class = object.__class__
    other_objects = object_class.objects. exclude(pk=object.pk).order_by('catalog__slug', 'id_in_catalog')
    radius = chord_length(fov, degrees=True) * fudge
    coords = []
    for other in other_objects:
        coords.append(other.get_xyz)

    center = object.get_xyz
    tree = spatial.KDTree(coords)
    neighbor_list = tree.query_ball_point([center], radius)
    neighbor_objects = []
    for idx in neighbor_list[[0][0]]:
        neighbor_objects.append(other_objects[idx])
    
    if grid:
        return grid_and_transpose_list(neighbor_objects)
    else:
        return neighbor_objects

def get_small_ang_sep(ra1, dec1, ra2, dec2, degrees=True):
    xx = math.cos(math.radians((dec1 + dec2) / 2.))
    t1 = (15. * (ra1 - ra2) * xx) **2
    t2 = (dec1 - dec2) **2
    z = math.sqrt(t1 + t2)
    if degrees:
        return z
    else:
        return z * 3600. # arcseconds