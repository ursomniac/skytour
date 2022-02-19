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
   row = mps.loc[asteroid.mpc_lookup_designation]
   target = sun + mpc.mpcorb_orbit(row, ts, GM_SUN)
   return target

def get_asteroid(utdt, asteroid, utdt_end=None, location=None, serialize=False):
   ts = load.timescale()
   eph = load('de421.bsp')
   sun, earth = eph['sun'], eph['earth']
   t = ts.utc(utdt.year, month=utdt.month, day=utdt.day, hour=utdt.hour, minute=utdt.minute, second=utdt.second)
   #with load.open('bright_asteroids.txt') as f:
   #   mps = mpc.load_mpcorb_dataframe(f)
   #mps = mps.set_index('designation', drop=False)
   #row = mps.loc[asteroid.mpc_lookup_designation]
   #target = sun + mpc.mpcorb_orbit(row, ts, GM_SUN)
   target = get_asteroid_target(asteroid, ts, sun)
   
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
   m2 = 2.5 * math.log10((1 - asteroid.g) * phi_1 + asteroid.g * phi_2)
   magnitude = m1 - m2

   # Elongation
   cos_psi = (rr*rr + delta*delta - r*r)/(2. * r * delta)
   psi = math.degrees(math.acos(cos_psi))

   # Get what constellation this is in
   constellation = get_constellation(xra.hours.item(), xdec.degrees.item())
   # If location is provided, get the almanac dict
   almanac = get_object_rise_set(utdt, eph, target, location) if location else None
   # if location AND utdt_end are provided, get the session dict
   session = get_observing_situation(observe, utdt, utdt_end, location) if utdt_end and location else None

   ang_size = get_angular_size(asteroid.mean_diameter, xdelta.km.item())

   return_dict = dict(
      name = "{} {}".format(asteroid.number, asteroid.name),
      slug = asteroid.slug,
      coords = observe_to_values(observe),
      observe = dict(
         constellation=constellation,
         illum_fraction=None,
         apparent_mag = magnitude,
         angular_diameter = ang_size,
         angular_diameter_str = to_sex(ang_size/3600., format="degrees"),
         phase_angle = math.degrees(phase_angle),
         phase_angle_str = to_sex(math.degrees(phase_angle), format="degrees"),
         elongation = psi, 
      ),
      physical = None,
      close_to = None, # Do this?
      almanac = almanac,
      session = session,
      moons = None, # N/A
      # keeping these here for now, might delete later
      sun_distance = r,
      earth_sun_distance  = rr
   )
   if not serialize:
      return_dict['object'] = asteroid
      return_dict['target'] = observe
   return return_dict
   

      

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

