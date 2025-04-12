import math
from skyfield.api import load
from skyfield.constants import GM_SUN_Pitjeva_2005_km3_s2 as GM_SUN
from skyfield.data import mpc

def get_asteroid_target(asteroid, ts, sun):
   """
   Get target from the asteroid.mpc_object
   """
   #with load.open('generated_data/bright_asteroids.txt') as f:
   #   mps = mpc.load_mpcorb_dataframe(f)
   #mps = mps.set_index('designation', drop=False)
   try:
      #row = mps.loc[asteroid.mpc_lookup_designation]
      row = asteroid.mpc_object
      target = sun + mpc.mpcorb_orbit(row, ts, GM_SUN)
   except:
      return None
   return target

def lookup_asteroid_object(name):
   """
   This is VERY VERY slow.
   TODO: find SOME way to optimize this
   """
   with load.open('data/MPCORB.DAT') as f:
      mps = mpc.load_mpcorb_dataframe(f)
   mps = mps.set_index('designation', drop=False)
   try:
      row = mps.loc[name]
   except:
      return None   
   return row

def get_asteroid_object(asteroid):
   """
   Lookup an asteroid in bright_asteroids.txt and return it as a target.
   TODO: Deprecate!  
   """
   with load.open('generated_data/bright_asteroids.txt') as f:
      mps = mpc.load_mpcorb_dataframe(f)
   mps = mps.set_index('designation', drop=False)
   try:
      row = mps.loc[asteroid.mpc_lookup_designation]
   except:
      return None
   return row

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
      if asteroid.mag_g and asteroid.mag_h:
         m1 = asteroid.mag_h + 5 * math.log10(r_sun_target * r_earth_target) 
         m2 = 2.5 * math.log10((1 - asteroid.mag_g) * phi_1 + asteroid.mag_g * phi_2)
         mag = m1 - m2
   
   return mag

def create_asteroid_dict(mpc):
   """
   Sample mpc data:
      designation_packed                            00102 str
      magnitude_H                                    9.47 float
      magnitude_G                                    0.15 float
      epoch_packed                                  K2555 str
      mean_anomaly_degrees                       29.93000 float
      argument_of_perihelion_degrees            147.35374 float
      longitude_of_ascending_node_degrees       210.76235 float
      inclination_degrees                         5.17409 float
      eccentricity                              0.2508431 float
      mean_daily_motion_degrees                0.22687954 float
      semimajor_axis_au                         2.6623950 float
      uncertainty                                       0 +int
      reference                                 MPO901162 +str
      observations                                   7133 int
      oppositions                                      66 int
      observation_period                        1870-2025 str
      rms_residual_arcseconds                        0.60 +float
      coarse_perturbers                               M-v +str
      precise_perturbers                              3Ek +str
      computer_name                              MPCLINUX +str
      hex_flags                                      0000 +str
      designation                            (102) Miriam str
      last_observation_date                    20250119.0 float
   """
   STRING_FIELDS = [
      'designation_packed', 'observation_period', 'designation', 'epoch_packed'
   ]
   FLOAT_FIELDS = [
      'magnitude_H', 'magnitude_G', 'mean_anomaly_degrees',
      'argument_of_perihelion_degrees', 'eccentricity',
      'longitude_of_ascending_node_degrees',
      'inclination_degrees', 'mean_daily_motion_degrees',
      'semimajor_axis_au', 'last_observation_date'
   ]
   INT_FIELDS = ['observations', 'oppositions']
   out = {}
   for key in mpc.index:
      if key in STRING_FIELDS:
         out[key] = mpc[key]
      elif key in FLOAT_FIELDS:
         out[key] = float(mpc[key])
      elif key in INT_FIELDS:
         out[key] = int(mpc[key])
      else: # not interested
         pass
   return out


