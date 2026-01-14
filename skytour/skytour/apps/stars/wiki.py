from ..abstract.wiki import get_wiki_page, get_page_attrs
from ..abstract.vocabs import YES, NO
from .models import VariableStarWiki, BrightStarWiki, StellarObjectWiki

def check_categories(cdict):
    """
    Stupid test because searching on something like "HR 1" might come
    back with something that's not a star...
    PRESUMABLY all pages about stars are in categories about stars...
    """
    try:
        for k in cdict.keys():
            if 'star' in k.lower():
                return True
    except:
        return False
    return False

def run_wiki_object(name):
    """
    For a given search term (name)
    """
    fail = {'exists': None, 'is_star': None, 'ambiguous': None, 'on_group_page': None, 'works': False }

    if name is None: # If the name is None return an empty dict
        return fail
    try:
        page = get_wiki_page(name)
        attr = get_page_attrs(page)
    except:
        try:
            page = get_wiki_page(name)
            attr = get_page_attrs(page)
        except:
            return fail
    # Set the flags that determine success
    attr['is_star'] = check_categories(page.categories)
    attr['ambiguous'] = is_ambiguous(attr) == YES
    attr['on_group_page'] = test_if_on_group_page(attr)
    return attr

def test_if_on_group_page(attr):
    """
    Look for "List_of_stars" in the URL
    """
    if attr['canonical_url'] is not None:
        return 'List_of_stars' in attr['canonical_url']
    return False

def is_ambiguous(attr):
    """
    If the search term comes up with a "page of pages" 
    or for a star on a page of "List of stars in..."
    then this is ambiguous and we don't want it...
    """
    if attr['ambiguous']:
        return YES
    return YES if test_if_on_group_page(attr) else NO

def is_valid(t):
    """
    conditions:
        exists:        True  = page exists
        ambiguous:     False = page found is a single page for an object
        on_group_page: False = star not on a page of "List of stars in..."
        is_star:       True  = categories for the page mention "star" somewhere
        works:         True  = all metadata needed are present
    """
    success = (True, False, False, True, True)
    result = (t['exists'], t['ambiguous'], t['on_group_page'], t['is_star'], t['works'])
    return success == result

def process_bright_star(star, sep=' ', verbose=False):
    """
    Look up a star and see if you can find a page.
    Return an object with success or nothing if this fails.
    """
    if verbose:
        print("Running ", star)
    attempts = [
        (star.wiki.override_lookup, 'Override'),
        (star.default_wikipedia_star_name, "Name"),
        (f"HR{sep}{star.hr_id}", 'HR'),
        (f"HD{sep}{star.hd_id}", 'HD'),
        #(f"HD {star.hd_id}_(star)", 'HD (star)')
    ]
    for attempt in attempts: # loop through altername names until the first success
        if attempt[0] is None:
            continue # skip
        if verbose:
            print(f"\t attempting {attempt[0]}")
        t = run_wiki_object(attempt[0]) # These are the attributes and flags
        if is_valid(t): # check if the flags are what we need
            return (star, attempt[0], attempt[1], t)
    return (star, None, None, None) # Not found - oh well

def save_wiki_object(wiki, worked, result):
    wiki.exists = result['exists']
    wiki.ambiguous = result['ambiguous']
    wiki.override_lookup = worked
    wiki.title = result['title']
    wiki.summary = result['summary']
    wiki.summary_length = result['summary_length']
    wiki.canonical_url = result['canonical_url']
    wiki.save()
    return wiki

def update_bright_star_wiki(star, skip=False, save=True, verbose=False):
    if skip and star.has_wiki == 'WIKI':
        return None, 'skipped'
    if hasattr(star, 'wiki'):
        wiki = star.wiki
    else:
        # there's a cool way to do this that I just did for variable stars
        wiki = BrightStarWiki.objects.create(object=star)
    star, worked, how, result = process_bright_star(star, verbose=verbose)
    if how is not None: # it worked!
        if save:
            wiki = save_wiki_object(wiki, worked, result)
    return wiki, how
        
### THIS WILL NEED TO BE RE-WRITTEN for VariableStar and StellarObject
def update_star_wiki(instance):
    # REDO - untested for VariableStar and StellarObject
    # won't work for BrightStar
    wiki = None
    WIKIMODEL = {
        'VariableStar': VariableStarWiki,
        'BrightStar': BrightStarWiki,
        'StellarObject': StellarObjectWiki
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
    #wiki = update_wiki_object(wiki, instance.default_wikipedia_name)
    return wiki

