import time
from astroquery.simbad import Simbad
from skytour.apps.utils.format import to_sex, tuple_ra, tuple_dec 
def setup_simbad():
    csim = Simbad()
    csim.reset_votable_fields()
    csim.add_votable_fields(
        #'basic',
        'coordinates', 
        'parallax', 
        'propermotions',
        'velocity',
        'sp',
        'U', 'B', 'V', 'R', 'I',
        #'mesVar',
        #'mesRot',
        #'mesDiameter',
        
    )
    return csim
SIMBAD = setup_simbad()

def process_simbad_object(obj, index=0):
    data = obj.columns.items()
    d = {}
    for k, v in data:
        #index = -1 if k[:3] == 'mes' else 0 # I think tables read in reverse
        value = v.tolist()[index] # default to first value
        try:
            units = v.unit.to_string()
        except:
            units = None
        d[k] = (value, units)
    return d

def simbad_make_request(name, csim):
    simobj = csim.query_object(name)
    return simobj
    
def simbad_parse_coords(objdict):
    if 'ra' not in objdict.keys() or 'dec' not in objdict.keys():
        return None, None
    try:
        ra = objdict['ra'][0] / 15.
        dec = objdict['dec'][0]
        return ra, dec
    except:
        return None, None

def normalize_simbad(d):
    v = {}

    # magnitudes
    vmag = v['magnitude'] = d['V'][0]
    bmag = d['B'][0]
    v['B-V'] = None if (vmag is None or bmag is None) else bmag - vmag

    # distance
    parallax = d['plx_value'][0]
    plx_units = d['plx_value'][1]
    plx_error = d['plx_err'][0]
    parsecs = parsecs_error = distance = dist_error = None
    if parallax is not None:
        if plx_units == 'mas':
            parsecs = 1000./parallax
            parsecs_error = 1000. * plx_error / parallax**2
            distance = 3.26 * parsecs
            dist_error = 3.26 * parsecs_error
    v['parallax'] = dict(value = parallax, error = plx_error, units=plx_units)
    v['distance'] = {
        'pc': dict(value = parsecs, error = parsecs_error),
        'ly': dict(value = distance, error = dist_error)
    }
    
    # spectral type
    v['spectral_type'] = d['sp_type'][0]
    # proper motion
    v['proper_motion'] = {
        'ra':  dict(value = d['pmra'][0],  units = d['pmra'][1]),
        'dec': dict(value = d['pmdec'][0], units = d['pmdec'][1]), 
        'error': dict(major = d['pm_err_maj'][0], minor = d['pm_err_min'][0], angle=d['pm_err_angle'][0])
    }
    # radial velocity
    v['radial_velocity'] = dict(
        value = d['rvz_radvel'][0], units = d['rvz_radvel'][1], error = d['rvz_err'][0]
    )
    # v sin i - TODO
    # diameter - TODO
    # variabililty - TODO
    return v

def norm_float(x, prec=2):
    s = f"{x:.{prec}f}"
    return float(s)

def process_simbad_request(name, debug=False):
    req = simbad_make_request(name, SIMBAD)
    if debug:
        print("REQ: ", req)
    if req is None:
        if debug:
            print(f"Cannot find {name} in SIMBAD.")
        return None
    try:
        objdict = process_simbad_object(req)
    except:
        print(f"ERROR - REQ: {req}")
        return None
    if debug:
        print("OBJDICT: ", objdict)
        print("KEYS: ", objdict.keys())

    d = {}
    d['ra_float'], d['dec_float'] = simbad_parse_coords(objdict)
    if debug:
        print("D: ", d)
    if d['ra_float'] is None and d['dec_float'] is None:
        return None
    #d['ra_float'] = convert_ra(d['ra'])
    #d['dec_float'] = convert_dec(d['dec'])
        # coordinates

    d['ra_text'] = to_sex(d['ra_float'], 'ra')
    d['dec_text'] = to_sex(d['dec_float'], 'dec')
    d['ra_tuple'] = tuple_ra(d['ra_float'])
    d['dec_tuple'] = tuple_dec(d['dec_float'])
    d['raw_values'] = objdict
    d['values'] = normalize_simbad(objdict)
    raw_aliases = SIMBAD.query_objectids(name)
    grab = [a[0] for a in raw_aliases.as_array().tolist()]
    d['aliases'] = [' '.join(x.split()) for x in grab]
    return d

