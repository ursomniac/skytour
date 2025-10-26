from skytour.apps.dso.models import DSO
from skytour.apps.solar_system.models import Planet, Asteroid, Comet, MeteorShower

def access_object(reftype, ref):
    if reftype == 'DSO':
        return DSO.objects.filter(shown_name=ref).first() # send None if not found
    elif reftype == 'Planet':
        return Planet.objects.filter(name=ref).first()
    elif reftype == 'Asteroid':
        things = ref.split(' ')
        ast = things[0] if len(things) == 1 else things[1]
        return Asteroid.objects.filter(name=ast).first()
    elif reftype == 'Comet':
        return Comet.objects.filter(name__contains=ref).first()
    elif reftype == 'MeteorShower':
        return MeteorShower.filter(slug__contains=ref).first()
    return None