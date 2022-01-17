from .models import (
    SiteParameterSwitch,
    SiteParameterLink,
    SiteParameterPositiveInteger,
    SiteParameterNumber,
    SiteParameterString,
    SiteParameterImage,
)

# This is just a dict of models with keys.
PARAM_TYPES = {
    'link': SiteParameterLink,
    'number': SiteParameterNumber, 
    'text': SiteParameterString,
    'positive': SiteParameterPositiveInteger,
    'string': SiteParameterString, 
    'image': SiteParameterImage
}

def find_site_parameter(slug=None, default=None, param_type=None):
    """
    Look up a site parameter by type and slug.
    If no type is given, all of them are searched.

    If the queryset is empty, then return the default value provided.

    Isn't that neat?
    """
    if not slug:    # why did you call me when you have nothing to say?
        return None
    if param_type:    # faster
        try:
            item = PARAM_TYPES[param_type].objects.get(slug=slug)
            return item.value
        except Exception:
            return default
    else:    # slower
        for k in PARAM_TYPES.keys():
            try:
                item = PARAM_TYPES[param_type].objects.get(slug=slug)
                return item.value
            except Exception:
                pass    # try again
    # I couldn't find anything - sorry.
    return default
