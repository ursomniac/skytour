import math
from skyfield.api import load
from skyfield.constants import GM_SUN_Pitjeva_2005_km3_s2 as GM_SUN
from skyfield.data import mpc

def get_asteroid(utdt, asteroid):
   ts = load.timescale()
   eph = load('de421.bsp')
   sun, earth = eph['sun'], eph['earth']
   t = ts.utc(utdt.year, month=utdt.month, day=utdt.day, hour=utdt.hour, minute=utdt.minute, second=utdt.second)
   with load.open('bright_asteroids.txt') as f:
      mps = mpc.load_mpcorb_dataframe(f)
   mps = mps.set_index('designation', drop=False)
   row = mps.loc[asteroid.mpc_lookup_designation]
   target = sun + mpc.mpcorb_orbit(row, ts, GM_SUN)
   observe = earth.at(t).observe(target)
   # Get all the distances (earth-asteroid, earth-sun, sun-asteroid)
   # None of this is needed once there's a method for getting phase_angle.
   earth_sun = earth.at(t).observe(sun)
   sun_asteroid = sun.at(t).observe(target)
   _, _, xr = sun_asteroid.ecliptic_latlon()
   r = xr.au.item()
   _, _, xrr = earth_sun.radec()
   rr = xrr.au.item()
   xra, xdec, xdelta = observe.radec()
   ra = xra.hours.item()
   dec = xdec.hours.item()
   delta = xdelta.au.item()
   #
   # Phase angle is needed for calculating magnitude,
   # It APPEARS that this is in v1.42 of Skyfield, as-yet not released.
   #
   # for now:
   cos_beta = (r*r + delta*delta - rr*rr) / (2. * r * delta)
   phase_angle = math.acos(cos_beta) # RADIANS

   phi_1 = math.exp(-3.33 * math.tan(phase_angle/2.)**0.63)
   phi_2 = math.exp(-1.87 * math.tan(phase_angle/2.)**1.22)
   m1 = asteroid.h + 5 * math.log10(r * delta)
   m2 = -2.5 * math.log10((1 - asteroid.g) * phi_1 + asteroid.g * phi_2)
   magnitude = m1 - m2

   return dict(
      observe = observe,
      magnitude = magnitude,
      phase_angle = math.degrees(phase_angle),
      coords = dict(ra=ra, dec=dec, distance=delta)
   )


"""
MINOR PLANET CENTER ORBIT DATABASE (MPCORB)

This file contains published orbital elements for all numbered and unnumbered
multi-opposition minor planets for which it is possible to make reasonable
predictions.  It also includes published elements for recent one-opposition
minor planets and is intended to be complete through the last issued Daily
Orbit Update MPEC.  As such it is intended to be of interest primarily
to astrometric observers.

   Software programs may include this datafile amongst their datasets, as
   long as this header is included (it is acceptable if it is contained
   in a file separate from the actual data) and that proper attribution
   to the Minor Planet Center is given.  Credit to the individual orbit
   computers is implicit by the inclusion of a reference and the name of
   the orbit computer on each orbit record.  Information on how to obtain
   updated copies of the datafile must also be included.

   The work of the individual astrometric observers, without whom none of
   the work of the Minor Planet Center would be possible, is gratefully
   acknowledged.  Credit to the individual observers is implicit by the
   inclusion of the reference to the publication of their observations in
   all data sets distributed by the Minor Planet Center.

New versions of this file, updated on a daily basis, will be available at:

          https://www.minorplanetcenter.org/iau/MPCORB/MPCORB.DAT

The elements contained within MPCORB are divided into three sections,
separated by blank lines.  The first section contains the numbered objects,
the second section contains the unnumbered objects with perturbed orbit
solutions and the third contains the recent 1-opposition objects with
unperturbed orbit solutions.  Each object's elements are stored on a single
line, the format of which is described at:

          http://www.minorplanetcenter.org/iau/info/MPOrbitFormat.html

If you find a problem with any data herein, please contact mpc@cfa.harvard.edu.

A brief header is given below:

Des'n     H     G   Epoch     M        Peri.      Node       Incl.       e            n           a        Reference #Obs #Opp    Arc    rms  Perts   Computer

----------------------------------------------------------------------------------------------------------------------------------------------------------------
"""