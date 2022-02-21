import math
from skyfield.api import load
from skyfield.constants import GM_SUN_Pitjeva_2005_km3_s2 as GM_SUN
from skyfield.data import mpc
from ..observe.almanac import get_object_rise_set
from ..observe.local import get_observing_situation
from ..utils.compile import observe_to_values
from ..utils.format import to_sex
from .utils import get_angular_size, get_constellation

def get_asteroid_target(asteroid, ts, sun):
   with load.open('bright_asteroids.txt') as f:
      mps = mpc.load_mpcorb_dataframe(f)
   mps = mps.set_index('designation', drop=False)
   try:
      row = mps.loc[asteroid.mpc_lookup_designation]
      target = sun + mpc.mpcorb_orbit(row, ts, GM_SUN)
   except:
      return None
   return target