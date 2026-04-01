from astropy.coordinates import SkyCoord, Galactic, Galactocentric
import astropy.units as u
#from astroquery.gaia import Gaia

def to_galactocentric_xyz(self, ra, dec, parallax):
        """Converts Gaia observables to Galactocentric XYZ coordinates."""
        # Convert parallax (mas) to distance (pc)
        distance = (1000 / parallax) * u.pc
        
        # Create SkyCoord in ICRS frame
        c = SkyCoord(ra=ra*u.deg, dec=dec*u.deg, distance=distance, frame='icrs')
        
        # Transform to Galactocentric
        # Uses default Astropy solar parameters (~8.122 kpc from center)
        gc = c.transform_to(Galactocentric())


def get_galactic_uvw(ra_deg, dec_deg, dist_pc, pm_ra, pm_dec, rv_kms, dist_units='pc'):
    """
    Computes Heliocentric U, V, W velocities in km/s.
    
    Parameters:
    ra_deg, dec_deg : Right Ascension and Declination (Degrees)
    dist_pc         : Distance (Parsecs)
    pm_ra_cosdec    : Proper motion in RA (mas/yr, includes cos(dec))
    pm_dec          : Proper motion in Dec (mas/yr)
    rv_kms          : Radial Velocity (km/s)

    THIS DOES NOT WORK!    
    """
    if dist_units == 'pc':
        return None
    DIST_CONVERT = {'pc': 1., 'ly': 1./3.26 }
    # 1. Define the star in the ICRS (Equatorial) frame with units
    star = SkyCoord(ra=ra_deg * u.degree,
                    dec=dec_deg * u.degree,
                    distance=dist_pc * u.pc * DIST_CONVERT[dist_units],
                    pm_ra_cosdec=pm_ra_cosdec * u.mas / u.yr,
                    pm_dec=pm_dec * u.mas / u.yr,
                    radial_velocity=rv_kms * u.km / u.s,
                    frame='icrs')

    # 2. Transform to the Galactic frame
    # Astropy uses a right-handed system: U is toward the Galactic Center
    gal = star.transform_to(Galactic())

    # 3. Extract Cartesian velocity components (U, V, W)
    # In the Galactic frame, U=v_x, V=v_y, W=v_z
    u_vel = gal.velocity.d_x.value
    v_vel = gal.velocity.d_y.value
    w_vel = gal.velocity.d_z.value

    return u_vel, v_vel, w_vel

# Example usage (Proxima Centauri approx):
def test_uvw():
    u_val, v_val, w_val = get_galactic_uvw(217.42, -62.67, 1.3, -3781, 769, -22.2)
    print(f"U: {u_val:.2f} km/s, V: {v_val:.2f} km/s, W: {w_val:.2f} km/s")
