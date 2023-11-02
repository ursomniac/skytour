import math
from skyfield.api import load
from skyfield.constants import GM_SUN_Pitjeva_2005_km3_s2 as GM_SUN
from skyfield.data import mpc

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

def fast_asteroid(asteroid, eph, t, earth, sun, r_earth_sun):
   """
   Trying to get a fast estimate of magnitude for filtering.
   """
   # Earth to asteroid
   target = earth.at(t).observe(eph).apparent()
   r_earth_target = target.radec()[2].au.item()
   # Sun to asteroid
   sun_target = sun.at(t).observe(eph)
   r_sun_target = sun_target.radec()[2].au.item()

   # Phase angle
   cos_beta = (r_sun_target**2 + r_earth_target**2 - r_earth_sun**2)/(2. * r_sun_target * r_earth_target)
   if cos_beta > 1.:
      phase_angle = None
   else:
      phase_angle = math.acos(cos_beta) # RADIANS
   
   # Magnitude
   mag = None
   # This is apparently in Skyfield v1.42 as-yet not released.
   if phase_angle:
      rpa = math.radians(phase_angle) # Assuming this is the same phase angle
      phi_1 = math.exp(-3.33 * math.tan(rpa/2.)**0.63)
      phi_2 = math.exp(-1.87 * math.tan(rpa/2.)**1.22)
      m1 = asteroid.h + 5 * math.log10(r_sun_target * r_earth_target) 
      m2 = 2.5 * math.log10((1 - asteroid.g) * phi_1 + asteroid.g * phi_2)
      mag = m1 - m2
   
   return mag