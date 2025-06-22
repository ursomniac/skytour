from ..site.utils import get_skytour_version
import wikipediaapi

def get_user_agent():
    version = get_skytour_version()
    return f"Skytour/{version}"

wiki = wikipediaapi.Wikipedia(user_agent=get_user_agent(), language='en')

def get_wiki_page(name):
    return wiki.page(name)

def does_page_exist(page):
    return page.exists()

def is_page_ambiguous(page):
     return "Category:All disambiguation pages" in page.categories.keys()

def get_page_attrs(page):
    return dict(
        title = page.title,
        exists = does_page_exist(page),
        ambiguous = is_page_ambiguous(page),
        summary = page.summary,
        summary_length = len(page.summary),
        canonical_url = page.canonicalurl
    )

def test():
    pages = [
        'Messier 1',  # Messier object
        'NGC 6543',   # NGC object
        '135 Hertha', # Asteroid
        'Cygnus',     # Constellation
        '10P/Tempel', # Comet
        'Neptune'     # Planet
    ]
    for item in pages:
        page = get_wiki_page(item)
        x = get_page_attrs(page)
        print(f"{x['title']:20s}: {str(x['exists']):5s} {x['summary_length']:5d} chars, {str(x['ambiguous']):5s} {x['canonical_url']}")