def update_star_metadata(model, stars, verbose=True, delay=0.5):
    """
    Stars can be BrightStar or StellarObject instances
    """
    n = 0
    for star in stars:
        time.sleep(delay)
        if not hasattr(star, 'metadata'):
            print(f'Cannot save metadata for {star} - skipping')
            continue
        if model == 'BrightStar':
            name = star.hr_name
        elif model == 'StellarObject':
            name = star.simbad_lookup or star.shown_name
        else:
            continue
        try:
            if verbose:
                print(f"Attempting {star.pk}: {star}")
            metadata = process_simbad_request(name)
            if metadata is None:
                if verbose:
                    print("\t ... failed - found no metadata")
                continue
        except:
            if verbose:
                print(f"\tFailed - exception")
            continue
        # Save metadata
        star.metadata.metadata = metadata
        star.metadata.save()
        n += 1
    return n

# TODO: Need to get metadata for these.   They're proably all close binaries with a single 
#   HR number but separate entries in SIMBAD.
# PROBABLY what I will do is make the metadata object a JSON list of dicts for these
# and a simple dict for everything else (saves having to re-write/re-run anything).
# Extracting metadata will have to test on the object type (list or dict) and then process
# accordingly.    
# RAD 2026-01-10
PROBABLE_BINARIES = [
     251,  394,  997, 1359, 1372, 1405, 1504, 1593, 2482, 3358, 3455, 3715,
    4602, 4917, 4990, 5141, 5210, 5233, 5346, 5497, 5900, 6029, 6063, 6923,
    7059, 7978, 8396, 8687, 8724, 9002
]
def update_problematic_stars(stars):
    for hr in PROBABLE_BINARIES:
        time.sleep(1)
        ml = []
        star = stars.filter(hr_id=hr).first()
        if not hasattr(star, 'metadata'):
            print(f'Cannot save metadata for {star} - skipping')
            continue
        for comp in ['A', 'B']:
            name = f"HD {star.hd_id} {comp}" # Use HD for lookup not HR
            try:
                print(f"Attempting {star.pk}: {star}")
                metadata = process_simbad_request(name)
                if metadata is None:
                    print("\t ... failed - found no metadata")
                    break
            except:
                print(f"\tFailed - exception")
                break
            if metadata:
                ml.append(metadata)
        # save the list
        star.metadata.metadata = ml
        star.metadata.save()

