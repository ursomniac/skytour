
def create_shown_name(obj):
    """
    This takes the main name, or if there's a Bayer/Flamsteed designation, 
    assemble a string from that.
    """
    things = []
    if obj.catalog.name in ['Bayer', 'Flamsteed']:
            try:
                return "{} {}".format(obj.id_in_catalog, obj.object.constellation.abbreviation)
            except:
                pass
    if obj.catalog.use_abbr:
        things.append(obj.catalog.abbreviation)
        things.append(obj.id_in_catalog)
    else:
        things.append(obj.id_in_catalog)
        things.append(obj.constellation.abbreviation)
    return ' '.join(things)
