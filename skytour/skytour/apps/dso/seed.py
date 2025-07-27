import json
from ..abstract.vocabs import YES, NO
from ..abstract.wiki import get_wiki_page, get_page_attrs
from .models import MilkyWay, DSOWiki, DSOInFieldWiki, DSO, DSOInField

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

def seed_dso_wiki(model, idlist=None, debug=False):
    OBJECT_MODELS = {'DSO': DSO, 'DSOInField': DSOInField}
    WIKI_MODELS = {'DSO': DSOWiki, 'DSOInField': DSOInFieldWiki}
    if model in WIKI_MODELS.keys():
        wiki_model = WIKI_MODELS[model]
        obj_model = OBJECT_MODELS[model]
    else:
        return None
    
    if idlist is not None:
        objects = obj_model.objects.filter(pk__in=idlist)
    else:
        objects = obj_model.objects.all()

    for o in objects:
        if o.has_wiki == 'NOINSTANCE':
            w = wiki_model()
            search = o.default_wikipedia_name
            w.object_id = o.pk
        else:
            w = o.wiki
            search = o.default_wikipedia_name if w.override_lookup is None else w.override_lookup
        wiki = get_wiki_page(search)
        attr = get_page_attrs(wiki)
        w.exists = YES if attr['exists'] else NO
        w.ambiguous = YES if attr['ambiguous'] else NO

        if attr['exists']:
            w.title = attr['title']
            if not attr['ambiguous']:
                w.summary = attr['summary']
                w.summary_length = attr['summary_length']
                w.canonical_url = attr['canonical_url']
        w.save()

        if debug:
            print(f"{o.pk} = {search}: E{w.exists} A{w.ambiguous} SL:{w.summary_length} URL:{w.canonical_url}")

def fix_wiki_page(model_name, pk, text, update=True):
    model = DSO if model_name == 'DSO' else DSOInField
    obj = model.objects.get(pk=pk)
    if not hasattr(obj, 'wiki'):
        print ("Need to create wiki entry - aborting")
        return None
    wiki = obj.wiki
    wiki.override_lookup = text
    wiki.save()

    if update:
        page = get_wiki_page(text)
        attr = get_page_attrs(page)
        wiki.exists = YES if attr['exists'] else NO
        wiki.ambiguous = YES if attr['ambiguous'] else NO

        if attr['exists']:
            wiki.title = attr['title']
            if not attr['ambiguous']:
                wiki.summary = attr['summary']
                wiki.summary_length = attr['summary_length']
                wiki.canonical_url = attr['canonical_url']
        wiki.save()
    return wiki