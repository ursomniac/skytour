from django.db.models.functions import Cast
from django.db.models import Count, IntegerField
from itertools import chain, takewhile
from operator import attrgetter
from .models import Catalog
from ..dso.models import DSO, DSOAlias

def assemble_catalog(catalog_slug, raw=None):
    catalog_abbr = Catalog.objects.get(slug=catalog_slug).abbreviation
    # 1. get all objects with a primary ID
    if raw is None:
        native = DSO.objects.filter(catalog__slug=catalog_slug)
        native = native.annotate(cid=Cast('id_in_catalog', IntegerField())).order_by('cid', 'id_in_catalog')
        for x in native:
            x.cat_id = f"{catalog_abbr} {x.cid}"
    else:
        native = raw
    # 2. get all objects with an Alias in a catalog
    aliases = DSOAlias.objects.filter(catalog__slug=catalog_slug)
    # 2a. remove all aliases in the same catalog (e.g., multiple NGC numbers for one object)
    aliases = aliases.exclude(object__catalog__slug=catalog_slug)
    aliases = aliases.annotate(cid=Cast('id_in_catalog', IntegerField())).order_by('cid', 'id_in_catalog')
    # 2a. replace the list with the DSOs themselves
    alias_dsos = [x.object for x in aliases]
    # 2b. add "back" the cid to the alias_dsos
    for i in range(len(alias_dsos)):
        alias_dsos[i].cid = aliases[i].cid
        alias_dsos[i].cat_id = f"{catalog_abbr} {alias_dsos[i].cid}"
    # 3. combine the two with chain, and sort on cid
    dso_list = sorted(chain(native, alias_dsos), key=attrgetter('cid'))

    # views.py 128- might be better since it handled string and int...?
    return dso_list

# Missing H400
#  42 = NGC 1052 (NGC 1042)
# 141 = NGC 3166 (NGC 3169)
# 145 = NGC 3193 (NGC 3190)
# 157 = NGC 3384 (M 105)
# 171 = NGC 3613 (NGC 3619)
# 181 = NGC 3686 (NGC 3681)
# 183 = NGC 3729 (NGC 3718)
# 197 = NGC 3982 (NGC 3972)
# 199 = NGC 3998 (NGC 3972)
# 203 = NGC 4036 (NGC 4041)
# 207 = NGC 4085 (NGC 4088)
# 235 = NGC 4394 (M 85)
# 246 = NGC 4473 (NGC 4477)
# 248 = NGC 4478 (M 87)
# 249 = NGC 4485 (NGC 4490)
# 271 = NGC 4665 (alias to NGC 4664)
# 279 = NGC 4754 (NGC 4762)
# 296 = NGC 5363 (NGC 5364)
# 340 = NGC 6528 (NGC 6522)