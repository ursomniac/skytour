from skytour.apps.observe.models import ObservingLocation

def run_location(loc):
    state = loc.state.abbreviation
    loc.region = f"{state}, USA"
    loc.save()

def run_all():
    locs = ObservingLocation.objects.all()
    for loc in locs:
        run_location(loc)