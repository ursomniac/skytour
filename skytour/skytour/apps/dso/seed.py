import json
from .models import MilkyWay

def clear_database_table():
    all = MilkyWay.objects.all()
    for row in all:
        row.delete()

### TODO V2.1:  make this a standalone script used in DB seeding!
def seed_milky_way_from_json():
    """
    This is a PITA and another example of how "pure" coding/data
    results in a LOT of unnecessary grunt work.
    The data can be modeled with 4 things: contour, segement, ra, and dec.
    """
    with open('data/milky_way/mw.json') as f:
        raw = json.load(f)
        clear_database_table()
        pk = 1

        # Iteration 1
        contours = raw['features'] # there are 5 - this is a LIST
        for contour in contours: # this is a DICT
            # Iteration 2 - keys = type, id, properties, and geometry
            contour_id = int(contour['id'].strip('ol'))
            segment_id = 1
            # iteration 3 - this ia list but it always has length 1
            segments = contour['geometry']['coordinates'][0]
            # iteration 4 - these lists are the segments (10, 113, 46, 27, 6) in each contour
            for segment in segments:
                # iteration 5 - FINALLY - a list of coordinates!
                #print(f"C: {contour_id} S: {segment_id} COORDS: {len(segment)}")
                for coord in segment:
                    rec = MilkyWay()
                    rec.pk = pk
                    rec.contour = contour_id
                    rec.segment = segment_id
                    rec.longitude = coord[0]
                    rec.ra = (rec.longitude % 360.) / 15.
                    rec.dec = coord[1]
                    rec.save()
                    pk += 1
                segment_id += 1
    return MilkyWay.objects.count()