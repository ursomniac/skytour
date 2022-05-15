from numpy import rec
from ..dso.models import AtlasPlate
from .models import Constellation, ConstellationVertex, ConstellationBoundaries

def convert(s):
    sign = None
    if s[0] in ['+', '-']:
        sign = s[0]
        s = s[1:]
    dd, mm, ss = s.split(':')
    f = int(dd) + 0.
    f += int(mm) / 60.
    f += int(ss) / 3600.
    if sign == '-':
        f *= -1.
    return f

def process_vertex(line, debug=False):
    line = line.strip('\n')
    line = line.replace('SER1', 'SER')
    line = line.replace('SER2', 'SER')
    fields = line.split(' ')
    id = int(fields[0])
    ra = convert(fields[1])
    dec = convert(fields[2])
    con_abbr = fields[3:]
    constellations = Constellation.objects.filter(abbreviation__in=con_abbr)

    if debug:
        print(f"ID: {id}, RA: {ra}, DEC: {dec} ")
        print(f"Constellations: {constellations}")
        
    else:
        rec = ConstellationVertex()
        rec.pk = id
        rec.ra_1875 = ra
        rec.dec_1875 = dec
        rec.save()
        rec.constellation.add(*constellations)
        rec.save()
        return rec

def delete_vertices():
    vv = ConstellationVertex.objects.all()
    for v in vv:
        v.delete()

def import_vertices():
    delete_vertices()
    with open('data/constellation_metadata/verts_18.txt') as f:
        lines = f.readlines()
    for l in lines:
        # 685 08:22:00 -36:45:00 PUP PYX VEL
        rec = process_vertex(l)

def delete_lines():
    ll = ConstellationBoundaries.objects.all()
    for l in ll:
        l.delete()

def process_boundary(row, n):
    """
     0.1740267 +23.695751 030:031
    """
    row = row.strip('\n')
    if row[0] == ' ':
        row = row[1:]
    ra, dec, vertices = row.split(' ')
    v1, v2 = vertices.split(':')

    rec = ConstellationBoundaries()
    rec.pk = n
    rec.ra = ra
    rec.dec = dec
    rec.start_vertex = v1
    rec.end_vertex = v2
    rec.save()
    return rec

def import_lines():
    delete_lines()
    with open('data/constellation_metadata/lines_in_20.txt') as f:
        lines = f.readlines()
    n = 1
    for l in lines:
        rec = process_boundary(l, n)
        n += 1

def run_things(plate_id):
    plate = AtlasPlate.objects.get(plate_id=plate_id)
    # get constellations on plate
    const_list = plate.constellation.all()
    # get vertices for these constellations
    verts = ConstellationVertex.objects.filter(constellation__in=const_list)
    vert_list = verts.values_list('pk', flat=True)
    # get boundary line segments
    segments = ConstellationBoundaries.objects.filter(start_vertex__in=vert_list)
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
