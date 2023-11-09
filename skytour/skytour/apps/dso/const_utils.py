from django.db.models import Q
from ..utils.models import Constellation, ConstellationBoundaries, ConstellationVertex
from .models import AtlasPlate

def get_boundary_lines(identifier, model_type='plate'):
    """
    Get all of the constellation boundaries seen on a plate.
    This is slightly optimized: it uses the list of known constellations on the plate,
    and only returns the lines relevant to them.   
    """
    if model_type == 'plate':
        plate = AtlasPlate.objects.get(plate_id=identifier)
        # get constellations on plate
        const_list = plate.constellation.all()
    else:
        constellation = Constellation.objects.get(abbeviation=identifier.upper())
        const_list = constellation.neighbors.all()

    # get vertices for these constellations
    verts = ConstellationVertex.objects.filter(constellation__in=const_list)
    vert_list = verts.values_list('pk', flat=True)
    # get boundary line segments
    segments = ConstellationBoundaries.objects.filter(Q(start_vertex__in=vert_list) | Q(end_vertex__in=vert_list))
    lines = {}
    p = 0
    for seg in segments:
        v1 = seg.start_vertex
        v2 = seg.end_vertex
        t = tuple([v1, v2])
        if t not in lines.keys():
            lines[t] = []
        lines[t].append(tuple([seg.ra, seg.dec]))
        p += 1
    return lines, p