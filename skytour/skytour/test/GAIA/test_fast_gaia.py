import json
import numpy as np
from astroquery.gaia import Gaia

def to_python_type(val):
    """Converts Numpy/Astropy types to standard Python for JSON."""
    if hasattr(val, 'mask') and val.mask:
        return None
    if isinstance(val, (np.bool_, bool)):
        return bool(val)
    if isinstance(val, (np.floating, float)):
        return float(val)
    if isinstance(val, (np.integer, int)):
        return int(val)
    return val

def build_star_dict(row, colnames, table, original_name, release_tag):
    """Structures the dictionary with name, release, and units."""
    star_dict = {"name": original_name, "release_origin": release_tag}
    for col in colnames:
        clean_val = to_python_type(row[col])
        unit_obj = table[col].unit
        
        if unit_obj and clean_val is not None:
            star_dict[col] = {"value": clean_val, "units": str(unit_obj)}
        else:
            star_dict[col] = clean_val
    return star_dict

def bulk_fetch_mixed(input_lines):
    """
    input_lines: List of strings like ["DR2 12345", "DR3 67890"]
    """
    dr2_ids, dr3_ids = [], []
    order = [] # To keep track of the original sequence

    for line in input_lines:
        parts = line.split()
        if len(parts) < 2: continue
        tag, sid = parts[0].upper(), parts[1]
        order.append((tag, sid))
        if tag == "DR2": dr2_ids.append(sid)
        else: dr3_ids.append(sid)

    results_map = {}

    # 1. Fetch DR3 directly
    if dr3_ids:
        q3 = f"SELECT * FROM gaiadr3.gaia_source WHERE source_id IN ({','.join(dr3_ids)})"
        res3 = Gaia.launch_job(q3).get_results()
        for row in res3:
            results_map[("DR3", str(row['source_id']))] = build_star_dict(row, res3.colnames, res3, str(row['source_id']), "DR3")

    # 2. Fetch DR2 counterparts via neighborhood cross-match
    if dr2_ids:
        q2 = f"""
        SELECT x.dr2_source_id, dr3.* FROM gaiadr3.gaia_source AS dr3
        JOIN gaiadr3.dr2_neighbourhood AS x ON dr3.source_id = x.dr3_source_id
        WHERE x.dr2_source_id IN ({','.join(dr2_ids)})
        """
        res2 = Gaia.launch_job(q2).get_results()
        for row in res2:
            # We map it back to the original DR2 ID provided in the list
            results_map[("DR2", str(row['dr2_source_id']))] = build_star_dict(row, res2.colnames, res2, str(row['dr2_source_id']), "DR2")

    # 3. Assemble final list in original order with error reporting
    final_output = []
    for tag, sid in order:
        if (tag, sid) in results_map:
            final_output.append(results_map[(tag, sid)])
        else:
            final_output.append({
                "name": sid, 
                "release_origin": tag, 
                "error": "Data not obtained: ID not found in Gaia Archive or cross-match table"
            })

    return json.dumps(final_output, indent=4)

if __name__ == "__main__":
    # Example mixed list
    my_list = ["DR2 2495333550503023872", "DR3 2495333550503023872"]
    print(bulk_fetch_mixed(my_list))
