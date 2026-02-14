from .models import DSOWiki, DSOInFieldWiki
from ..abstract.wiki import update_wiki_object

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

def format_wiki_text(instance):
    text = instance.summary
    html_output = "".join(f"<p>{line.strip()}</p>\n" for line in text.strip().splitlines())
    return html_output
