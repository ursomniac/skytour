from skytour.apps.dso.scrape.simbad import norm_distance
from skytour.apps.dso.models import DSO

def run_all(debug=True, test=True):
    dsos = DSO.objects.all()

    for dso in dsos:
        try:
            raw = dso.simbad['raw_values']
            raw_dist = raw['Distance_distance'][0]
            dist = dso.simbad['values']['distance']['value']
            if dist <= 0.0 and raw_dist != 0.0:
                raw_dist_units = raw['Distance_unit'][0]
                new_dist, new_units = norm_distance(raw_dist, raw_dist_units)
                if debug:
                    print(f"Fixing {dso}: {dist} {raw_dist_units} --> {new_dist} {new_units}")
                if not test:
                    dso.simbad['values']['distance'] = {
                        'value': new_dist,
                        'units': new_units
                    }
                    dso.save()
            # otherwise leave alone
        except:
            continue