"""                         Mag  q-1.017     q        H       a       e
y        1 Ceres       :   6.50   1.5319   2.5489    3.5   2.7660  0.0785
y        2 Pallas      :   6.11   1.1168   2.1338    4.2   2.7711  0.2300
y        3 Juno        :   6.69   0.9662   1.9832    5.3   2.6688  0.2569
y        4 Vesta       :   5.34   1.1359   2.1529    3.4   2.3613  0.0882
y        5 Astraea     :   8.73   1.0686   2.0856    7.0   2.5752  0.1901
y        6 Hebe        :   6.89   0.9161   1.9331    5.7   2.4257  0.2031
y        7 Iris        :   6.51   0.8219   1.8389    5.6   2.3866  0.2295
y        8 Flora       :   7.51   0.8411   1.8581    6.5   2.2017  0.1561
y        9 Metis       :   8.13   1.0736   2.0906    6.4   2.3853  0.1236
y       10 Hygiea      :   9.02   1.7742   2.7912    5.5   3.1419  0.1116
y       11 Parthenope  :   8.70   1.1921   2.2091    6.6   2.4533  0.0995
y       12 Victoria    :   8.13   0.8016   1.8186    7.3   2.3338  0.2207
y       13 Egeria      :   9.34   1.3394   2.3564    6.8   2.5766  0.0854
y       14 Irene       :   8.48   1.1400   2.1570    6.5   2.5859  0.1659
y       15 Eunomia     :   7.35   1.1336   2.1506    5.4   2.6441  0.1866
y       16 Psyche      :   8.98   1.5158   2.5328    6.1   2.9245  0.1339
y       17 Thetis      :   9.67   1.1254   2.1424    7.8   2.4706  0.1329
y       18 Melpomene   :   7.26   0.7785   1.7955    6.5   2.2958  0.2179
y       19 Fortuna     :   9.04   1.0423   2.0593    7.4   2.4429  0.1570
y       20 Massalia    :   8.23   1.0472   2.0642    6.6   2.4088  0.1431
y       21 Lutetia     :   9.11   1.0199   2.0369    7.5   2.4352  0.1635
y       22 Kalliope    :   9.63   1.6069   2.6239    6.5   2.9102  0.0984
y       23 Thalia      :   8.68   1.0010   2.0180    7.2   2.6300  0.2327
.       24 Themis      :  10.66   1.7408   2.7578    7.2   3.1424  0.1224
.       25 Phocaea     :   8.54   0.7706   1.7876    7.8   2.3994  0.2550
y       26 Proserpina  :  10.14   1.4007   2.4177    7.5   2.6550  0.0894
y       27 Euterpe     :   8.36   0.9270   1.9440    7.1   2.3481  0.1721
.       28 Bellona     :   9.73   1.3372   2.3542    7.2   2.7747  0.1515
y       29 Amphitrite  :   8.57   1.3497   2.3667    6.0   2.5542  0.0734
y       30 Urania      :   9.23   1.0468   2.0638    7.6   2.3660  0.1277
y       31 Euphrosyne  :   9.65   1.4576   2.4746    6.9   3.1641  0.2179
y       32 Pomona      :  10.20   1.3590   2.3760    7.7   2.5873  0.0817
.       33 Polyhymnia  :   9.72   0.9041   1.9211    8.5   2.8746  0.3317
.       36 Atalante    :   9.77   0.8904   1.9074    8.6   2.7467  0.3056
y       37 Fides       :   9.40   1.1596   2.1766    7.4   2.6410  0.1759
.       38 Leda        :  10.97   1.3055   2.3225    8.6   2.7424  0.1531
y       39 Laetitia    :   8.82   1.4435   2.4605    6.1   2.7701  0.1117
y       40 Harmonia    :   9.14   1.1446   2.1616    7.2   2.2669  0.0465
y       41 Daphne      :   8.92   0.9861   2.0031    7.4   2.7613  0.2746
y       42 Isis        :   8.70   0.8810   1.8980    7.6   2.4419  0.2227
y       43 Ariadne     :   8.90   0.8141   1.8311    8.0   2.2031  0.1688
y       44 Nysa        :   8.61   1.0451   2.0621    6.9   2.4228  0.1489
y       45 Eugenia     :  10.45   1.4764   2.4934    7.6   2.7208  0.0836
y       46 Hestia      :  10.29   1.0718   2.0888    8.5   2.5251  0.1728
.       48 Doris       :  10.84   1.8782   2.8952    7.2   3.1152  0.0706
.       49 Pales       :  10.49   1.3948   2.4118    7.9   3.0981  0.2215
.       50 Virginia    :  10.44   0.8772   1.8942    9.3   2.6500  0.2852
y       51 Nemausa     :   9.68   1.1888   2.2058    7.6   2.3657  0.0676
y       52 Europa      :   9.88   1.7354   2.7524    6.5   3.0953  0.1108
.       53 Kalypso     :  10.65   1.0718   2.0888    8.9   2.6193  0.2025
.       54 Alexandra   :   9.84   1.1606   2.1776    7.8   2.7119  0.1970
.       55 Pandora     :  10.37   1.3453   2.3623    7.9   2.7592  0.1438
.       56 Melete      :   9.91   0.9611   1.9781    8.5   2.5959  0.2380
.       57 Mnemosyne   :  10.51   1.7932   2.8102    7.0   3.1571  0.1099
.       59 Elpis       :  10.62   1.3775   2.3945    8.0   2.7126  0.1173
.       60 Echo        :   9.83   0.9323   1.9493    8.5   2.3919  0.1850
.       61 Danae       :  10.49   1.4757   2.4927    7.7   2.9844  0.1648
y       63 Ausonia     :   9.22   1.0735   2.0905    7.5   2.3958  0.1274
.       64 Angelina    :  10.16   1.3276   2.3446    7.7   2.6814  0.1256
.       65 Cybele      :  10.84   2.0245   3.0415    6.9   3.4333  0.1141
.       67 Asia        :   9.75   0.9576   1.9746    8.4   2.4222  0.1848
y       68 Leto        :   9.27   1.2512   2.2682    7.0   2.7830  0.1850
.       69 Hesperia    :   9.97   1.4517   2.4687    7.2   2.9750  0.1702
y       70 Panopaea    :  10.07   1.1261   2.1431    8.2   2.6153  0.1806
.       71 Niobe       :   9.43   1.2581   2.2751    7.2   2.7574  0.1749
.       72 Feronia     :  10.54   0.9759   1.9929    9.1   2.2660  0.1205
.       74 Galatea     :  10.62   1.1079   2.1249    8.8   2.7817  0.2361
.       75 Eurydike    :  10.06   0.8458   1.8628    9.1   2.6749  0.3036
.       78 Diana       :  10.11   1.0650   2.0820    8.4   2.6215  0.2058
.       79 Eurynome    :   9.39   0.9628   1.9798    8.0   2.4452  0.1903
y       80 Sappho      :   8.97   0.8189   1.8359    8.1   2.2956  0.2002
.       81 Terpsichore :  10.86   1.2320   2.2490    8.7   2.8520  0.2114
.       82 Alkmene     :  10.23   1.1377   2.1547    8.3   2.7641  0.2205
.       83 Beatrix     :  10.95   1.2189   2.2359    8.8   2.4336  0.0812
.       84 Klio        :  10.14   0.7867   1.8037    9.4   2.3622  0.2364
.       85 Io          :   9.66   1.1201   2.1371    7.8   2.6522  0.1942
y       88 Thisbe      :   9.68   1.3043   2.3213    7.3   2.7695  0.1618
y       89 Julia       :   8.48   1.0621   2.0791    6.8   2.5502  0.1847
.       92 Undina      :  10.38   1.8360   2.8530    6.8   3.1912  0.1060
.       93 Minerva     :  10.46   1.3552   2.3722    7.9   2.7549  0.1389
.       96 Aegle       :  10.86   1.6012   2.6182    7.8   3.0492  0.1414
.       97 Klotho      :   9.22   0.9632   1.9802    7.8   2.6676  0.2577
.       98 Ianthe      :  10.93   1.1670   2.1840    8.9   2.6878  0.1875
.      100 Hekate      :  10.66   1.5484   2.5654    7.7   3.0874  0.1691
.      101 Helena      :  10.36   1.2020   2.2190    8.2   2.5838  0.1412
.      102 Miriam      :  10.83   0.9775   1.9945    9.4   2.6630  0.2511
.      103 Hera        :  10.44   1.4718   2.4888    7.6   2.7029  0.0792
.      105 Artemis     :  10.09   0.9358   1.9528    8.8   2.3744  0.1776
.      106 Dione       :  10.84   1.6561   2.6731    7.6   3.1795  0.1593
.      109 Felicitas   :  10.14   0.8707   1.8877    9.1   2.6949  0.2995
.      110 Lydia       :  10.73   1.4955   2.5125    7.9   2.7316  0.0802
.      111 Ate         :  10.61   1.3100   2.3270    8.2   2.5928  0.1025
.      113 Amalthea    :  10.51   1.1539   2.1709    8.5   2.3757  0.0862
.      114 Kassandra   :  10.69   1.2894   2.3064    8.3   2.6756  0.1380
y      115 Thyra       :   8.85   0.9031   1.9201    7.7   2.3798  0.1932
.      116 Sirona      :  10.41   1.3575   2.3745    7.9   2.7659  0.1415
.      118 Peitho      :  10.51   1.0182   2.0352    8.9   2.4363  0.1646
.      119 Althaea     :  10.88   1.3540   2.3710    8.3   2.5808  0.0813
.      124 Alkeste     :  10.79   1.4137   2.4307    8.1   2.6323  0.0766
y      128 Nemesis     :  10.31   1.3799   2.3969    7.7   2.7490  0.1281
.      129 Antigone    :   9.30   1.2393   2.2563    7.1   2.8669  0.2130
.      130 Elektra     :   9.99   1.4553   2.4723    7.2   3.1269  0.2093
.      132 Aethra      :   8.83   0.5782   1.5952    9.0   2.6101  0.3889
.      135 Hertha      :   9.40   0.9090   1.9260    8.2   2.4286  0.2069
.      137 Meliboea    :  10.94   1.4470   2.4640    8.2   3.1256  0.2117
.      138 Tolosa      :  10.43   1.0346   2.0516    8.8   2.4491  0.1623
.      139 Juewa       :  10.38   1.2818   2.2988    8.0   2.7828  0.1739
.      140 Siwa        :  10.38   1.1317   2.1487    8.4   2.7341  0.2141
.      141 Lumen       :  10.25   1.0790   2.0960    8.5   2.6654  0.2136
y      144 Vibilia     :   9.68   1.0124   2.0294    8.1   2.6541  0.2354
y      145 Adeona      :  10.52   1.2634   2.2804    8.2   2.6715  0.1464
y      148 Gallia      :   9.86   1.2326   2.2496    7.7   2.7699  0.1879
.      156 Xanthippe   :  10.53   1.0939   2.1109    8.7   2.7285  0.2264
.      161 Athor       :  10.77   1.0365   2.0535    9.1   2.3798  0.1371
.      163 Erigone     :  10.92   0.8946   1.9116    9.8   2.3664  0.1922
.      164 Eva         :   9.23   0.7004   1.7174    8.8   2.6311  0.3473
.      172 Baucis      :  10.56   1.0897   2.1067    8.8   2.3801  0.1149
y      173 Ino         :   9.92   1.1498   2.1668    7.9   2.7413  0.2096
.      181 Eucharis    :  10.70   1.4613   2.4783    7.9   3.1265  0.2073
.      182 Elsa        :  10.51   0.9468   1.9638    9.2   2.4152  0.1869
.      183 Istria      :  10.40   0.8036   1.8206    9.6   2.7937  0.3483
.      185 Eunike      :  10.27   1.3721   2.3891    7.7   2.7378  0.1274
.      186 Celuta      :  10.54   0.9905   2.0075    9.1   2.3616  0.1499
y      187 Lamberta    :   9.96   1.0548   2.0718    8.3   2.7287  0.2408
y      192 Nausikaa    :   8.15   0.7948   1.8118    7.4   2.4023  0.2458
.      193 Ambrosia    :  10.67   0.8097   1.8267    9.8   2.6002  0.2975
.      194 Prokne      :   9.27   0.9774   1.9944    7.8   2.6164  0.2377
y      196 Philomela   :  10.56   2.0502   3.0672    6.6   3.1150  0.0154
y      198 Ampella     :   9.61   0.8815   1.8985    8.5   2.4581  0.2277
.      200 Dynamene    :  10.97   1.3586   2.3756    8.4   2.7383  0.1325
.      201 Penelope    :  10.45   1.1823   2.1993    8.4   2.6796  0.1792
.      202 Chryseis    :  10.89   1.7342   2.7512    7.5   3.0710  0.1041
.      216 Kleopatra   :   8.82   1.0739   2.0909    7.1   2.7930  0.2514
.      219 Thusnelda   :  10.14   0.8110   1.8280    9.3   2.3537  0.2233
y      230 Athamantis  :   9.55   1.2172   2.2342    7.4   2.3822  0.0621
.      233 Asterope    :  10.97   1.3783   2.3953    8.4   2.6602  0.0996
.      234 Barbara     :   9.84   0.7844   1.8014    9.1   2.3862  0.2451
.      236 Honoria     :  10.54   1.2472   2.2642    8.3   2.7993  0.1912
.      245 Vera        :  10.65   1.4702   2.4872    7.8   3.0980  0.1972
.      247 Eukrate     :   9.93   1.0504   2.0674    8.2   2.7407  0.2457
.      250 Bettina     :  10.81   1.7011   2.7181    7.5   3.1452  0.1358
.      258 Tyche       :  10.06   1.0615   2.0785    8.3   2.6142  0.2049
.      270 Anahita     :   9.83   0.8509   1.8679    8.8   2.1982  0.1503
.      287 Nephthys    :  10.60   1.2825   2.2995    8.2   2.3529  0.0227
.      304 Olga        :  10.94   0.8540   1.8710    9.9   2.4037  0.2216
.      306 Unitas      :  10.30   0.9857   2.0027    8.8   2.3581  0.1507
.      313 Chaldaea    :  10.35   0.9253   1.9423    9.1   2.3746  0.1821
.      322 Phaeo       :  10.90   1.0843   2.1013    9.1   2.7825  0.2448
.      323 Brucia      :   9.82   0.6521   1.6691    9.6   2.3825  0.2994
y      324 Bamberga    :   7.65   0.7483   1.7653    7.0   2.6806  0.3414
.      326 Tamara      :  10.40   0.8607   1.8777    9.4   2.3178  0.1899
.      335 Roberta     :  10.71   1.0305   2.0475    9.1   2.4749  0.1727
.      337 Devosa      :  10.45   1.0416   2.0586    8.8   2.3831  0.1362
.      344 Desiderata  :   9.01   0.7642   1.7812    8.3   2.5966  0.3140
.      345 Tercidina   :  10.95   1.1645   2.1815    8.9   2.3252  0.0618
y      346 Hermentaria :  10.22   1.4904   2.5074    7.4   2.7945  0.1027
y      349 Dembowska   :   9.11   1.6444   2.6614    5.9   2.9263  0.0905
y      354 Eleonora    :   9.17   1.4722   2.4892    6.3   2.8034  0.1121
.      356 Liguria     :  10.19   1.0751   2.0921    8.4   2.7560  0.2409
.      364 Isara       :  10.94   0.8737   1.8907    9.8   2.2210  0.1487
.      372 Palma       :   9.95   1.3404   2.3574    7.5   3.1625  0.2546
.      376 Geometria   :  10.63   0.8758   1.8928    9.5   2.2880  0.1727
.      385 Ilmatar     :  10.44   1.4729   2.4899    7.6   2.8476  0.1256
.      386 Siegena     :  10.33   1.3921   2.4091    7.7   2.8990  0.1690
.      387 Aquitania   :   9.34   1.0795   2.0965    7.6   2.7403  0.2349
.      389 Industria   :  10.53   1.4173   2.4343    7.8   2.6077  0.0665
.      391 Ingeborg    :  10.75   0.5935   1.6105   10.8   2.3199  0.3058
.      393 Lampetia    :   9.39   0.8455   1.8625    8.4   2.7807  0.3302
.      397 Vienna      :  10.83   0.9630   1.9800    9.4   2.6337  0.2482
.      404 Arsinoe     :  10.92   1.0568   2.0738    9.2   2.5932  0.2003
.      405 Thia        :   9.89   0.9384   1.9554    8.6   2.5843  0.2434
.      409 Aspasia     :  10.19   1.3729   2.3899    7.6   2.5751  0.0719
.      410 Chloris     :  10.01   1.0497   2.0667    8.3   2.7244  0.2414
.      413 Edburga     :  10.33   0.6852   1.7022   10.0   2.5854  0.3416
.      415 Palatia     :  10.70   0.9378   1.9548    9.4   2.7926  0.3000
.      416 Vaticana    :   9.74   1.1672   2.1842    7.7   2.7917  0.2176
.      419 Aurelia     :   9.89   0.9276   1.9446    8.6   2.5976  0.2514
.      432 Pythia      :  10.45   1.0054   2.0224    8.9   2.3687  0.1462
y      433 Eros        :   5.91   0.1165   1.1335   10.3   1.4583  0.2227
.      444 Gyptis      :  10.34   1.2703   2.2873    8.0   2.7702  0.1743
.      451 Patientia   :  10.39   1.8303   2.8473    6.8   3.0674  0.0717
.      455 Bruchsalia  :   9.94   0.8545   1.8715    8.9   2.6549  0.2951
y      471 Papagena    :   8.83   1.2123   2.2293    6.7   2.8905  0.2287
.      485 Genua       :  10.45   1.2042   2.2212    8.3   2.7484  0.1918
.      498 Tokio       :  10.57   1.0422   2.0592    8.9   2.6509  0.2232
.      505 Cava        :  10.41   1.0175   2.0345    8.8   2.6877  0.2430
y      511 Davida      :   9.43   1.5496   2.5666    6.4   3.1625  0.1884
.      512 Taurinensis :  10.83   0.6168   1.6338   10.8   2.1899  0.2540
.      516 Amherstia   :   9.57   0.9313   1.9483    8.3   2.6812  0.2734
y      521 Brixia      :   9.91   0.9625   1.9795    8.5   2.7430  0.2783
.      532 Herculina   :   8.18   1.2585   2.2755    5.9   2.7708  0.1788
.      550 Senta       :  10.83   0.9944   2.0114    9.3   2.5883  0.2229
y      554 Peraga      :  10.63   0.9973   2.0143    9.1   2.3751  0.1519
.      563 Suleika     :  10.13   1.0533   2.0703    8.4   2.7113  0.2364
.      582 Olympia     :  10.63   1.0142   2.0312    9.1   2.6103  0.2219
y      584 Semiramis   :   9.39   0.8014   1.8184    8.6   2.3739  0.2340
.      599 Luisa       :  10.16   0.9436   1.9606    8.8   2.7717  0.2926
.      602 Marianna    :  10.90   1.2912   2.3082    8.5   3.0821  0.2511
.      626 Notburga    :  10.54   0.9344   1.9514    9.2   2.5738  0.2418
.      654 Zelinda     :   9.26   0.7506   1.7676    8.7   2.2978  0.2308
y      674 Rachele     :   9.98   1.3343   2.3513    7.5   2.9210  0.1950
.      675 Ludmilla    :  10.19   1.1855   2.2025    8.1   2.7682  0.2043
.      678 Fredegundis :  10.76   0.9893   2.0063    9.3   2.5721  0.2200
.      679 Pax         :   9.91   0.7699   1.7869    9.2   2.5877  0.3095
.      686 Gersuind    :  10.80   0.8770   1.8940    9.7   2.5892  0.2685
.      694 Ekard       :  10.02   0.7908   1.8078    9.2   2.6702  0.3230
.      695 Bella       :  10.98   1.1150   2.1320    9.1   2.5392  0.1604
.      699 Hela        :  10.99   0.5240   1.5410   11.4   2.6126  0.4102
.      704 Interamnia  :   9.41   1.5640   2.5810    6.4   3.0563  0.1555
.      712 Boliviana   :  10.46   1.0820   2.0990    8.7   2.5761  0.1852
.      735 Marghanna   :  10.76   0.8372   1.8542    9.8   2.7305  0.3209
.      737 Arequipa    :  10.34   0.9395   1.9565    9.0   2.5906  0.2448
.      747 Winchester  :   9.26   0.9657   1.9827    7.8   3.0012  0.3394
.      751 Faina       :  10.75   1.1489   2.1659    8.8   2.5513  0.1511
.      753 Tiflis      :  11.00   0.7963   1.8133   10.2   2.3286  0.2213
.      760 Massinga    :  10.56   1.3950   2.4120    7.9   3.1471  0.2336
.      776 Berbericia  :  10.44   1.4267   2.4437    7.7   2.9295  0.1658
.      779 Nina        :   9.65   1.0410   2.0580    8.0   2.6635  0.2273
.      796 Sarita      :   9.90   0.7744   1.7914    9.2   2.6346  0.3201
.      804 Hispania    :  10.63   1.4200   2.4370    7.9   2.8374  0.1411
.      814 Tauris      :  10.89   1.1764   2.1934    8.8   3.1589  0.3056
.      852 Wladilena   :  10.50   0.6969   1.7139   10.1   2.3620  0.2744
.      887 Alinda      :   7.28   0.0453   1.0623   13.9   2.4732  0.5705
.      914 Palisana    :  10.42   0.9143   1.9313    9.2   2.4585  0.2144
.      980 Anacostia   :   9.98   1.1676   2.1846    8.0   2.7396  0.2026
.     1021 Flammario   :  10.45   0.9419   1.9589    9.1   2.7392  0.2849
y     1036 Ganymed     :   6.49   0.2276   1.2446    9.2   2.6658  0.5331
.     1580 Betulia     :  10.15   0.1099   1.1269   14.7   2.1973  0.4872
.     1627 Ivar        :   8.07   0.1070   1.1240   12.7   1.8633  0.3967
.     1917 Cuyo        :   7.79   0.0462   1.0632   14.3   2.1498  0.5055
.     1943 Anteros     :   9.15   0.0471   1.0641   15.7   1.4304  0.2560
.     1980 Tezcatlipoca:   8.16   0.0687   1.0857   13.8   1.7094  0.3648
.     2061 Anza        :   9.09   0.0334   1.0504   16.4   2.2643  0.5361
.     3122 Florence    :   1.50   0.0030   1.0200   14.0   1.7687  0.4233
.     3199 Nefertiti   :  10.31   0.1100   1.1270   14.8   1.5745  0.2842
.     3288 Seleucus    :  10.20   0.0881   1.1051   15.3   2.0326  0.4563
.     3551 Verenia     :  10.61   0.0560   1.0730   16.7   2.0926  0.4872
.     3552 Don Quixote :  10.19   0.2253   1.2423   13.0   4.2633  0.7086
.     3908 Nyx         :   9.60   0.0257   1.0427   17.5   1.9279  0.4591
.     3988 Huma        :  10.98   0.0385   1.0555   17.9   1.5446  0.3166
.     4596 1981 QB     :  10.30   0.0582   1.0752   16.3   2.2394  0.5198
.     4954 Eric        :   7.46   0.0857   1.1027   12.6   2.0014  0.4490
.     5587 1990 SB     :   8.40   0.0753   1.0923   13.8   2.3973  0.5444
.     5836 1993 MF     :  10.47   0.1137   1.1307   14.9   2.4407  0.5367
.     5863 Tara        :  10.53   0.0819   1.0989   15.8   2.2226  0.5056
.     6491 1991 OA     :   8.03   0.0072   1.0242   18.7   2.5012  0.5905
.     7358 Oze         :   9.43   0.0769   1.0939   14.8   2.1983  0.5024
.     7839 1994 ND     :   9.92   0.0255   1.0425   17.8   2.1658  0.5187
.     8567 1996 HW1    :  10.80   0.1094   1.1264   15.3   2.0457  0.4494
.     9400 1994 TW1    :   9.23   0.0688   1.0858   14.9   2.5877  0.5804
"""