LIST_OF_FIELDS = """
mesDiameter                     	table                   	Collection of stellar diameters.
mesPM                           	table                   	Collection of proper motions.
mesISO                          	table                   	Infrared Space Observatory (ISO) observing log.
mesSpT                          	table                   	Collection of spectral types.
allfluxes                       	table                   	all flux/magnitudes U,B,V,I,J,H,K,u_,g_,r_,i_,z_
ident                           	table                   	Identifiers of an astronomical object
flux                            	table                   	Magnitude/Flux information about an astronomical object
mesOtype                        	table                   	Other object types associated with an object with origins
mesPLX                          	table                   	Collection of trigonometric parallaxes.
otypedef                        	table                   	all names and definitions for the object types
mesDistance                     	table                   	Collection of distances (pc, kpc or Mpc) by several means.
otypes                          	table                   	List of all object types associated with an object
mesVar                          	table                   	Collection of stellar variability types and periods.
mesXmm                          	table                   	XMM observing log.
mesVelocities                   	table                   	Collection of HRV, Vlsr, cz and redshifts.
has_ref                         	table                   	Associations between astronomical objects and their bibliographic references
mesRot                          	table                   	Stellar Rotational Velocities.
biblio                          	table                   	Bibliography
ids                             	table                   	all names concatenated with pipe
mesHerschel                     	table                   	The Herschel observing Log
mesIUE                          	table                   	International Ultraviolet Explorer observing log.
mesFe_h                         	table                   	Collection of metallicity, as well as Teff, logg for stars.
alltypes                        	table                   	all object types concatenated with pipe
basic                           	table                   	General data about an astronomical object
dec                             	column of basic         	Declination
main_id                         	column of basic         	Main identifier for an object
otype_txt                       	column of basic         	Object type
ra                              	column of basic         	Right ascension
coo_bibcode                     	column of basic         	Coordinate reference
coo_err_angle                   	column of basic         	Coordinate error angle
coo_err_maj                     	column of basic         	Coordinate error major axis
coo_err_maj_prec                	column of basic         	Coordinate error major axis precision
coo_err_min                     	column of basic         	Coordinate error minor axis
coo_err_min_prec                	column of basic         	Coordinate error minor axis precision
coo_qual                        	column of basic         	Coordinate quality
coo_wavelength                  	column of basic         	Wavelength class for the origin of the coordinates (R,I,V,U,X,G)
dec_prec                        	column of basic         	Declination precision
galdim_angle                    	column of basic         	Galaxy ellipse angle
galdim_bibcode                  	column of basic         	Galaxy dimension reference
galdim_majaxis                  	column of basic         	Angular size major axis
galdim_majaxis_prec             	column of basic         	Angular size major axis precision
galdim_minaxis                  	column of basic         	Angular size minor axis
galdim_minaxis_prec             	column of basic         	Angular size minor axis precision
galdim_qual                     	column of basic         	Galaxy dimension quality
galdim_wavelength               	column of basic         	Wavelength class for the origin of the Galaxy dimension
hpx                             	column of basic         	Healpix number at ORDER=10
morph_bibcode                   	column of basic         	morphological type reference
morph_qual                      	column of basic         	Morphological type quality
morph_type                      	column of basic         	Morphological type
nbref                           	column of basic         	number of references
oid                             	column of basic         	Object internal identifier
otype                           	column of basic         	Object type
plx_bibcode                     	column of basic         	Parallax reference
plx_err                         	column of basic         	Parallax error
plx_err_prec                    	column of basic         	Parallax error precision
plx_prec                        	column of basic         	Parallax precision
plx_qual                        	column of basic         	Parallax quality
plx_value                       	column of basic         	Parallax
pm_bibcode                      	column of basic         	Proper motion reference
pmdec                           	column of basic         	Proper motion in DEC
pmdec_prec                      	column of basic         	Proper motion in DEC precision
pm_err_angle                    	column of basic         	Proper motion error angle
pm_err_maj                      	column of basic         	Proper motion error major axis
pm_err_maj_prec                 	column of basic         	Proper motion error major axis precision
pm_err_min                      	column of basic         	Proper motion error minor axis
pm_err_min_prec                 	column of basic         	Proper motion error minor axis precision
pm_qual                         	column of basic         	Proper motion quality
pmra                            	column of basic         	Proper motion in RA
pmra_prec                       	column of basic         	Proper motion in RA precision
ra_prec                         	column of basic         	Right ascension precision
rvz_bibcode                     	column of basic         	Radial velocity / redshift reference
rvz_err                         	column of basic         	Radial velocity / redshift error
rvz_err_prec                    	column of basic         	Radial velocity / redshift error precision
rvz_nature                      	column of basic         	velocity / redshift nature
rvz_qual                        	column of basic         	Radial velocity / redshift quality
rvz_radvel                      	column of basic         	Radial Velocity
rvz_radvel_prec                 	column of basic         	Radial velocity precision
rvz_redshift                    	column of basic         	redshift
rvz_redshift_prec               	column of basic         	redshift precision
rvz_type                        	column of basic         	Radial velocity / redshift type
rvz_wavelength                  	column of basic         	Wavelength class for the origin of the radial velocity/reshift
sp_bibcode                      	column of basic         	spectral type reference
sp_qual                         	column of basic         	Spectral type quality
sp_type                         	column of basic         	MK spectral type
update_date                     	column of basic         	Date of last modification
vlsr                            	column of basic         	velocity in Local Standard of Rest reference frame
vlsr_bibcode                    	column of basic         	Reference for the origin of the LSR velocity
vlsr_err                        	column of basic         	Error incertainty of the VLSR velocity
vlsr_max                        	column of basic         	Maximum for the mean value of the LSR velocity
vlsr_min                        	column of basic         	Minimum for the mean value of the LSR velocity
vlsr_wavelength                 	column of basic         	Wavelength class for the origin of the LSR velocity
coordinates                     	bundle of basic columns 	all fields related with coordinates
dim                             	bundle of basic columns 	major and minor axis, angle and inclination
dimensions                      	bundle of basic columns 	all fields related to object dimensions
morphtype                       	bundle of basic columns 	all fields related to the morphological type
parallax                        	bundle of basic columns 	all fields related to parallaxes
propermotions                   	bundle of basic columns 	all fields related with the proper motions
sp                              	bundle of basic columns 	all fields related with the spectral type
velocity                        	bundle of basic columns 	all fields related with radial velocity and redshift
U                               	filter name             	Magnitude U
B                               	filter name             	Magnitude B
V                               	filter name             	Magnitude V
R                               	filter name             	Magnitude R
I                               	filter name             	Magnitude I
J                               	filter name             	Magnitude J
H                               	filter name             	Magnitude H
K                               	filter name             	Magnitude K
u                               	filter name             	Magnitude SDSS u
g                               	filter name             	Magnitude SDSS g
r                               	filter name             	Magnitude SDSS r
i                               	filter name             	Magnitude SDSS i
z                               	filter name             	Magnitude SDSS z
G                               	filter name             	Magnitude Gaia G
F150W                           	filter name             	JWST NIRCam F150W
F200W                           	filter name             	JWST NIRCam F200W
F444W                           	filter name             	JWST NIRCan F444W
"""