from skyfield.api import Star
from .models import MilkyWay

def get_list_of_segments(contour=1):
     """
     Get the list of segments for the Milky Way at a particular contour level.
     (There are 5; Skymap only looks at level=1, but AtlasPlate uses levels 1 and 2.)
     """
     points = MilkyWay.objects.filter(contour=contour)
     segment_ids = set(points.values_list('segment', flat=True))
     list_of_coords = []
     for sid in segment_ids:
          segment = []
          coords = points.filter(segment=sid).order_by('pk').values_list('ra', 'dec')
          for c in coords:
               segment.append(c)
          list_of_coords.append(segment)
     return list_of_coords
