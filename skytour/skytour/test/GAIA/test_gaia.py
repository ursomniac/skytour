import json
import numpy as np
from astroquery.gaia import Gaia

def to_python_type(val):
    """Converts Numpy/Astropy/Masked types to standard Python for JSON."""
    if hasattr(val, 'mask') and val.mask:
        return None
    if isinstance(val, (np.bool_, bool)):
        return bool(val)
    if isinstance(val, (np.floating, float)):
        return float(val)
    if isinstance(val, (np.integer, int)):
        return int(val)
    if isinstance(val, (bytes, bytearray)):
        return val.decode('utf-8')
    return val

def get_gaia_by_hd(hd_name):
    """
    Fetches Gaia DR3 data for an HD identifier.
    Returns JSON where values are nested with their units.
    """
    name = hd_name.upper() if "HD" in hd_name.upper() else f"HD {hd_name}"
    
    try:
        # query_object returns an Astropy Table
        results = Gaia.query_object(coordinate=name, width="20 arcsec", height="20 arcsec")

        if not results or len(results) == 0:
            return json.dumps({"error": f"Object {name} not found"}, indent=4)

        # Get the first row (the best match)
        row = results[0]
        data_dict = {}

        for col in results.colnames:
            raw_val = row[col]
            clean_val = to_python_type(raw_val)
            
            # Check for units in the table metadata
            unit_obj = results[col].unit
            
            if unit_obj and clean_val is not None:
                # Wrap in value/units dictionary
                data_dict[col] = {
                    "value": clean_val,
                    "units": str(unit_obj)
                }
            else:
                # No units or null value, return just the value
                data_dict[col] = clean_val
        
        return json.dumps(data_dict, indent=4)
        
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=4)

if __name__ == "__main__":
    # Test with HD 1835 (9 Ceti)
    print(get_gaia_by_hd("HD 1835"))
