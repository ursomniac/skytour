from .models import PlanetWiki, CometWiki, AsteroidWiki, MeteorShowerWiki
from ..abstract.wiki import get_wiki_page, get_page_attrs
from ..abstract.vocabs import YES, NO

def update_wiki_object(obj, name):
    page = get_wiki_page(name)
    attr = get_page_attrs(page)
    obj.exists = YES if attr['exists'] else NO
    obj.ambiguous = YES if attr['ambiguous'] else NO

    if attr['exists']:
        obj.title = attr['title']
        if not attr['ambiguous']:
            obj.summary = attr['summary']
            obj.summary_length = attr['summary_length']
            obj.canonical_url = attr['canonical_url']
    obj.save()
    return obj

def update_solar_system_wiki(instance):
    WIKIMODEL = {
        'Planet': PlanetWiki,
        'Asteroid': AsteroidWiki,
        'Comet': CometWiki,
        'MeteorShower': MeteorShowerWiki
    }
    parent_model = instance._meta.model.__name__
    if parent_model not in WIKIMODEL.keys():
        return None
    else:
        wiki_model = WIKIMODEL[parent_model]
    if hasattr(instance, 'wiki'): # exists
        wiki = instance.wiki
    else:
        wiki = wiki_model() # Create new instance
        wiki.object = instance
        wiki.override_lookup = None
    wiki = update_wiki_object(wiki, instance.default_wikipedia_name)
    return wiki

