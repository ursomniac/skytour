from .models import DSOWiki, DSOInFieldWiki
from ..abstract.wiki import get_wiki_page, get_page_attrs
from ..abstract.vocabs import YES, NO
from ..solar_system.wiki import update_wiki_object

def update_dso_wiki(instance):
    WIKIMODEL = {
        'DSO': DSOWiki,
        'DSOInField': DSOInFieldWiki,
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

